#!/usr/bin/env python3
"""
配置加载工具
============

提供统一的配置加载功能，支持：
1. 命令行参数指定config.py路径
2. 交互式输入路径
3. 文件选择对话框（GUI）
4. 自动搜索默认位置
"""

import os
import sys
import argparse
from typing import Optional

def find_config_file(start_dir: str = None) -> Optional[str]:
    """
    自动搜索config.py文件
    
    搜索顺序：
    1. 当前工作目录
    2. 脚本所在目录
    3. 脚本所在目录的父目录（项目根目录）
    """
    if start_dir is None:
        start_dir = os.getcwd()
    
    # 候选目录列表
    search_dirs = [
        os.getcwd(),  # 当前工作目录
        os.path.dirname(os.path.abspath(__file__)),  # 脚本所在目录
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # 项目根目录
    ]
    
    # 去重并保持顺序
    seen = set()
    search_dirs = [d for d in search_dirs if d not in seen and not seen.add(d)]
    
    for search_dir in search_dirs:
        config_path = os.path.join(search_dir, 'config.py')
        if os.path.exists(config_path) and os.path.isfile(config_path):
            return os.path.abspath(config_path)
    
    return None

def select_config_file_gui() -> Optional[str]:
    """
    使用GUI文件选择对话框选择config.py文件
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        root.attributes('-topmost', True)  # 置顶
        
        config_path = filedialog.askopenfilename(
            title="选择 config.py 文件",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialdir=os.getcwd()
        )
        
        root.destroy()
        
        if config_path and os.path.exists(config_path):
            return os.path.abspath(config_path)
    except ImportError:
        # tkinter不可用（某些Linux环境）
        pass
    except Exception as e:
        print(f"⚠️  GUI文件选择器不可用: {e}")
    
    return None

def select_config_file_interactive(default_path: str = None) -> Optional[str]:
    """
    交互式命令行选择config.py文件
    """
    print("\n" + "=" * 70)
    print("📋 选择 config.py 文件")
    print("=" * 70)
    
    if default_path:
        print(f"\n💡 建议位置: {default_path}")
    
    print("\n请选择config.py文件的位置：")
    print("  1. 使用建议位置（如果存在）")
    print("  2. 手动输入路径")
    print("  3. 浏览文件选择（GUI）")
    print("  4. 自动搜索")
    print("  0. 取消")
    
    while True:
        try:
            choice = input("\n请选择 [1-4, 0取消]: ").strip()
            
            if choice == '0':
                print("❌ 已取消")
                return None
            
            elif choice == '1':
                if default_path and os.path.exists(default_path):
                    print(f"✅ 使用: {default_path}")
                    return os.path.abspath(default_path)
                else:
                    print("⚠️  建议位置不存在，请选择其他选项")
            
            elif choice == '2':
                path = input("请输入 config.py 的完整路径: ").strip()
                # 去除引号
                path = path.strip('"').strip("'")
                if os.path.exists(path):
                    if path.endswith('config.py'):
                        print(f"✅ 使用: {os.path.abspath(path)}")
                        return os.path.abspath(path)
                    else:
                        print("⚠️  文件不是 config.py，是否继续？ [y/N]: ", end='')
                        if input().strip().lower() == 'y':
                            return os.path.abspath(path)
                else:
                    print(f"❌ 文件不存在: {path}")
            
            elif choice == '3':
                config_path = select_config_file_gui()
                if config_path:
                    print(f"✅ 已选择: {config_path}")
                    return config_path
                else:
                    print("⚠️  未选择文件，请重试")
            
            elif choice == '4':
                print("\n🔍 正在自动搜索 config.py...")
                config_path = find_config_file()
                if config_path:
                    print(f"✅ 找到: {config_path}")
                    return config_path
                else:
                    print("❌ 未找到 config.py 文件")
                    print("   请尝试手动指定路径")
            
            else:
                print("⚠️  无效选择，请输入 1-4 或 0")
        
        except KeyboardInterrupt:
            print("\n\n❌ 已取消")
            return None
        except Exception as e:
            print(f"❌ 错误: {e}")

def load_config(config_path: Optional[str] = None) -> Optional[object]:
    """
    加载config模块
    
    Args:
        config_path: config.py的路径，如果为None则尝试自动搜索或交互选择
    
    Returns:
        config模块对象，如果加载失败返回None
    """
    # 如果指定了路径，直接加载
    if config_path:
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return None
        
        # 添加到sys.path以便导入
        config_dir = os.path.dirname(os.path.abspath(config_path))
        if config_dir not in sys.path:
            sys.path.insert(0, config_dir)
        
        # 导入config模块
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", config_path)
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            print(f"✅ 已从 {config_path} 加载配置")
            return config
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return None
    
    # 尝试自动搜索
    default_path = find_config_file()
    
    # 如果找到，询问是否使用
    if default_path:
        print(f"💡 找到配置文件: {default_path}")
        use_default = input("是否使用此文件？ [Y/n]: ").strip().lower()
        if use_default != 'n':
            return load_config(default_path)
    
    # 交互式选择
    selected_path = select_config_file_interactive(default_path)
    if selected_path:
        return load_config(selected_path)
    
    return None

def get_config_from_args_or_interactive() -> Optional[object]:
    """
    从命令行参数获取config路径，如果没有则交互式选择
    
    使用方法：
        python script.py --config /path/to/config.py
        或
        python script.py  # 会弹出交互式选择界面
    """
    parser = argparse.ArgumentParser(description='Zotero AI工具 - 配置加载')
    parser.add_argument(
        '--config',
        type=str,
        help='config.py文件的路径（可选，如果不指定将弹出选择界面）'
    )
    
    args, unknown = parser.parse_known_args()
    
    if args.config:
        return load_config(args.config)
    else:
        return load_config(None)  # 交互式选择

# 便捷函数：直接获取配置（用于快速集成）
def get_config() -> Optional[object]:
    """
    快速获取配置，优先使用命令行参数，否则交互式选择
    """
    return get_config_from_args_or_interactive()

