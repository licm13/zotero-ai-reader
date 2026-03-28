# 学生版配置模板：复制本文件为 config.py 后填写真实值（勿提交 config.py 到公开仓库）

# --- Zotero ---
LIBRARY_ID = "YOUR_LIBRARY_ID"
API_KEY = "YOUR_ZOTERO_API_KEY"
LIBRARY_TYPE = "user"
ZOTERO_STORAGE_PATH = r"C:\Path\To\Your\zotero-pdf"

# --- 小米 MIMO（唯一支持的模型后端）---
# 获取密钥: https://platform.xiaomimimo.com/
XiaoMi_API_KEY = "YOUR_MIMO_API_KEY"
XIAOMI_MODEL = "mimo-v2-pro"

# --- 提示词文件（与本文件夹内 md 同名）---
PROMPT_FILE_NAME = "prompt.md"

# --- 处理范围 ---
ITEM_TYPES_TO_PROCESS = None
TARGET_COLLECTION_PATH = None

# --- 测试 ---
TEST_MODE = True
TEST_LIMIT = 3

# --- 可选：标签（与界面一致即可）---
SUCCESS_TAG = "MIMO_read"
NON_LIT_TAG = "non-read-mimo"
# TAGS_SKIP_IF_PRESENT = ["MIMO_read"]

# --- 备忘（本 reader 脚本不使用，仅与课程说明一致）---
KEEP_TAGS = ["精读", "重要", "MIMO_read"]
