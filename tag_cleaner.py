from pyzotero import zotero
import time

# ================= 1. 配置加载 =================
# 优先从 config.py 读取配置，如果不存在则使用默认值（不推荐）
try:
    import config
    LIBRARY_ID = config.LIBRARY_ID
    API_KEY = config.API_KEY
    LIBRARY_TYPE = config.LIBRARY_TYPE
    KEEP_TAGS = getattr(config, 'KEEP_TAGS', ["精读", "重要", "可行", "参考"])
    ITEM_TYPES_TO_PROCESS = getattr(config, 'ITEM_TYPES_TO_PROCESS', None)
    print("✅ 已从 config.py 加载配置")
except ImportError:
    print("⚠️  未找到 config.py 文件！")
    print("📋 请复制 config.example.py 为 config.py 并填入您的配置信息")
    print("   或者修改此文件中的配置（不推荐，因为会暴露敏感信息）")
    print("   按 Enter 继续使用默认配置（如果已在此文件中配置）...")
    input()
    
    # 默认配置（仅用于开发测试，生产环境请使用 config.py）
    # ⚠️ 警告：不要将真实的 API 密钥提交到 Git！
    LIBRARY_ID = 'YOUR_LIBRARY_ID'
    API_KEY = 'YOUR_ZOTERO_API_KEY'
    LIBRARY_TYPE = 'user'
    KEEP_TAGS = ["精读", "重要", "可行", "参考"]
    ITEM_TYPES_TO_PROCESS = None

# ================= 2. 功能函数定义 =================

def clean_zotero_item_tags(zot, item_key, keep_tags=None):
    """
    移除Zotero条目上除指定标签外的所有标签。
    Args:
        zot: Zotero 客户端实例
        item_key: 需要处理的条目key
        keep_tags: 要保留的标签列表（字符串，区分大小写）。默认为配置中的KEEP_TAGS
    """
    if keep_tags is None:
        keep_tags = KEEP_TAGS
    
    try:
        # 获取当前项目
        item = zot.item(item_key)
        current_tags = item['data'].get('tags', [])
        
        # 获取当前所有标签名
        current_tag_names = [tag.get('tag') for tag in current_tags if tag.get('tag')]
        
        # 筛选保留的标签
        filtered_tags = [tag for tag in current_tags if tag.get('tag') in keep_tags]
        
        # 如果标签有变化才提交更新
        if len(filtered_tags) != len(current_tags):
            removed_tags = [name for name in current_tag_names if name not in keep_tags]
            item['data']['tags'] = filtered_tags
            zot.update_item(item)
            kept_tag_names = [tag['tag'] for tag in filtered_tags]
            print(f"   🧹 已清理 {len(removed_tags)} 个标签: {', '.join(removed_tags) if removed_tags else '无'}")
            print(f"   ✅ 保留标签: {', '.join(kept_tag_names) if kept_tag_names else '无'}")
            return True
        else:
            print(f"   ℹ️  无需清理（所有标签都在保留列表中）")
            return False
    except Exception as e:
        print(f"   ⚠️  清理标签失败: {str(e)}")
        return False

# ================= 3. 主程序流程 =================

def main():
    print("🚀 标签清理程序启动...")
    print(f"📋 配置：保留标签 = {', '.join(KEEP_TAGS)}")
    
    # 1. 初始化 Zotero 客户端
    zot = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY)
    
    # 2. 获取所有文献列表（分页获取）
    print("\n📥 正在获取 Zotero 文献列表...")
    
    # 获取所有项目（使用分页）
    all_items = []
    start = 0
    batch_size = 100  # 每次获取100个
    
    while True:
        try:
            batch = zot.items(start=start, limit=batch_size)
            if not batch:
                break
            all_items.extend(batch)
            print(f"   已获取 {len(all_items)} 个文献...")
            
            # 如果返回的数量少于 batch_size，说明已经获取完所有数据
            if len(batch) < batch_size:
                break
            
            start += batch_size
        except Exception as e:
            print(f"   ⚠️  获取文献时出错: {e}")
            break
    
    print(f"✅ 总共找到 {len(all_items)} 个文献\n")
    
    # 统计信息
    processed_count = 0
    cleaned_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, item in enumerate(all_items, 1):
        title = item['data'].get('title', '无标题')
        item_key = item['key']
        item_type = item['data'].get('itemType', '')
        
        # 如果设置了文献类型过滤，只处理指定类型
        if ITEM_TYPES_TO_PROCESS is not None:
            if item_type not in ITEM_TYPES_TO_PROCESS:
                skipped_count += 1
                continue  # 跳过不符合类型的文献
        
        # 显示进度
        print(f"[{idx}/{len(all_items)}] 处理文献: {title[:60]}...")
        
        # 检查是否有标签
        item_tags = item['data'].get('tags', [])
        if not item_tags:
            print(f"   ⏭️  跳过 (无标签)")
            skipped_count += 1
            continue
        
        # 清理标签
        try:
            was_cleaned = clean_zotero_item_tags(zot, item_key, KEEP_TAGS)
            if was_cleaned:
                cleaned_count += 1
            processed_count += 1
        except Exception as e:
            print(f"   ❌ 处理失败: {str(e)}")
            error_count += 1
        
        # 显示当前统计
        print(f"   📊 进度: 已处理 {processed_count} | 已清理 {cleaned_count} | 已跳过 {skipped_count} | 错误 {error_count}\n")
        
        # 休息一下，避免触发 API 频率限制
        time.sleep(0.5)
    
    # 最终统计
    print(f"\n{'='*60}")
    print(f"📊 处理完成！")
    print(f"   总计: {len(all_items)} 个文献")
    print(f"   已处理: {processed_count} 个")
    print(f"   已清理: {cleaned_count} 个（移除了无关标签）")
    print(f"   已跳过: {skipped_count} 个（无标签或不符合类型）")
    print(f"   错误: {error_count} 个")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

