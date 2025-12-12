# 🤖 Zotero AI Reader

<div align="center">

**让 AI 帮你读论文，解放你的时间！**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zotero](https://img.shields.io/badge/Zotero-API-orange.svg)](https://www.zotero.org/)

*一个强大的 Zotero 文献自动化阅读和分析工具，使用 AI 深度理解论文，自动生成结构化笔记*

[✨ 特性](#-核心特性) • [🚀 快速开始](#-快速开始) • [📖 使用指南](#-使用指南) • [💡 使用场景](#-使用场景)

</div>

---

## 🌟 为什么需要它？

还在为堆积如山的论文发愁吗？还在逐字逐句地阅读每一篇文献吗？

**Zotero AI Reader** 来拯救你！🎉

这个工具可以：

- 📚 **自动读取** Zotero 文献库中的 PDF
- 🧠 **AI 深度分析** 论文的核心内容
- 📝 **生成结构化笔记** 直接保存到 Zotero
- ⚡ **批量处理** 整个文献库或指定集合
- 🏷️ **智能标记** 已处理的文献，避免重复工作

**想象一下**：早上起床，发现昨晚的 50 篇论文已经被 AI 分析完毕，每篇都有详细的结构化笔记，而你只需要喝杯咖啡，浏览一下重点！☕

---

## ✨ 核心特性

### 🎯 智能论文分析

- **8 大分析维度**：从核心总览到通俗解读，全方位理解论文
- **结构化输出**：研究问题、论证路径、数据方法、批判视角一应俱全
- **防幻觉设计**：强调引用页码和图表编号，确保信息准确

### 🔄 自动化工作流

- **零手动操作**：配置一次，自动处理整个文献库
- **智能去重**：自动跳过已处理的文献
- **批量处理**：支持按集合、类型筛选，灵活控制

### 🎨 完美集成

- **无缝对接 Zotero**：笔记直接保存为文献子项
- **智能 PDF 搜索**：多种策略自动定位 PDF 文件
- **标签管理**：自动添加处理标记，便于管理

### 🛡️ 安全可靠

- **配置分离**：敏感信息独立管理，不会泄露
- **错误处理**：完善的异常处理和重试机制
- **进度追踪**：实时显示处理进度和统计信息

---

## 💡 使用场景

### 📖 研究生/博士生

- **文献综述**：快速理解大量相关论文，提取关键信息
- **开题准备**：系统分析领域现状，发现研究缺口
- **论文写作**：快速回顾已读文献，引用关键观点

### 👨‍🏫 研究人员

- **领域追踪**：定期批量分析新发表的论文
- **教学准备**：快速筛选适合教学的论文案例
- **基金申请**：系统梳理相关研究，支撑申请材料

### 📚 学术爱好者

- **知识管理**：建立结构化的文献知识库
- **快速学习**：高效理解新领域的核心论文
- **笔记整理**：自动生成标准化笔记，便于检索

---

## 📁 项目结构

```
zotero-ai-reader/
├── reader.py               # 🎯 主程序：AI 论文分析工具
├── tag_cleaner.py          # 🧹 标签清理工具
├── prompt.md               # 📋 AI 分析提示词模板
├── config.example.py       # ⚙️ 配置文件模板
├── requirements.txt        # 📦 依赖包列表
└── README.md               # 📖 本文件
```

---

## 🎯 核心文件说明

### 1. `reader.py` - 主程序 🚀

**这是项目的核心！** 它会自动处理你的 Zotero 文献库。

**工作流程**：

```
📥 连接 Zotero → 🔍 查找 PDF → 📖 提取文本 → 🤖 AI 分析 → 💾 保存笔记
```

**核心能力**：

- ✅ 智能 PDF 搜索（支持多种匹配策略）
- ✅ 批量处理（支持集合筛选、类型过滤）
- ✅ 自动去重（通过标签识别已处理文献）
- ✅ 错误恢复（完善的异常处理机制）

**快速上手**：

```bash
# 1. 配置 config.py（见下方）
# 2. 运行程序
python reader.py
```

---

### 2. `tag_cleaner.py` - 标签清理工具 🧹

**文献库标签太多太乱？** 这个工具帮你一键清理！

**功能**：

- 🎯 批量清理标签，只保留重要标签
- 🔍 支持按文献类型过滤
- 📊 实时显示清理进度和统计

**使用场景**：

- 清理导入文献时自动添加的冗余标签
- 统一标签命名规范
- 批量整理文献分类

**使用方法**：

```bash
python tag_cleaner.py
```

---

### 3. `prompt.md` - AI 分析模板 📋

**这是 AI 的"大脑"！** 定义了如何深度分析论文。

**8 大分析维度**：

1. 📊 **核心总览** - 一句话总结、分类、基本信息
2. 🔬 **研究问题与论证** - 问题、路径、亮点
3. 📚 **学术背景** - 关键文献、研究脉络
4. 🔧 **数据与方法** - 数据表格、方法细节
5. ⚖️ **批判视角** - 不足、改进建议
6. 🚀 **未来展望** - 研究方向、基金机会
7. 🎓 **教学应用** - 课程案例、讨论问题
8. 🌍 **通俗解读** - 高中生也能懂的版本

**特点**：

- 📝 结构化 Markdown 格式
- ✅ 质量自检清单
- 🔗 强调引用页码，防止幻觉
- 📊 支持 JSON 输出（可选）

---

## 🚀 快速开始

### 📋 前置要求

- 🐍 Python 3.7+
- 📚 Zotero 账户（免费注册：https://www.zotero.org/）
- 🤖 Google Gemini API Key（免费获取：https://makersuite.google.com/app/apikey）

### ⚡ 5 分钟快速上手

#### 1️⃣ 克隆仓库

```bash
git clone https://github.com/yourusername/zotero-ai-reader.git
cd zotero-ai-reader
```

#### 2️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

#### 3️⃣ 配置密钥

```bash
# 复制配置模板
cp config.example.py config.py

# 编辑 config.py，填入你的 API 密钥
# 需要配置：
# - Zotero Library ID 和 API Key
# - Gemini API Key
# - PDF 存储路径
```

#### 4️⃣ 运行程序

```bash
# 测试模式（推荐首次使用）
# 在 config.py 中设置：TEST_MODE = True, TEST_LIMIT = 3
python reader.py
```

**🎉 完成！** 你的第一篇论文已经被 AI 分析并保存到 Zotero 了！

---

## ⚙️ 配置说明

### 🔐 安全配置（重要！）

为了保护你的 API 密钥，我们使用了配置文件分离机制：

1. **复制模板**：

   ```bash
   cp config.example.py config.py
   ```
2. **编辑配置**：
   打开 `config.py`，填入你的真实配置：

   ```python
   LIBRARY_ID = '你的库ID'
   API_KEY = '你的Zotero_API密钥'
   AI_API_KEY = '你的Gemini_API密钥'
   ZOTERO_STORAGE_PATH = r'你的PDF路径'
   ```
3. **自动保护**：

   - ✅ `config.py` 已在 `.gitignore` 中
   - ✅ 不会被提交到 Git
   - ✅ 你的密钥安全无忧

### 📝 配置项说明

| 配置项                     | 说明             | 示例                                                             |
| -------------------------- | ---------------- | ---------------------------------------------------------------- |
| `LIBRARY_ID`             | Zotero 库 ID     | `'4084102'`                                                    |
| `API_KEY`                | Zotero API 密钥  | 在[Zotero 设置](https://www.zotero.org/settings/keys) 获取          |
| `AI_API_KEY`             | Gemini API 密钥  | 在[Google AI Studio](https://makersuite.google.com/app/apikey) 获取 |
| `ZOTERO_STORAGE_PATH`    | PDF 存储路径     | `r'C:\Users\Name\Zotero\storage'`                              |
| `TARGET_COLLECTION_PATH` | 目标集合（可选） | `"0 2025/12"` 或 `None`                                      |
| `TEST_MODE`              | 测试模式         | `True` / `False`                                             |

---

## 🔧 使用技巧

### 💡 主程序技巧

#### 🧪 测试模式

首次使用建议开启测试模式：

```python
TEST_MODE = True
TEST_LIMIT = 3  # 只处理前 3 篇
```

#### 📁 集合筛选

只处理特定集合的文献：

```python
TARGET_COLLECTION_PATH = "0 2025/12"  # 集合路径
```

#### 🔍 类型过滤

只处理特定类型的文献：

```python
ITEM_TYPES_TO_PROCESS = ['journalArticle', 'conferencePaper']
```

#### 🔄 重新分析

如果想重新分析某篇文献：

1. 在 Zotero 中删除该文献的 `gemini_read` 标签
2. 重新运行程序

### 🧹 标签清理技巧

#### 💾 备份优先

清理前建议备份 Zotero 库（Zotero 菜单 → 文件 → 导出库）

#### 🎯 精确配置

只保留真正需要的标签：

```python
KEEP_TAGS = ["精读", "重要", "可行", "参考"]
```

---

## 📊 工作流程示例

### 场景：批量分析 50 篇论文

```bash
# 1. 配置集合路径
TARGET_COLLECTION_PATH = "待读论文/2025年1月"

# 2. 开启测试模式（先测试 3 篇）
TEST_MODE = True
TEST_LIMIT = 3

# 3. 运行程序
python reader.py

# 4. 检查结果，确认无误后关闭测试模式
TEST_MODE = False

# 5. 再次运行，处理全部文献
python reader.py
```

**预期结果**：

- ✅ 50 篇论文全部分析完成
- ✅ 每篇都有详细的结构化笔记
- ✅ 所有文献都标记了 `gemini_read` 标签
- ⏱️ 总耗时约 2-3 小时（取决于 API 响应速度）

---

## ⚠️ 注意事项

### 🔒 API 限制

- **Zotero API**：有频率限制，程序已内置延迟机制（0.5-2 秒）
- **Gemini API**：有调用次数和 Token 限制，注意控制使用量
- 💡 **建议**：大批量处理时，可以分批进行

### 📁 PDF 路径

- 确保 `ZOTERO_STORAGE_PATH` 路径正确
- 如果 PDF 不在标准位置，程序会尝试智能搜索
- 💡 **提示**：程序支持多种 PDF 搜索策略，通常能找到文件

### 🏷️ 标签管理

- 已处理的文献会自动添加 `gemini_read` 标签
- 已处理的文献会被自动跳过
- 💡 **技巧**：删除标签可以重新分析

### 💾 笔记保存

- 笔记保存为文献的子项（在 Zotero 中可见）
- 笔记标题自动提取自"一句话总结"
- 💡 **注意**：确保 Zotero API Key 有"创建笔记"权限

---

## 🐛 常见问题

### ❓ 找不到 PDF 文件？

**A**:

1. 检查 `ZOTERO_STORAGE_PATH` 路径是否正确
2. 程序会自动尝试多种搜索策略
3. 如果还是找不到，可以手动检查 PDF 文件名是否匹配

### ❓ API 调用失败？

**A**:

1. 检查 API 密钥是否正确
2. 确认 Zotero API Key 有**写入权限**（包括创建笔记）
3. 检查网络连接是否正常
4. 查看错误信息，可能是 API 限制或权限问题

### ❓ 笔记保存失败？

**A**:

1. 确保 Zotero API Key 有"创建笔记"权限
2. 检查网络连接
3. 查看控制台输出的详细错误信息

### ❓ 如何重新分析已处理的文献？

**A**:

1. 在 Zotero 中找到该文献
2. 删除 `gemini_read` 标签
3. 重新运行程序

### ❓ 处理速度慢？

**A**:

- AI 分析每篇论文需要 30-120 秒
- 程序已内置延迟避免触发 API 限制
- 大批量处理建议分批进行或使用测试模式先验证

---

## 📦 依赖包

```
pyzotero>=2.0.0      # Zotero API 客户端
google-genai>=0.2.0  # Google Gemini API
PyMuPDF>=1.23.0      # PDF 文本提取
markdown>=3.4.0      # Markdown 转 HTML
```

---

## 🎓 使用示例

### 示例 1：快速了解新领域

**场景**：你刚进入一个新研究领域，需要快速理解 20 篇核心论文。

**操作**：

1. 在 Zotero 中创建集合"新领域核心论文"
2. 添加 20 篇论文到该集合
3. 配置 `TARGET_COLLECTION_PATH = "新领域核心论文"`
4. 运行程序
5. 等待 1-2 小时，所有论文分析完成
6. 在 Zotero 中浏览生成的笔记，快速掌握领域核心

**结果**：每篇论文都有详细的分析笔记，包括研究问题、方法、结果、不足等，帮你快速建立领域知识框架。

### 示例 2：文献综述准备

**场景**：准备写文献综述，需要系统分析 100 篇相关论文。

**操作**：

1. 将所有相关论文添加到 Zotero 集合
2. 分批处理（每次 20-30 篇）
3. 使用 `ITEM_TYPES_TO_PROCESS = ['journalArticle']` 只处理期刊论文
4. 处理完成后，在 Zotero 中按标签筛选，查看所有笔记
5. 根据笔记中的"研究问题"和"核心亮点"部分，快速组织综述结构

**结果**：系统化的文献分析，每篇论文的关键信息一目了然，大大提升综述写作效率。

---

## 🤝 贡献

欢迎贡献代码、提出建议、报告问题！

### 如何贡献

1. 🍴 Fork 本项目
2. 🌿 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 💾 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 📤 推送到分支 (`git push origin feature/AmazingFeature`)
5. 🔀 开启 Pull Request

### 贡献方向

- 🐛 Bug 修复
- ✨ 新功能开发
- 📝 文档改进
- 🎨 UI/UX 优化
- 🌍 多语言支持

---

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Zotero](https://www.zotero.org/) - 优秀的文献管理工具
- [Google Gemini](https://ai.google.dev/) - 强大的 AI 模型
- [pyzotero](https://github.com/urschrei/pyzotero) - Zotero API 客户端

---

## 📧 联系方式

- 🐛 **问题反馈**：[GitHub Issues](https://github.com/yourusername/zotero-ai-reader/issues)
- 💬 **讨论交流**：[GitHub Discussions](https://github.com/yourusername/zotero-ai-reader/discussions)
- 📧 **邮件联系**：licm@scut.com

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**

Made with ❤️ by the community

</div>
