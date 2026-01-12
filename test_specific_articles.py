#!/usr/bin/env python3
"""
测试脚本：检查特定文章的笔记读取
"""

import sys
import os
from pyzotero import zotero

# 配置路径
CONFIG_PATH = r'C:\Users\ASUS\OneDrive\SCI\Github\zotero_ai_read_config.py'

# 目标论文标题
TARGET_TITLES = [
    "Time shift between precipitation and evaporation has more impact on annual streamflow variability than the elasticity of potential evaporation",
    "Future intensification of compound heatwaves and socioeconomic exposure in africa"
]

def load_config(config_path):
    """加载配置文件"""
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return None
    
    config_dir = os.path.dirname(os.path.abspath(config_path))
    if config_dir not in sys.path:
        sys.path.insert(0, config_dir)
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_path)
        if not spec or not spec.loader:
            print(f"❌ 无法创建模块规范: {config_path}")
            return None
        
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        required_attrs = ['LIBRARY_ID', 'API_KEY', 'LIBRARY_TYPE']
        missing_attrs = [attr for attr in required_attrs if not hasattr(config, attr)]
        
        if missing_attrs:
            print(f"❌ 配置文件缺少必需的属性: {', '.join(missing_attrs)}")
            return None
        
        print(f"✅ 已从 {config_path} 加载配置")
        return config
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def find_items_by_titles(zot, titles):
    """根据标题列表查找论文"""
    print(f"\n🔍 搜索 {len(titles)} 篇论文...")
    
    all_items = []
    
    # 获取所有items
    print("\n方法1: 获取所有items并过滤...")
    try:
        items = zot.items()
        print(f"   找到 {len(items)} 个items")
        
        for item in items:
            item_title = item.get('data', {}).get('title', '')
            for target_title in titles:
                if target_title.lower() in item_title.lower() or item_title.lower() in target_title.lower():
                    all_items.append((item, target_title))
                    print(f"   ✅ 匹配: {item_title[:80]}...")
                    break
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    return all_items

