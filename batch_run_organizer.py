#!/usr/bin/env python3
"""
批量运行 organizer.py，处理多个 collection

依次修改配置文件中的 TARGET_COLLECTION_PATH，然后运行 organizer.py 处理每个 collection
"""

import os
import sys
import re
import subprocess
from datetime import datetime

# 要处理的 collection 列表
COLLECTIONS = [
    'Fire',
    'GCM',
    'Hydro-Model',
    'Hydroclimate Volatility',
    'LSM-Reanalysis',
    'Open Water',
    'Review',
    'Snow',
    'Soil',
    'Temperature',
    'Terrestrial',
    'Vegetation'
]

# 配置文件路径（上一级目录）
CONFIG_FILE = os.path.join('..', 'zotero_ai_read_config.py')

# 日志文件
LOG_FILE = 'batch_run_log.txt'


def update_config_file(collection_path):
    """
    修改配置文件中的 TARGET_COLLECTION_PATH
    
    Args:
        collection_path: 要设置的 collection 路径
    """
    try:
        # 读取配置文件
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式替换 TARGET_COLLECTION_PATH（只匹配非注释的行）
        # 匹配行首（或空白）后跟 TARGET_COLLECTION_PATH = 'xxx' 或 TARGET_COLLECTION_PATH = None
        pattern = r"^(\s*)TARGET_COLLECTION_PATH\s*=\s*(?:'[^']*'|\"[^\"]*\"|None)"
        
        if collection_path is None:
            replacement = r"\1TARGET_COLLECTION_PATH = None"
        else:
            # 转义单引号
            escaped_path = collection_path.replace("'", "\\'")
            replacement = f"\\1TARGET_COLLECTION_PATH = '{escaped_path}'"
        
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # 写入配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"[ERROR] 修改配置文件失败: {e}")
        return False


def run_organizer():
    """
    运行 organizer.py
    
    Returns:
        (success, output): (是否成功, 输出内容)
    """
    try:
        # 运行 organizer.py
        result = subprocess.run(
            [sys.executable, 'organizer.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        return success, output
    except Exception as e:
        return False, f"运行 organizer.py 时出错: {e}"


def log_message(message, log_file=LOG_FILE):
    """记录日志消息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)


def main():
    """主函数：批量处理所有 collection"""
    
    print("=" * 80)
    print("批量运行 Zotero AI Paper Organizer")
    print("=" * 80)
    print(f"配置文件: {CONFIG_FILE}")
    print(f"要处理的 collection 数量: {len(COLLECTIONS)}")
    print(f"日志文件: {LOG_FILE}")
    print("=" * 80)
    
    # 检查配置文件是否存在
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] 配置文件不存在: {CONFIG_FILE}")
        sys.exit(1)
    
    # 初始化日志文件
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"批量运行开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"要处理的 collection: {COLLECTIONS}\n")
        f.write("=" * 80 + "\n\n")
    
    # 统计信息
    success_count = 0
    failed_count = 0
    failed_collections = []
    
    # 处理每个 collection
    for i, collection in enumerate(COLLECTIONS, 1):
        print(f"\n{'=' * 80}")
        print(f"[{i}/{len(COLLECTIONS)}] 处理 collection: {collection}")
        print(f"{'=' * 80}")
        log_message(f"开始处理 collection: {collection}")
        
        # 更新配置文件
        if not update_config_file(collection):
            log_message(f"❌ 失败: 无法更新配置文件", LOG_FILE)
            failed_count += 1
            failed_collections.append(collection)
            continue
        
        log_message(f"✅ 配置文件已更新: TARGET_COLLECTION_PATH = '{collection}'")
        
        # 运行 organizer.py
        print(f"\n运行 organizer.py...")
        success, output = run_organizer()
        
        if success:
            log_message(f"✅ 成功处理 collection: {collection}")
            success_count += 1
            print(f"\n✅ Collection '{collection}' 处理成功")
        else:
            log_message(f"❌ 处理 collection '{collection}' 时出错")
            log_message(f"错误输出:\n{output}")
            failed_count += 1
            failed_collections.append(collection)
            print(f"\n❌ Collection '{collection}' 处理失败")
            print(f"错误信息:\n{output}")
        
        # 保存详细输出到日志文件
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n--- Collection: {collection} 的输出 ---\n")
            f.write(output)
            f.write(f"\n--- 结束 Collection: {collection} 的输出 ---\n\n")
        
        # 在每个collection之间添加分隔
        print(f"\n{'=' * 80}\n")
    
    # 打印最终统计
    print("\n" + "=" * 80)
    print("批量处理完成")
    print("=" * 80)
    print(f"总计: {len(COLLECTIONS)} 个 collection")
    print(f"成功: {success_count} 个")
    print(f"失败: {failed_count} 个")
    
    if failed_collections:
        print(f"\n失败的 collection:")
        for coll in failed_collections:
            print(f"  - {coll}")
    
    log_message(f"批量处理完成: 成功 {success_count}/{len(COLLECTIONS)}, 失败 {failed_count}/{len(COLLECTIONS)}")
    
    if failed_collections:
        log_message(f"失败的 collection: {failed_collections}")
    
    print(f"\n详细日志已保存到: {LOG_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    main()
