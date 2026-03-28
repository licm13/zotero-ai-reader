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
├── prompt.md              # 默认提示词模板
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
- [Zotero](https://www.zotero.org/) 账户，API Key 需 **读取 + 写入（含创建笔记）**
- **Gemini**：[Google AI Studio](https://makersuite.google.com/app/apikey) 获取 Key（选用）
- **小米 MIMO**：[开放平台](https://platform.xiaomimimo.com/) 获取 Key（选用）

---

## 快速开始（完整版 GUI）

```bash
pip install -r requirements.txt
copy config.example.py config.py   # Windows；macOS/Linux: cp ...
# 编辑 config.py，填写 Zotero 与至少一种 AI 的密钥
python reader_gui.py
```

在界面中可加载/编辑配置、修改 `prompt.md` 对应内容、选择 Gemini 或 MIMO，再点击「开始运行」。

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

---

## 许可证

若仓库根目录包含 `LICENSE` 文件，以该文件为准；否则由项目维护者自行补充。
