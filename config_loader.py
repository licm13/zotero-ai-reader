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
    1. 默认配置文件路径（用户指定）
    2. 当前工作目录的上一级目录中的 zotero_ai_read_config.py
    3. 脚本所在目录的上一级目录中的 zotero_ai_read_config.py
    4. 当前工作目录中的 config.py
    5. 脚本所在目录中的 config.py
    6. 脚本所在目录的父目录（项目根目录）中的 config.py
    """
    if start_dir is None:
        start_dir = os.getcwd()
    
    # 默认配置文件路径（用户指定，可根据需要修改）
    # 注意：此路径仅作为示例，实际使用时请根据您的环境修改
    DEFAULT_CONFIG_PATH = None  # 设置为None以禁用默认路径，或设置为您的配置文件路径
    
    # 候选文件列表（按优先级排序）
    candidate_paths = []
    
    # 1. 首先检查默认配置文件路径
    if os.path.exists(DEFAULT_CONFIG_PATH) and os.path.isfile(DEFAULT_CONFIG_PATH):
        candidate_paths.append(os.path.abspath(DEFAULT_CONFIG_PATH))
    
    # 2. 检查上一级目录中的 zotero_ai_read_config.py（优先）
    parent_dirs = []
    
    # 当前工作目录的上一级
    current_dir = os.getcwd()
    current_parent = os.path.dirname(current_dir)
    if current_parent and current_parent != current_dir:
        parent_dirs.append(current_parent)
    
    # 脚本所在目录的上一级
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_parent = os.path.dirname(script_dir)
    if script_parent and script_parent != script_dir:
        parent_dirs.append(script_parent)
    
    # 去重并保持顺序
    seen = set()
    parent_dirs = [d for d in parent_dirs if d not in seen and not seen.add(d)]
    
    # 搜索上一级目录中的 zotero_ai_read_config.py
    for parent_dir in parent_dirs:
        zotero_config_path = os.path.join(parent_dir, 'zotero_ai_read_config.py')
        abs_path = os.path.abspath(zotero_config_path)
        if abs_path not in candidate_paths and os.path.exists(zotero_config_path) and os.path.isfile(zotero_config_path):
            candidate_paths.append(abs_path)
    
    # 3. 然后检查标准搜索目录中的config.py
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
        abs_path = os.path.abspath(config_path)
        if abs_path not in candidate_paths and os.path.exists(config_path) and os.path.isfile(config_path):
            candidate_paths.append(abs_path)
    
    # 返回第一个找到的配置文件
    if candidate_paths:
        return candidate_paths[0]
    
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

            if not spec:
                print(f"❌ 无法创建模块规范: {config_path}")
                return None

            if not spec.loader:
                print(f"❌ 模块规范缺少加载器: {config_path}")
                return None

            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)

            # 验证必需的配置属性
            required_attrs = ['LIBRARY_ID', 'API_KEY', 'LIBRARY_TYPE', 'AI_API_KEY']
            missing_attrs = []

            for attr in required_attrs:
                if not hasattr(config, attr):
                    missing_attrs.append(attr)

            if missing_attrs:
                print(f"❌ 配置文件缺少必需的属性: {', '.join(missing_attrs)}")
                print(f"   请确保config.py包含以下属性:")
                for attr in missing_attrs:
                    print(f"   - {attr}")
                return None

            # 验证属性值不为空
            empty_attrs = []
            for attr in required_attrs:
                value = getattr(config, attr, None)
                if not value or (isinstance(value, str) and not value.strip()):
                    empty_attrs.append(attr)

            if empty_attrs:
                print(f"⚠️  警告: 以下配置属性为空: {', '.join(empty_attrs)}")
                print(f"   程序可能无法正常工作")

            # 验证LIBRARY_TYPE的值是否有效
            if hasattr(config, 'LIBRARY_TYPE'):
                valid_types = ['user', 'group']
                if config.LIBRARY_TYPE not in valid_types:
                    print(f"⚠️  警告: LIBRARY_TYPE值无效 ('{config.LIBRARY_TYPE}')，应为: {', '.join(valid_types)}")

            print(f"✅ 已从 {config_path} 加载配置")
            return config

        except SyntaxError as syntax_err:
            print(f"❌ 配置文件语法错误: {syntax_err}")
            print(f"   文件: {config_path}")
            print(f"   行号: {syntax_err.lineno if hasattr(syntax_err, 'lineno') else '未知'}")
            return None
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            import traceback
            traceback.print_exc()
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

