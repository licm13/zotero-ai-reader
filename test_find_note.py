#!/usr/bin/env python3
"""
测试脚本：查找特定论文的笔记
用于诊断为什么笔记没有被找到
"""

import sys
import os
from pyzotero import zotero

# 配置路径
CONFIG_PATH = r'C:\Users\ASUS\OneDrive\SCI\Github\zotero_ai_read_config.py'

# 目标论文标题（部分匹配）
TARGET_TITLE = "A novel high-resolution soil-moisture mapping using sentinel-1-imagery and optimization-based for a new precise remote sensing drought index"

def load_config(config_path):
    """加载配置文件"""
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return None
    
    # 添加到sys.path以便导入
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
        
        # 验证必需的配置属性
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

def find_item_by_title(zot, title_keywords):
    """根据标题关键词查找论文"""
    print(f"\n🔍 搜索论文（关键词: {title_keywords[:80]}...）")
    
    # 尝试多种搜索方式
    search_queries = [
        title_keywords,  # 完整标题
        title_keywords[:50],  # 前50个字符
        "soil-moisture mapping",  # 关键词
        "sentinel-1",  # 关键词
    ]
    
    all_items = []
    
    # 方法1: 搜索所有items
    print("\n方法1: 获取所有items并过滤...")
    try:
        items = zot.items()
        print(f"   找到 {len(items)} 个items")
        
        for item in items:
            item_title = item.get('data', {}).get('title', '')
            if title_keywords.lower() in item_title.lower():
                all_items.append(item)
                print(f"   ✅ 匹配: {item_title[:80]}...")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 方法2: 使用搜索API（如果支持）
    print("\n方法2: 尝试使用搜索API...")
    try:
        # pyzotero可能支持搜索，但需要检查
        # 这里先尝试获取items with limit
        items = zot.items(limit=100)
        print(f"   获取了 {len(items)} 个items（限制100）")
        
        for item in items:
            item_title = item.get('data', {}).get('title', '')
            if title_keywords.lower() in item_title.lower():
                if item not in all_items:
                    all_items.append(item)
                    print(f"   ✅ 匹配: {item_title[:80]}...")
    except Exception as e:
        print(f"   ⚠️  搜索API可能不支持: {e}")
    
    return all_items

def check_item_notes(zot, item):
    """检查item的笔记"""
    item_key = item.get('key', '')
    item_title = item.get('data', {}).get('title', 'Unknown')
    item_type = item.get('data', {}).get('itemType', 'unknown')
    
    print(f"\n{'='*80}")
    print(f"📄 论文信息:")
    print(f"   标题: {item_title}")
    print(f"   类型: {item_type}")
    print(f"   Key: {item_key}")
    
    # 方法1: 使用children()方法
    print(f"\n方法1: 使用 zot.children('{item_key}')")
    try:
        children = zot.children(item_key)
        print(f"   ✅ 成功调用children()，返回 {len(children)} 个子项")
        
        if len(children) == 0:
            print(f"   ⚠️  没有子项")
        else:
            print(f"   📋 子项列表:")
            for i, child in enumerate(children):
                child_type = child.get('data', {}).get('itemType', 'unknown')
                child_title = child.get('data', {}).get('title', 'No title')
                print(f"      [{i+1}] 类型: {child_type}, 标题: {child_title[:60]}...")
                
                if child_type == 'note':
                    note_content = child.get('data', {}).get('note', '')
                    note_length = len(note_content)
                    print(f"          ✅ 这是笔记！长度: {note_length} 字符")
                    if note_length > 0:
                        # 显示前200个字符
                        import re
                        text_preview = re.sub(r'<[^>]+>', '', note_content[:200])
                        print(f"          预览: {text_preview}...")
                    else:
                        print(f"          ⚠️  笔记内容为空")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 方法2: 尝试获取完整item信息
    print(f"\n方法2: 使用 zot.item('{item_key}')")
    try:
        full_item = zot.item(item_key)
        if isinstance(full_item, list) and len(full_item) > 0:
            full_item = full_item[0]
        
        print(f"   ✅ 成功获取完整item信息")
        print(f"   类型: {type(full_item)}")
        
        if isinstance(full_item, dict):
            item_data = full_item.get('data', {})
            print(f"   Item data keys: {list(item_data.keys())[:10]}...")
            
            # 检查是否有notes字段
            if 'notes' in item_data:
                print(f"   ✅ 找到'notes'字段: {item_data['notes']}")
            else:
                print(f"   ⚠️  没有'notes'字段")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 方法3: 尝试通过collection获取
    print(f"\n方法3: 检查item所在的collections")
    try:
        collections = item.get('data', {}).get('collections', [])
        print(f"   Item在 {len(collections)} 个collections中")
        
        if collections:
            for coll_key in collections[:3]:  # 只显示前3个
                try:
                    coll = zot.collection(coll_key)
                    coll_name = coll.get('data', {}).get('name', 'Unknown')
                    print(f"      Collection: {coll_name} (key: {coll_key[:8]}...)")
                except:
                    print(f"      Collection key: {coll_key[:8]}... (无法获取详情)")
    except Exception as e:
        print(f"   ⚠️  错误: {e}")

def main():
    print("="*80)
    print("测试脚本：查找论文笔记")
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
        
        # 测试连接
        items = zot.items(limit=1)
        print(f"✅ 连接成功！库中有items")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 查找论文
    items = find_item_by_title(zot, TARGET_TITLE)
    
    if not items:
        print(f"\n❌ 未找到匹配的论文")
        print(f"\n💡 尝试搜索所有items...")
        try:
            all_items = zot.items(limit=50)
            print(f"   前50个items的标题:")
            for i, item in enumerate(all_items[:10]):
                title = item.get('data', {}).get('title', 'Unknown')[:60]
                print(f"      [{i+1}] {title}...")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        return
    
    print(f"\n✅ 找到 {len(items)} 个匹配的论文")
    
    # 检查每个匹配的论文
    for i, item in enumerate(items):
        print(f"\n{'#'*80}")
        print(f"论文 #{i+1}")
        check_item_notes(zot, item)
    
    print(f"\n{'='*80}")
    print("测试完成")

if __name__ == '__main__':
    main()