def check_item_notes_detailed(zot, item, expected_title):
    """详细检查item的笔记"""
    item_key = item.get('key', '')
    item_title = item.get('data', {}).get('title', 'Unknown')
    item_type = item.get('data', {}).get('itemType', 'unknown')
    
    print(f"\n{'='*80}")
    print(f"📄 论文信息:")
    print(f"   标题: {item_title}")
    print(f"   类型: {item_type}")
    print(f"   Key: {item_key}")
    print(f"   期望标题: {expected_title}")
    
    # 检查item结构
    print(f"\n📋 Item结构分析:")
    print(f"   Item类型: {type(item)}")
    print(f"   Item keys: {list(item.keys()) if isinstance(item, dict) else 'Not a dict'}")
    if isinstance(item, dict) and 'data' in item:
        item_data = item['data']
        print(f"   Item data类型: {type(item_data)}")
        print(f"   Item data keys (前10个): {list(item_data.keys())[:10] if isinstance(item_data, dict) else 'Not a dict'}")
    
    # 方法1: 使用children()方法（与organizer.py相同的方式）
    print(f"\n方法1: 使用 zot.children('{item_key}')")
    children = []
    try:
        children = zot.children(item_key)
        print(f"   ✅ 成功调用children()，返回类型: {type(children)}")
        print(f"   ✅ 返回数量: {len(children) if isinstance(children, list) else 'Not a list'}")
        
        if not isinstance(children, list):
            print(f"   ⚠️  返回的不是列表，而是: {type(children)}")
            children = []
        
        if len(children) == 0:
            print(f"   ⚠️  没有子项")
        else:
            print(f"   📋 子项列表:")
            for i, child in enumerate(children):
                print(f"      [{i+1}] 子项类型: {type(child)}")
                if isinstance(child, dict):
                    print(f"          Keys: {list(child.keys())}")
                    child_data = child.get('data', {})
                    if isinstance(child_data, dict):
                        child_type = child_data.get('itemType', 'unknown')
                        child_title = child_data.get('title', 'No title')
                        print(f"          类型: {child_type}, 标题: {child_title[:60]}...")
                        
                        if child_type == 'note':
                            note_content = child_data.get('note', '')
                            note_length = len(note_content)
                            print(f"          ✅ 这是笔记！长度: {note_length} 字符")
                            if note_length > 0:
                                import re
                                text_preview = re.sub(r'<[^>]+>', '', note_content[:200])
                                print(f"          预览: {text_preview}...")
                            else:
                                print(f"          ⚠️  笔记内容为空")
                    else:
                        print(f"          ⚠️  child['data']不是字典: {type(child_data)}")
                else:
                    print(f"          ⚠️  子项不是字典: {type(child)}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 方法2: 尝试从collection获取（模拟organizer.py的方式）
    print(f"\n方法2: 检查item所在的collections")
    try:
        collections = item.get('data', {}).get('collections', [])
        print(f"   Item在 {len(collections)} 个collections中")
        
        if collections:
            for coll_key in collections[:3]:
                try:
                    coll = zot.collection(coll_key)
                    coll_name = coll.get('data', {}).get('name', 'Unknown')
                    print(f"      Collection: {coll_name} (key: {coll_key[:8]}...)")
                except Exception as e:
                    print(f"      Collection key: {coll_key[:8]}... (无法获取详情: {e})")
    except Exception as e:
        print(f"   ⚠️  错误: {e}")
    
    # 方法3: 尝试通过collection_items获取（模拟organizer.py的fetch_all_items）
    print(f"\n方法3: 尝试通过collection获取items（模拟organizer.py）")
    if collections:
        for coll_key in collections[:1]:  # 只测试第一个collection
            try:
                print(f"   尝试从collection {coll_key[:8]}... 获取items...")
                coll_items = zot.collection_items(coll_key, tag='gemini_read')
                print(f"   找到 {len(coll_items)} 个items（带gemini_read标签）")
                
                # 查找当前item
                for coll_item in coll_items:
                    if coll_item.get('key') == item_key:
                        print(f"   ✅ 在collection中找到当前item")
                        print(f"      Collection item类型: {type(coll_item)}")
                        print(f"      Collection item keys: {list(coll_item.keys()) if isinstance(coll_item, dict) else 'Not a dict'}")
                        
                        # 尝试获取children
                        try:
                            coll_children = zot.children(item_key)
                            print(f"      ✅ 通过collection item获取children成功: {len(coll_children)} 个")
                        except Exception as e:
                            print(f"      ❌ 通过collection item获取children失败: {e}")
                        break
            except Exception as e:
                print(f"   ⚠️  错误: {e}")
                import traceback
                traceback.print_exc()

def main():
    print("="*80)
    print("测试脚本：检查特定文章的笔记读取")
    print("="*80)
    
    # 加载配置
    config = load_config(CONFIG_PATH)
    if not config:
        print("❌ 无法加载配置，退出")
        return
    
    # 初始化Zotero
    print(f"\n🔌 连接到Zotero...")
    print(f"   Library ID: {config.LIBRARY_ID}")
    print(f"   Library Type: {config.LIBRARY_TYPE}")
    
    try:
        zot = zotero.Zotero(config.LIBRARY_ID, config.LIBRARY_TYPE, config.API_KEY)
        items = zot.items(limit=1)
        print(f"✅ 连接成功！库中有items")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 查找论文
    items_found = find_items_by_titles(zot, TARGET_TITLES)
    
    if not items_found:
        print(f"\n❌ 未找到匹配的论文")
        return
    
    print(f"\n✅ 找到 {len(items_found)} 个匹配的论文")
    
    # 检查每个匹配的论文
    for item, expected_title in items_found:
        check_item_notes_detailed(zot, item, expected_title)
    
    print(f"\n{'='*80}")
    print("测试完成")

if __name__ == '__main__':
    main()
