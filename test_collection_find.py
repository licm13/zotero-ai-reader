#!/usr/bin/env python3
"""
测试脚本：查找 Zotero collection
用于调试 collection 查找问题
"""

import sys
from pyzotero import zotero
from config_loader import get_config_from_args_or_interactive

config = get_config_from_args_or_interactive()
if config is None:
    print("❌ 无法加载配置文件，程序退出")
    sys.exit(1)

# 初始化 Zotero
zot = zotero.Zotero(config.LIBRARY_ID, config.LIBRARY_TYPE, config.API_KEY)

print("=" * 70)
print("🔍 Collection 查找测试")
print("=" * 70)

# 获取所有 collections
print("\n📥 获取所有 collections...")
try:
    all_colls = zot.collections()
    print(f"✅ 获取到 {len(all_colls)} 个 collections")
except Exception as e:
    print(f"❌ 获取 collections 失败: {e}")
    sys.exit(1)

# 打印所有顶级 collections
print("\n📋 所有顶级 collections（没有父 collection 的）:")
top_level = []
for c in all_colls:
    parent = c['data'].get('parentCollection', None)
    if not parent:
        name = c['data']['name']
        top_level.append(name)
        print(f"   - {name} (Key: {c['key']})")

print(f"\n✅ 找到 {len(top_level)} 个顶级 collections")

# 检查是否包含 "0-New"
print("\n🔍 检查是否包含 '0-New':")
if '0-New' in top_level:
    print("   ✅ 找到了 '0-New'")
    # 找到它的 key
    for c in all_colls:
        if c['data']['name'] == '0-New' and not c['data'].get('parentCollection'):
            print(f"   Key: {c['key']}")
            # 查找它的子 collections
            print(f"\n📋 '0-New' 的子 collections:")
            for child in all_colls:
                if child['data'].get('parentCollection') == c['key']:
                    print(f"   - {child['data']['name']} (Key: {child['key']})")
else:
    print("   ❌ 没有找到 '0-New'")
    print(f"\n💡 可用的顶级 collections: {', '.join(top_level[:20])}")

# 尝试构建路径缓存
print("\n📋 构建路径缓存:")
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

cache = {}
for c in all_colls:
    full_path = build_full_path(c)
    cache[full_path] = c['key']
    if '0-New' in full_path:
        print(f"   ✅ {full_path} -> {c['key']}")

# 检查目标路径
target_path = "0-New/test"
print(f"\n🔍 检查目标路径: '{target_path}'")
if target_path in cache:
    print(f"   ✅ 找到了！Key: {cache[target_path]}")
else:
    print(f"   ❌ 没有找到")
    # 查找包含 "0-New" 的所有路径
    matching = [p for p in cache.keys() if '0-New' in p]
    if matching:
        print(f"\n💡 包含 '0-New' 的路径:")
        for p in matching[:20]:
            print(f"   - {p}")

print("\n" + "=" * 70)
print("✅ 测试完成")
