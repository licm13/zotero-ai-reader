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
# MIMO_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1" # tp- 开头的 Key 专用

# --- 提示词文件（与本文件夹内 md 同名）---
PROMPT_FILE_NAME = "prompt.md"

# --- 处理范围 ---
ITEM_TYPES_TO_PROCESS = None
# 支持动态日期：设为 "0-New/mmdd" 或包含 {{mmdd}} 将自动解析为当前月日（如 0419）。
TARGET_COLLECTION_PATH = "0-New/mmdd"

# --- 测试 ---
TEST_MODE = True
TEST_LIMIT = 3

# --- 可选：标签（与界面一致即可）---
SUCCESS_TAG = "mimo-read"
NON_LIT_TAG = "non-read-mimo"
# TAGS_SKIP_IF_PRESENT = ["mimo-read"]

# --- 备忘（本 reader 脚本不使用，仅与课程说明一致）---
KEEP_TAGS = ["精读", "重要", "mimo-read"]
