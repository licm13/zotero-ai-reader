# Zotero AI 阅读工具 — 学生版（小米 MIMO）

本文件夹为**独立分发包**：仅使用**小米 MIMO** OpenAPI（OpenAI 兼容接口）分析 PDF，并将结构化笔记写回 Zotero。已内置课程用 **`prompt.md`** 模板，也可在图形界面中直接修改。

## 内容与依赖

| 文件 | 说明 |
|------|------|
| `gui_mimo_student.py` | **主入口（推荐）**：图形界面 |
| `reader_mimo_student.py` | 批处理核心（由 GUI 或命令行调用） |
| `prompt.md` | 默认提示词（与教师版一致） |
| `config.example.py` | 配置模板，复制为 `config.py` 后填写 |
| `requirements.txt` | Python 依赖 |

系统要求：Python 3.8+（建议 3.10+），需已安装 Zotero 并开启同步，且 Zotero API Key 具备**读写与创建笔记**权限。

## 快速开始

1. 在本文件夹打开终端，安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 复制配置并编辑：

   ```bash
   copy config.example.py config.py
   ```

   （macOS / Linux 使用 `cp`。）在 `config.py` 中填写 `LIBRARY_ID`、`API_KEY`、`ZOTERO_STORAGE_PATH`、`XiaoMi_API_KEY` 等。
   - **动态集合路径**：`TARGET_COLLECTION_PATH` 默认设为 `0-New/mmdd`。启动程序时将自动解析为当天月日（如 `0420`）。

3. 启动图形界面：

   ```bash
   python gui_mimo_student.py
   ```

   - 点击「加载配置」可从 `config.py` 读入字段；在「提示词」页可编辑并「保存提示词到 prompt.md」。
   - 确认「小米 MIMO」中的 Key 与模型无误后，点击「开始运行」。

## 纯命令行（可选）

已存在本目录下的 `config.py` 时：

```bash
python reader_mimo_student.py --cli
```

直接运行 `reader_mimo_student.py` 不带参数时，会提示使用上述两种方式之一。

## 小米 MIMO 说明

- 注册与密钥：<https://platform.xiaomimimo.com/>
- **Token Plan 支持**：如果您的 Key 以 `tp-` 开头，程序会自动识别并切换至专属端点。若有特殊需求，也可在 `config.py` 中通过 `MIMO_BASE_URL` 手动指定。
- 若返回余额相关错误，请在平台侧检查账户与用量。

## 安全提示

- **不要将 `config.py` 上传到公开仓库或发给他人。**
- 本包**不包含** Google Gemini，与完整仓库中的 `reader.py`（双模型）相互独立。

## 与仓库根目录的关系

- **本文件夹**：仅小米 MIMO + 轻量依赖，适合发给学生。  
- **上级目录**：`reader_gui.py` + `reader.py` 为**完整版图形界面**（可选 Gemini 或 MIMO），与课程小包相互独立。
