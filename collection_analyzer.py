import os
import sys
import time
import json
import re
from pyzotero import zotero
from google import genai
import markdown

# ================= 1. 配置加载 =================
from config_loader import get_config_from_args_or_interactive

config = get_config_from_args_or_interactive()
if config is None:
    print("❌ 无法加载配置文件，程序退出")
    sys.exit(1)

# 从config模块读取配置
LIBRARY_ID = config.LIBRARY_ID
API_KEY = config.API_KEY
LIBRARY_TYPE = config.LIBRARY_TYPE
AI_API_KEY = config.AI_API_KEY
AI_MODEL = getattr(config, 'AI_MODEL', 'gemini-2.0-flash-lite')
CACHE_FILE = "collections_cache.json"

def load_cache():
    """从磁盘加载集合 ID 缓存"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载缓存失败: {e}")
    return {}

def save_cache(cache):
    """将集合 ID 缓存保存到磁盘"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ 保存缓存失败: {e}")

def refresh_cache_from_zotero(zot):
    """从 Zotero 获取所有集合并构建缓存"""
    print("🔄 正在从 Zotero 刷新集合缓存 (可能需要较长时间)...")
    all_colls = []
    start = 0
    page_size = 100
    
    while True:
        try:
            print(f"   📥 正在获取第 {start//page_size + 1} 页集合...")
            page = zot.collections(limit=page_size, start=start)
            if not page:
                break
            all_colls.extend(page)
            if len(page) < page_size:
                break
            start += page_size
        except Exception as e:
            print(f"   ❌ 获取集合分页失败: {e}")
            break
            
    cache = {}
    key_to_coll = {c['key']: c for c in all_colls}

    def build_full_path(coll):
        path = [coll['data']['name']]
        parent = coll['data'].get('parentCollection', None)
        while parent:
            parent_coll = key_to_coll.get(parent)
            if not parent_coll:
                break
            path.insert(0, parent_coll['data']['name'])
            parent = parent_coll['data'].get('parentCollection', None)
        return '/'.join(path)

    for c in all_colls:
        full_path = build_full_path(c)
        cache[full_path] = {
            'key': c['key'],
            'name': c['data']['name'],
            'parent': c['data'].get('parentCollection', None)
        }
    
    save_cache(cache)
    print(f"✅ 缓存已更新，包含 {len(cache)} 个集合路径")
    return cache

def find_collection(zot, collection_query, cache):
    """
    查找集合 Key：
    1. 尝试完全匹配全路径 (Parent/Child)
    2. 尝试完全匹配集合名称 (Name)
    3. 尝试模糊匹配集合名称
    """
    # 1. 尝试完全匹配全路径
    if collection_query in cache:
        print(f"✅ 找到路径完全匹配: {collection_query}")
        return cache[collection_query]['key']
        
    # 2. 尝试匹配集合名称
    for path, info in cache.items():
        name = path.split('/')[-1]
        if name.lower() == collection_query.lower():
            print(f"✅ 找到名称完全匹配: {path} (Key: {info['key']})")
            return info['key']
            
    # 3. 尝试模糊匹配集合名称
    matches = []
    for path, info in cache.items():
        name = path.split('/')[-1]
        if collection_query.lower() in name.lower():
            matches.append((path, info))
            
    if len(matches) == 1:
        path, info = matches[0]
        print(f"✅ 找到唯一模糊匹配: {path} (Key: {info['key']})")
        return info['key']
    elif len(matches) > 1:
        print(f"⚠️ 找到多个匹配项，请指定更精确的名称或路径：")
        for i, (path, info) in enumerate(matches[:10], 1):
            print(f"   {i}. {path}")
        if len(matches) > 10:
            print(f"   ...以及其他 {len(matches)-10} 个匹配项")
        return None
        
    return None

