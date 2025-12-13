import time
import json
import math
import os
from pyzotero import zotero
from google import genai
import config

# ================= 配置 =================
# 如果不为 None，只处理该集合内的文献
TARGET_COLLECTION_PATH = getattr(config, 'TARGET_COLLECTION_PATH', None)
DRY_RUN = True              # ⚠️ 先开启测试模式，确认无误后改为 False
BATCH_SIZE = 5              # 批处理大小
AUTO_TAG_NAME = "auto_organized"
PROFILE_FILE = 'user_profile.json'
CACHE_FILE = 'collections_cache.json'

# ================= 双轨分类体系 (默认为您的画像定制) =================
DEFAULT_TAXONOMY = {
    "Track_A_Archive": {
        "description": "Standard disciplinary classification for retrieval.",
        "structure": [
            "📚 Archive/Processes/Evapotranspiration",
            "📚 Archive/Processes/Runoff & Streamflow",
            "📚 Archive/Processes/Cryosphere (Snow_Glacier)",
            "📚 Archive/Hazards/Drought (Flash_Drought)",
            "📚 Archive/Hazards/Flood",
            "📚 Archive/Hazards/Compound_Events",
            "📚 Archive/Methodology/Remote_Sensing (Retrieval)",
            "📚 Archive/Methodology/Deep_Learning",
            "📚 Archive/Methodology/Data_Fusion"
        ]
    },
    "Track_B_Idea_Lab": {
        "description": "Taste-driven classification based on scientific questions and physical structures.",
        "structure": [
            "💡 Idea Lab/Mechanism/Abrupt_Transitions (Phase_Change)",
            "💡 Idea Lab/Mechanism/Land_Atmosphere_Coupling",
            "💡 Idea Lab/Data_Philosophy/Signal_Purification (Uncertainty)",
            "💡 Idea Lab/Data_Philosophy/Scale_Issues",
            "💡 Idea Lab/Modeling/Physics_AI_Fusion",
            "💡 Idea Lab/Modeling/Causal_Inference"
        ]
    }
}

# ================= 功能函数 =================

def load_profile():
    """加载 profiler.py 生成的动态画像"""
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"base_info": "Use default hydrology profile."}

def load_collection_cache(zot):
    """加载集合缓存，如果没有则从 Zotero 获取"""
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            print(f"📦 已加载本地集合缓存 ({len(cache)} 个)")
            return cache
        except:
            print("⚠️ 缓存文件损坏，重新获取...")
    
    print("🌐 正在从 Zotero 获取集合列表 (这可能需要一点时间)...")
    try:
        # 获取所有集合 (简单映射 name -> key)
        # 注意：如果有同名集合，这里会覆盖。建议保持集合名称唯一。
        colls = zot.collections()
        for c in colls:
            cache[c['data']['name']] = c['key']
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
        return cache
    except Exception as e:
        print(f"❌ 获取集合失败: {e}")
        return {}

def update_cache(name, key):
    """更新缓存"""
    try:
        cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        cache[name] = key
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except:
        pass

def find_collection_by_path_simple(zot, path_str):
    """(辅助) 用于查找 TARGET_COLLECTION_PATH"""
    if not path_str: return None
    name = path_str.split('/')[-1].strip()
    colls = zot.collections(q=name) # 搜索
    for c in colls:
        if c['data']['name'] == name:
            return c['key']
    return None

