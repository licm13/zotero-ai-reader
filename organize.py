import time
import json
import math
import os
from pyzotero import zotero
from google import genai
import config  # 复用您的配置文件

# ================= 1. 配置区域 =================

# --- 关键设置 ---
# 如果不为 None，脚本只会在这个集合里找文献进行分类
# 示例: TARGET_COLLECTION_PATH = "00_Inbox" 或 "2025/Pending"
TARGET_COLLECTION_PATH = getattr(config, 'TARGET_COLLECTION_PATH', None) 
# 您也可以在这里强制指定，覆盖 config.py
# TARGET_COLLECTION_PATH = "2025_New_Papers"

DRY_RUN = True          # True=仅测试，False=真移动
BATCH_SIZE = 5          # 批处理大小
AUTO_TAG_NAME = "auto_organized" # 防止重复处理的标签

# --- 学术画像 (保持不变) ---
USER_PROFILE_CONTEXT = """
The user is a Professor in Hydrology (Chengming Li, SCUT/Tsinghua), specializing in:
1. Evapotranspiration (ET), Transpiration, and Global Water Cycle.
2. Hydrological Extremes: Specifically "Flash Drought", "Flood", and "Drought-Flood Abrupt Alternation" (旱涝急转).
3. Data Methods: Triple Collocation, Data Fusion, Uncertainty Analysis, and Deep Learning in Hydrology.

PREFERRED CATEGORY STRUCTURE (Hierarchy):
- Hydrological Extremes
  - Drought & Flash Drought
  - Flood & Inundation
  - Drought-Flood Transitions (For 'Abrupt Alternation' papers)
- Water Cycle Processes
  - Evapotranspiration & GPP (Focus on ET products, physiology)
  - Runoff & Streamflow
  - Snow & Glaciers (Cryosphere)
  - Soil Moisture
- Methodology
  - Data Fusion & Uncertainty (For Triple Collocation, Merging)
  - Remote Sensing Retrieval (For algorithm development)
  - AI & Deep Learning (For LSTM, CNN applications)
- Climate Change & Attribution
"""

# ================= 2. 核心功能函数 =================

def find_collection_by_path(zot, collection_path):
    """(复用自 reader.py) 根据路径查找集合 Key"""
    if not collection_path: return None
    path_parts = [p.strip() for p in collection_path.split('/') if p.strip()]
    if not path_parts: return None
    
    # 获取所有集合建立映射 (为了效率，只做简单名称匹配，严谨版需递归)
    try:
        all_colls = zot.collections()
    except Exception as e:
        print(f"❌ 获取集合列表失败: {e}")
        return None
        
    # 简单查找逻辑：找到匹配路径末尾名称的集合
    # 注意：如果有同名集合，这里可能会混淆，建议使用独特名称
    target_name = path_parts[-1]
    for c in all_colls:
        if c['data']['name'] == target_name:
            # 可以在这里增加对父集合的校验逻辑
            return c['key']
    
    print(f"⚠️ 未找到集合: {collection_path}")
    return None

def get_all_collections_map(zot):
    """获取现有集合映射 {name: key} 用于AI参考"""
    # 仅获取顶层和二级，避免Token过多
    raw_colls = zot.collections()
    return {c['data']['name']: c['key'] for c in raw_colls}

def extract_tags_from_note(note_content):
    import re
    text = re.sub(r'<[^>]+>', '', note_content)
    match = re.search(r'(?:Keywords[–-]Tags|论文分类)[：:]\s*(.+)', text, re.IGNORECASE)
    if match: return match.group(1).strip()
    return ""

def ai_classify_batch(batch_items, existing_colls):
    client = genai.Client(api_key=config.AI_API_KEY)
    papers_desc = [f"ID {i}: Title='{item['title']}', Keywords='{item['tags']}'" for i, item in enumerate(batch_items)]
    papers_text = "\n".join(papers_desc)
    existing_list = ", ".join(list(existing_colls.keys())[:50])

    prompt = f"""
    {USER_PROFILE_CONTEXT}
    
    TASK: Classify these papers into collections.
    EXISTING COLLECTIONS: [{existing_list}]
    
    INSTRUCTIONS:
    1. Match papers to the "Preferred Category Structure" if possible.
    2. Return JSON with IDs as keys and "collection_path" as values.
    
    INPUT:
    {papers_text}
    
    OUTPUT JSON format: {{"0": "Path/To/Collection"}}
    """
    
    try:
        response = client.models.generate_content(
            model=config.AI_MODEL,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"   ❌ Batch AI Error: {e}")
        return {}

