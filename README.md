# Zotero AI Reader

使用 **Google Gemini** 或 **小米 MIMO** 阅读 Zotero 中的 PDF，生成结构化笔记并写回文献条目。本仓库聚焦两件事：

1. **完整版图形界面**（根目录）：`reader_gui.py` + `reader.py`  
2. **学生分发包**（仅小米 MIMO）：[`student_pack/`](student_pack/README.md)

---

## 仓库结构

```
zotero-ai-reader/
├── reader_gui.py          # 推荐入口：图形界面（双模型可选）
├── reader.py              # 阅读核心（由 GUI 或命令行调用）
├── config_loader.py       # 配置发现与交互加载
├── config.example.py      # 配置模板 → 复制为 config.py
├── prompt.md              # 提示词模板（可通过 GUI 直接编辑）
├── requirements.txt
├── student_pack/          # 学生独立小包（见 student_pack/README.md）
│   ├── gui_mimo_student.py
│   ├── reader_mimo_student.py
│   ├── config.example.py
│   ├── prompt.md
│   ├── requirements.txt
│   └── README.md
└── README.md
```

---

## 环境要求

- Python 3.8+（建议 3.10+）
- 下面「账户与 API」中列出的服务账号（按你选用的模型准备即可）

---

## 账户与 API 从哪找

### Zotero（文献库 + 本工具写入笔记）

1. **注册与软件**  
   - 打开 [https://www.zotero.org/](https://www.zotero.org/) 注册免费账号，并安装桌面客户端（Windows / Mac 均可）。  
   - 本工具通过 **网络 API** 操作你在 zotero.org 上同步的文献库，请确保已在客户端里登录同一账号并开启同步。

2. **用户库 ID（`LIBRARY_ID`）**  
   - 用浏览器登录 [https://www.zotero.org/](https://www.zotero.org/)，点右上角进入个人主页或「我的文库」。  
   - 看浏览器地址栏：形如 `https://www.zotero.org/username` 时，个人库 ID 多为 **纯数字**，也可在 [https://www.zotero.org/settings/keys](https://www.zotero.org/settings/keys) 页面附近说明里核对；若是群组库，请到对应群组页面查看其 **Group ID**（也是数字）。  
   - `config.py` 里个人库一般写：`LIBRARY_TYPE = 'user'`；群组库写：`LIBRARY_TYPE = 'group'`，`LIBRARY_ID` 填该组的数字 ID。

3. **API Key（`API_KEY`）**  
   - 打开 [https://www.zotero.org/settings/keys](https://www.zotero.org/settings/keys)。  
   - 创建新密钥时务必勾选 **允许访问文库（Allow library access）**，并允许 **创建笔记 / 写入**（界面可能写作 *Notes* 或 *Write* 相关选项，以官网当前文案为准）。只读 Key 会导致无法把 AI 笔记写回 Zotero。

4. **本地 PDF 路径（`ZOTERO_STORAGE_PATH`）**  
   - 本工具要在本机磁盘上找到 PDF 文本，需填你存放同步 PDF 的文件夹（例如自建的 `zotero-pdf` 同步目录，或你了解的实际路径）。  
   - 与「Zotero 数据目录」不一定相同；以你电脑上 PDF 真实所在为准，在资源管理器里复制路径即可。

---

### Google Gemini（选用）

1. **账号**  
   - 使用常用 **Google 账号** 登录即可。

2. **API Key（`AI_API_KEY`）**  
   - 打开 [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)（或 [Google AI Studio](https://ai.google.dev/) 内「Get API key」）。  
   - 按页面提示创建 **API Key**，复制到 `config.py` 的 `AI_API_KEY`。  
   - 免费额度与地区政策以 Google 当前说明为准；若网页打不开，多半是网络或区域限制，需自行解决访问环境。

3. **模型名称（`AI_MODEL`）**  
   - 在 `config.example.py` 里有默认示例；若调用报错「模型不存在」，请到 [Google AI 文档 / 模型列表](https://ai.google.dev/gemini-api/docs/models) 查看当前可用模型名并改配置。

---

### 小米 MIMO（选用；学生包仅支持此项）

1. **账号与控制台**  
   - 打开 [https://platform.xiaomimimo.com/](https://platform.xiaomimimo.com/) 注册/登录。  
   - 平台分为 **普通账号** 和 **Token Plan (按量计费)**。普通账号通常有一定试用额度；Token Plan 需充值且密钥以 `tp-` 开头。

2. **API Key（`XiaoMi_API_KEY`）**  
   - 在控制台内创建或查看 **API Key**。
   - 如果您的密钥以 `tp-` 开头，程序会 **自动识别** 并切换到专属的高速接口（`token-plan-cn.xiaomimimo.com`）。您也可以在配置中手动通过 `MIMO_BASE_URL` 指定。

3. **模型名称（`XIAOMI_MODEL`）**  
   - 推荐模型：`mimo-v2-pro`（逻辑强）、`mimo-v1-pro` 等。
   - 若有视觉需求，可配置 `XIAOMI_VISION_MODEL = 'mimo-v2-omni'`（请确认您的账号权限）。

---

## 快速开始（完整版 GUI）

```bash
pip install -r requirements.txt
copy config.example.py config.py   # Windows；macOS/Linux: cp ...
# 编辑 config.py，填写 Zotero 与至少一种 AI 的密钥；默认使用小米 MIMO。
python reader_gui.py
```

在界面中可加载/编辑配置、修改 `prompt.md` 对应内容、选择 Gemini 或 MIMO（系统默认预设为小米），再点击「开始运行」。默认的「目标集合路径」已设为动态的 `0-New/mmdd`，会自动匹配当天日期。

### 提示词编辑

在 GUI 的「提示词」标签页中，您可以直接编辑提示词内容。编辑完成后可点击「保存提示词到文件」来更新本地的 `prompt.md` 或其他指定文件。点击窗口顶部的「重载提示词文件」可将文件中的最新内容重新加载到编辑框中。

### 命令行（可选）

```bash
python reader.py
```

将按 `config_loader` 规则选择配置文件，并在终端交互选择 PDF 路径与模型（行为以 `reader.py` 为准）。

---

## 学生包 `student_pack`

面向课程分发：**只支持小米 MIMO**，依赖更少（无 `google-genai`）。使用方式见 **[student_pack/README.md](student_pack/README.md)**。

---

## 安全提示

- **勿**将 `config.py` 或含真实密钥的文件提交到公开仓库（本仓库 `.gitignore` 已忽略 `config.py`）。
- 分享代码时使用 `config.example.py` 中的占位符。