def extract_tags_from_note(zot, item_key):
    """从笔记中提取 Keywords"""
    children = zot.children(item_key)
    for child in children:
        if child['data']['itemType'] == 'note':
            note = child['data']['note']
            import re
            clean = re.sub(r'<[^>]+>', '', note)
            match = re.search(r'(?:Keywords[–-]Tags|论文分类)[：:]\s*(.+)', clean, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    return ""

def ai_dual_classify(batch_items, user_profile):
    """调用 AI 进行双轨分类"""
    client = genai.Client(api_key=config.AI_API_KEY)
    
    papers_desc = []
    for i, item in enumerate(batch_items):
        papers_desc.append(f"Paper ID {i}: Title='{item['title']}', Keywords='{item['keywords']}'")
    papers_text = "\n".join(papers_desc)
    
    # 动态构建分类树描述
    profile_summary = user_profile.get('dynamic_analysis', {}).get('summary', '')
    
    prompt = f"""
    ROLE: You are an expert Research Assistant for Prof. Chengming Li (Hydrology/AI).
    
    USER PROFILE:
    {user_profile.get('base_info', '')}
    {profile_summary}
    
    TASK: Classify the following papers into TWO distinct tracks:
    1. **Track A (Archive)**: The standard disciplinary folder (Subject/Method).
    2. **Track B (Idea Lab)**: The scientific question or "taste-based" folder (Mechanism/Philosophy).
    
    AVAILABLE TAXONOMY (You strictly adhere to these paths, or suggest logical sub-paths):
    {json.dumps(DEFAULT_TAXONOMY, indent=2)}
    
    INPUT PAPERS:
    {papers_text}
    
    OUTPUT JSON FORMAT (Strictly JSON):
    {{
        "0": {{
            "archive_path": "📚 Archive/...", 
            "idea_path": "💡 Idea Lab/..."
        }},
        "1": ...
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=config.AI_MODEL,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return {}

def ensure_path_and_get_key(zot, path, cache):
    """确保路径存在并返回最后一级的 Key"""
    if not path or "Unclassified" in path: return None
    
    parts = [p.strip() for p in path.split('/') if p.strip()]
    parent_key = None
    
    for part in parts:
        # 检查缓存
        current_key = cache.get(part)
        
        # 如果缓存没有，尝试创建 (注意：这里简化了逻辑，假设名字唯一)
        if not current_key:
            if not DRY_RUN:
                print(f"      🔨 创建新集合: {part}")
                try:
                    payload = {'name': part}
                    if parent_key: payload['parentCollection'] = parent_key
                    res = zot.create_collections([payload])
                    if res and 'successful' in res:
                        current_key = list(res['successful'].values())[0]['key']
                        update_cache(part, current_key)
                        cache[part] = current_key # 更新内存缓存
                except Exception as e:
                    print(f"      ❌ 创建失败: {e}")
                    return None
            else:
                print(f"      [Dry Run] 拟创建集合: {part}")
                current_key = "fake_" + part
        
        parent_key = current_key
        
    return parent_key

# ================= 主程序 =================

def main():
    print(f"🚀 启动双轨分类引擎 (Dry Run: {DRY_RUN})...")
    
    # 初始化
    zot = zotero.Zotero(config.LIBRARY_ID, config.LIBRARY_TYPE, config.API_KEY)
    profile = load_profile()
    colls_cache = load_collection_cache(zot)
    
    # 确定处理范围
    target_key = None
    if TARGET_COLLECTION_PATH:
        print(f"🎯 目标集合: {TARGET_COLLECTION_PATH}")
        target_key = find_collection_by_path_simple(zot, TARGET_COLLECTION_PATH)
        if not target_key:
            print("❌ 无法找到目标集合，请检查 config.py 或路径名称。")
            return
    
    # 获取待处理文献
    print("🔍 搜索待处理文献 (tag: gemini_read)...")
    if target_key:
        items = zot.collection_items(target_key, tag='gemini_read', limit=50)
    else:
        items = zot.items(tag='gemini_read', limit=50)
        
    # 预处理：过滤已处理的，提取 Keywords
    todo_list = []
    for item in items:
        tags = [t['tag'] for t in item['data'].get('tags', [])]
        if AUTO_TAG_NAME in tags: continue
        
        kw = extract_tags_from_note(zot, item['key'])
        if kw:
            todo_list.append({
                'key': item['key'],
                'data': item['data'],
                'title': item['data'].get('title', 'Untitled'),
                'keywords': kw
            })
            
    print(f"✅ 找到 {len(todo_list)} 篇待分类文献")
    if not todo_list: return

    # 批处理
    batches = math.ceil(len(todo_list) / BATCH_SIZE)
    for i in range(batches):
        batch = todo_list[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
        print(f"\n📦 处理批次 {i+1}/{batches}...")
        
        # AI 决策
        decisions = ai_dual_classify(batch, profile)
        
        # 执行移动
        for idx_str, paths in decisions.items():
            try:
                idx = int(idx_str)
                if idx >= len(batch): continue
                
                paper = batch[idx]
                print(f"   📄 {paper['title'][:30]}...")
                
                # 获取路径
                p_archive = paths.get('archive_path')
                p_idea = paths.get('idea_path')
                
                keys_to_add = []
                
                # 处理 Archive 路径
                k1 = ensure_path_and_get_key(zot, p_archive, colls_cache)
                if k1 and not k1.startswith("fake"): keys_to_add.append(k1)
                
                # 处理 Idea Lab 路径
                k2 = ensure_path_and_get_key(zot, p_idea, colls_cache)
                if k2 and not k2.startswith("fake"): keys_to_add.append(k2)
                
                # 执行 Zotero 操作
                if not DRY_RUN:
                    for k in keys_to_add:
                        # 检查是否已存在
                        current_colls = paper['data'].get('collections', [])
                        if k not in current_colls:
                            zot.add_to_collection(k, paper['data'])
                            print(f"      ✅ 添加到: {colls_cache.get(k, k) if k in colls_cache else 'New Collection'}")
                    
                    # 打标签
                    zot.add_tags(paper['data'], AUTO_TAG_NAME)
                else:
                    print(f"      [Dry Run] 计划归入: \n        1. {p_archive}\n        2. {p_idea}")
                    
            except Exception as e:
                print(f"   ⚠️ 单条处理失败: {e}")
        
        time.sleep(2)

    print("\n🎉 完成所有分类任务！")

if __name__ == "__main__":
    main()