def ensure_and_move(zot, item, path, cached_colls):
    """创建路径并移动"""
    if not path or path == "Unclassified": return
    parts = [p.strip() for p in path.split('/') if p.strip()]
    parent_key = None
    
    # 逐级创建目录
    for part in parts:
        found_key = cached_colls.get(part) # 简单查找
        
        if not found_key:
            if not DRY_RUN:
                print(f"      🔨 创建新集合: {part}")
                try:
                    payload = {'name': part}
                    if parent_key: payload['parentCollection'] = parent_key
                    res = zot.create_collections([payload])
                    if res and 'successful' in res:
                        found_key = list(res['successful'].values())[0]['key']
                        cached_colls[part] = found_key
                except Exception as e:
                    print(f"      ❌ 创建失败: {e}")
                    return
            else:
                print(f"      [Dry Run] 拟创建集合: {part}")
                found_key = "fake_" + part
        
        parent_key = found_key

    # 移动文献
    if parent_key and not parent_key.startswith("fake_"):
        if not DRY_RUN:
            # 检查是否已在集合中
            if parent_key not in item['data'].get('collections', []):
                try:
                    zot.add_to_collection(parent_key, item)
                    zot.add_tags(item, AUTO_TAG_NAME) # 打标
                    print(f"      ✅ 已移入: {path}")
                except Exception as e:
                    print(f"      ❌ 移动失败: {e}")
            else:
                print(f"      ℹ️  已在目标集合中")
        else:
            print(f"      [Dry Run] 拟移入: {path}")

# ================= 3. 主流程 =================

def main():
    print(f"🚀 启动智能归档 (Dry Run: {DRY_RUN})")
    zot = zotero.Zotero(config.LIBRARY_ID, config.LIBRARY_TYPE, config.API_KEY)
    colls_cache = get_all_collections_map(zot)

    # --- 关键修改：支持指定集合 ---
    target_coll_key = None
    if TARGET_COLLECTION_PATH:
        print(f"📂 指定目标集合路径: {TARGET_COLLECTION_PATH}")
        target_coll_key = find_collection_by_path(zot, TARGET_COLLECTION_PATH)
        if not target_coll_key:
            print("❌ 未找到指定集合，请检查路径。退出。")
            return
        print(f"✅ 锁定集合Key: {target_coll_key}")

    # 获取待处理文献
    print("🔍 正在获取文献列表...")
    if target_coll_key:
        # 仅获取特定集合下的文献 (API过滤)
        # 注意：collection_items 默认不深层递归，如需递归需加参数，这里暂只处理该层级
        items = zot.collection_items(target_coll_key, tag='gemini_read', limit=50)
        print(f"   - 范围: 集合 '{TARGET_COLLECTION_PATH}'")
    else:
        # 全库搜索
        items = zot.items(tag='gemini_read', limit=50)
        print(f"   - 范围: 整个文献库")

    # 本地过滤已处理的
    todo_items = []
    for it in items:
        tags = [t['tag'] for t in it['data'].get('tags', [])]
        if AUTO_TAG_NAME not in tags:
            # 提取笔记
            children = zot.children(it['key'])
            note_tags = ""
            for child in children:
                if child['data']['itemType'] == 'note':
                    extracted = extract_tags_from_note(child['data']['note'])
                    if extracted: 
                        note_tags = extracted
                        break
            
            if note_tags:
                todo_items.append({
                    'key': it['key'],
                    'data': it['data'],
                    'title': it['data'].get('title', 'No Title'),
                    'tags': note_tags
                })
    
    print(f"✅ 待处理文献数: {len(todo_items)}")
    if not todo_items: return

    # 批处理循环
    total_batches = math.ceil(len(todo_items) / BATCH_SIZE)
    for i in range(total_batches):
        batch = todo_items[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
        print(f"\n📦 Batch {i+1}/{total_batches} ({len(batch)} items)...")
        
        results = ai_classify_batch(batch, colls_cache)
        
        for idx_str, path in results.items():
            try:
                idx = int(idx_str)
                if idx < len(batch):
                    ensure_and_move(zot, batch[idx]['data'], path, colls_cache)
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
        
        time.sleep(2)

    print("\n🎉 完成")

if __name__ == "__main__":
    main()