def get_collection_items_with_notes(zot, collection_key):
    """获取集合中文献及笔记"""
    print(f"📥 正在获取文献列表 (Key: {collection_key})...")
    items = zot.collection_items(collection_key)
    results = []
    
    parent_items = [i for i in items if i['data'].get('itemType') not in ['attachment', 'note']]
    print(f"✅ 找到 {len(parent_items)} 篇文献")
    
    for idx, item in enumerate(parent_items, 1):
        title = item['data'].get('title', '无标题')
        item_key = item['key']
        print(f"   [{idx}/{len(parent_items)}] 提取: {title[:50]}...")
        
        children = zot.children(item_key)
        notes = []
        for child in children:
            if child['data'].get('itemType') == 'note':
                content = re.sub(r'<[^>]+>', '', child['data'].get('note', '')).strip()
                if content:
                    notes.append(content)
        
        results.append({
            'title': title,
            'authors': item['meta'].get('creatorSummary', '未知作者'),
            'date': item['data'].get('date', '未知年份'),
            'abstract': item['data'].get('abstractNote', ''),
            'notes': notes
        })
    return results

def call_gemini_analysis(query_name, data):
    """AI 分析建议"""
    client = genai.Client(api_key=AI_API_KEY)
    
    context = [f"# Collection: {query_name}\nTotal Papers: {len(data)}\n"]
    for i, p in enumerate(data, 1):
        context.append(f"## {i}. {p['title']}")
        context.append(f"Authors: {p['authors']} | Date: {p['date']}")
        if p['abstract']:
            context.append(f"Abstract: {p['abstract'][:400]}...")
        if p['notes']:
            context.append("Notes Found:")
            for n in p['notes']:
                context.append(f"- {n[:1000]}")
        context.append("-" * 15)
        
    full_text = "\n".join(context)
    
    sys_prompt = f"""你是一位科学研究专家。请分析以下 Zotero 集合 "{query_name}" 的研究内容。
基于提供的文献摘要和笔记，总结出：
1. 研究核心领域与主要科学问题。
2. 已有的研究共识与主要进展。
3. 关键的数据源与核心方法论。
4. **尚未解决的矛盾或空白点**。
5. **对未来研究的 3 个具体创新切入点建议**。

输出请使用 Markdown 格式，语言专业。"""

    print(f"🧠 正在调用 Gemini 分析 (模型: {AI_MODEL})...")
    try:
        resp = client.models.generate_content(
            model=AI_MODEL,
            contents=f"{sys_prompt}\n\n文献及笔记数据：\n\n{full_text}"
        )
        return resp.text
    except Exception as e:
        print(f"❌ AI 分析出错: {e}")
        return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Zotero Collection Analyzer')
    parser.add_argument('--config', type=str, help='Config path')
    parser.add_argument('--refresh', action='store_true', help='Force refresh collection cache')
    parser.add_argument('collection', help='Collection name or path')
    args, unknown = parser.parse_known_args()
    
    zot = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY)
    
    # 加载或刷新缓存
    cache = {} if args.refresh else load_cache()
    if not cache:
        cache = refresh_cache_from_zotero(zot)
        
    # 查找集合
    col_key = find_collection(zot, args.collection, cache)
    
    # 如果没找到，尝试刷新缓存后再找一次
    if not col_key and not args.refresh:
        print("🔍 在缓存中未找到，正在刷新缓存尝试...")
        cache = refresh_cache_from_zotero(zot)
        col_key = find_collection(zot, args.collection, cache)
        
    if not col_key:
        print(f"❌ 无法定位集合: {args.collection}")
        return
        
    # 获取数据并分析
    data = get_collection_items_with_notes(zot, col_key)
    if not data:
        print("⚠️ 集合为空或未找到文献")
        return
        
    report = call_gemini_analysis(args.collection, data)
    if report:
        safe_name = re.sub(r'[^\w\s-]', '_', args.collection).strip().replace(' ', '_')
        fname = f"{safe_name}_analysis.md"
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ 报告已保存: {fname}")
        print("\n--- 报告摘要 ---")
        print(report[:400] + "...")

if __name__ == "__main__":
    main()
