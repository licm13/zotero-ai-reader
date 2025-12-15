#!/usr/bin/env python3
"""
测试脚本：检查特定文献是否存在并查看其笔记
"""

import os
from pyzotero import zotero

try:
    import config
    LIBRARY_ID = config.LIBRARY_ID
    API_KEY = config.API_KEY
    LIBRARY_TYPE = config.LIBRARY_TYPE
    print("✅ 已从 config.py 加载配置")
except ImportError:
    print("⚠️  未找到 config.py 文件！")
    exit(1)

# 目标文献标题
TARGET_TITLE = "A global urban tree leaf area index dataset for urban climate modeling"

print("=" * 70)
print("🔍 检查特定文献")
print("=" * 70)
print(f"目标标题: {TARGET_TITLE}")
print()

# 初始化Zotero连接
try:
    zot = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY)
    print(f"✅ 已连接到Zotero库 (ID: {LIBRARY_ID})")
except Exception as e:
    print(f"❌ 连接Zotero失败: {e}")
    exit(1)

# 搜索文献
print(f"\n📚 正在搜索文献...")
try:
    # 使用标题搜索
    items = zot.items(q=TARGET_TITLE, limit=10)
    print(f"   找到 {len(items)} 个匹配项")
    
    found = False
    for i, item in enumerate(items):
        title = item['data'].get('title', '')
        item_type = item['data'].get('itemType', '')
        key = item['key']
        
        print(f"\n   [{i+1}] 标题: {title}")
        print(f"       类型: {item_type}")
        print(f"       Key: {key}")
        
        # 检查是否是目标文献（完全匹配或包含关键词）
        if TARGET_TITLE.lower() in title.lower() or title.lower() in TARGET_TITLE.lower():
            found = True
            print(f"       ✅ 匹配到目标文献！")
            
            # 获取笔记
            print(f"\n   🔍 正在查找笔记...")
            try:
                children = zot.children(key)
                print(f"      找到 {len(children)} 个子项")
                
                notes_found = 0
                for child in children:
                    child_type = child['data'].get('itemType', '')
                    if child_type == 'note':
                        notes_found += 1
                        note_title = child['data'].get('title', '')
                        note_content = child['data'].get('note', '')
                        
                        print(f"\n       📝 笔记 {notes_found}:")
                        print(f"           标题: {note_title}")
                        note_preview = note_content[:200].replace('\n', ' ')
                        print(f"           内容预览: {note_preview}...")
                        
                        # 检查是否包含"关键词"或"Keywords"
                        if "关键词" in note_content or "Keywords" in note_content or "keywords" in note_content.lower():
                            print(f"           ✅ 包含关键词部分")
                            # 尝试提取关键词
                            import re
                            patterns = [
                                r'(?:Keywords|关键词|论文关键词|关键词：|Keywords:)[：:\s]*\n?\s*(.+?)(?:\n\n|\n(?:Summary|总结|Abstract|摘要)|$)',
                                r'(?:Keywords|关键词)[：:\s]+(.+?)(?:\n\n|\n(?:Summary|总结)|$)',
                            ]
                            for pattern in patterns:
                                match = re.search(pattern, note_content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                                if match:
                                    keywords_text = match.group(1).strip()
                                    print(f"           关键词内容: {keywords_text[:200]}...")
                                    break
                        else:
                            print(f"           ⚠️  未找到关键词部分")
                
                if notes_found == 0:
                    print(f"       ⚠️  该文献没有笔记")
                    
            except Exception as e:
                error_str = str(e)
                if "can only be called on" in error_str:
                    print(f"       ⚠️  该项目类型不支持children调用: {item_type}")
                else:
                    print(f"       ❌ 获取笔记失败: {e}")
            
            break
    
    if not found:
        print(f"\n   ⚠️  未找到完全匹配的文献")
        print(f"   尝试使用部分标题搜索...")
        
        # 尝试使用部分标题搜索
        search_terms = ["urban tree", "leaf area index", "urban climate"]
        for term in search_terms:
            items = zot.items(q=term, limit=20)
            print(f"\n   搜索词: '{term}' - 找到 {len(items)} 个结果")
            for item in items[:5]:  # 只显示前5个
                title = item['data'].get('title', '')
                if "leaf area" in title.lower() and "urban" in title.lower():
                    print(f"      - {title[:80]}...")
        
except Exception as e:
    print(f"   ❌ 搜索失败: {e}")

print("\n" + "=" * 70)
print("✅ 检查完成")
print("=" * 70)

