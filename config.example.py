# ================= Zotero Gemini 阅读工具配置文件示例 =================
# 
# 使用方法：
# 1. 复制此文件为 config.py
# 2. 填入您的真实配置信息
# 3. config.py 已在 .gitignore 中，不会被提交到 Git
#
# ========================================================================

# --- Zotero 设置 ---
# 获取地址: https://www.zotero.org/settings/keys
# 注意：API Key 需要具有"读取"和"写入"权限（包括创建笔记的权限）
LIBRARY_ID = 'YOUR_LIBRARY_ID'       # 替换为您的库 ID
API_KEY = 'YOUR_ZOTERO_API_KEY'      # 替换为您的 Zotero API Key
LIBRARY_TYPE = 'user'  # 个人库填 'user'，群组库填 'group'

# 本地 Storage 路径 (用于找 PDF)
# Windows 示例: r'C:\Users\YourName\Zotero\storage'
# Mac 示例: '/Users/YourName/Zotero/storage'
# Linux 示例: '/home/username/Zotero/storage'
ZOTERO_STORAGE_PATH = r'C:\Users\YourName\Zotero\storage'  # 替换为您的 PDF 存储路径

# --- AI 模型设置 (Gemini) ---
# 获取 API Key: https://makersuite.google.com/app/apikey
AI_API_KEY = 'YOUR_GEMINI_API_KEY'  # 替换为您的 Gemini API Key
AI_MODEL = 'gemini-2.5-flash-lite'  # 可选模型: gemini-2.5-flash-lite, gemini-1.5-pro, gemini-1.5-flash

# --- 文件设置 ---
PROMPT_FILE_NAME = 'prompt.md'  # 提示词文件名

# --- 处理设置 ---
# 要处理的文献类型（None 表示处理所有类型）
# 常见类型: 'journalArticle', 'conferencePaper', 'thesis', 'book', 'bookSection'
# 示例: ITEM_TYPES_TO_PROCESS = ['journalArticle', 'conferencePaper']
ITEM_TYPES_TO_PROCESS = None  # None = 处理所有类型

# --- 集合设置 ---
# 指定要处理的集合路径（用 '/' 分隔层级，如 "0 2025/12"）
# None 表示处理整个库中的所有文献
# 示例: TARGET_COLLECTION_PATH = "0 2025/12"
TARGET_COLLECTION_PATH = None  # 设置为 None 处理整个库

# --- 测试设置 ---
TEST_MODE = False  # 测试模式：只处理前N个文献
TEST_LIMIT = 3    # 测试模式下处理的文献数量

# --- 标签清理设置（用于 tag_cleaner.py）---
# 要保留的标签列表（区分大小写）
KEEP_TAGS = ["精读", "重要", "可行", "参考"]  # 根据您的需求修改

