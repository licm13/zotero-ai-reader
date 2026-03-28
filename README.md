# 🤖 Zotero AI Reader & Organizer

<div align="center">

**让 AI 帮你读论文 + 双轨自动分类，解放你的时间！**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zotero](https://img.shields.io/badge/Zotero-API-orange.svg)](https://www.zotero.org/)

*一个强大的 Zotero 文献自动化工具，使用 AI 深度理解论文并自动分类到双轨集合结构*

[✨ 特性](#-核心特性) • [🚀 快速开始](#-快速开始) • [📖 使用指南](#-使用指南) • [💡 使用场景](#-使用场景)

</div>

---

## 🌟 为什么需要它?

还在为堆积如山的论文发愁吗？还在逐字逐句地阅读每一篇文献吗？还在手动整理文献到不同文件夹吗？

**Zotero AI Reader** 来拯救你！🎉

这个工具可以：

- 📚 **自动读取** Zotero 文献库中的 PDF
- 🧠 **AI 深度分析** 论文的核心内容
- 📝 **生成结构化笔记** 直接保存到 Zotero
- 🗂️ **双轨智能分类** 同时归档到学科分类 + 科学问题分类
- 👤 **个性化画像** 基于阅读历史动态调整分类策略
- ⚡ **批量处理** 整个文献库或指定集合
- 🏷️ **智能标记** 已处理的文献，避免重复工作

**想象一下**：早上起床，发现昨晚的 50 篇论文已经被 AI 分析完毕，每篇都有详细的结构化笔记，并且自动归类到 "📚 Archive/Hazards/Flash Drought" 和 "💡 Idea Lab/Mechanism/Abrupt Transitions" 两个互补的结构中，而你只需要喝杯咖啡，浏览一下重点！☕

---

## ✨ 核心特性

### 🎯 智能论文分析

- **8 大分析维度**：从核心总览到通俗解读，全方位理解论文
- **结构化输出**：研究问题、论证路径、数据方法、批判视角一应俱全
- **防幻觉设计**：强调引用页码和图表编号，确保信息准确

### 🗂️ 双轨自动分类系统 (NEW!)

**核心理念："走两条腿"** - 一篇论文同时归入两个分类体系

#### Track A (📚 Archive): 学科分类

标准的学科/方法论分类，便于系统性检索：

- **Processes**: ET, Runoff, Soil Moisture, Cryosphere...
- **Hazards**: Drought, Flood, DFA, Extremes...
- **Methodology**: Remote Sensing, Deep Learning, Triple Collocation...
- **Applications**: Water Management, Climate Impact...

#### Track B (💡 Idea Lab): 问题驱动分类

基于科学问题和物理机制的"品味驱动"分类：

- **Mechanism**: Abrupt Transitions, Land-Atmosphere Coupling, Thresholds...
- **Data Philosophy**: Signal Purification, Scale Issues, Multi-Source Integration...
- **Modeling**: Physics-Informed AI, Causal Inference, Hybrid Modeling...
- **Dynamics**: Non-linearity, Tipping Points, Rapid Onset...
- **Coupling**: Vegetation-Water, Energy-Water, Human-Nature Systems...

**优势**：

- ✅ **互补性**: 既满足传统检索需求，又激发科研灵感
- ✅ **个性化**: 基于你的阅读历史动态调整
- ✅ **一键双归**: 利用 Zotero 多集合特性，一篇论文同时出现在两处

### 🧠 智能画像系统 (NEW!)

- **动态品味提取**：分析最近 20 篇阅读论文，理解你的当前关注点
- **自动适配分类**：根据你的研究品味调整 AI 分类逻辑
- **持续进化**：定期运行 profiler.py 更新画像，分类越用越聪明

### 🔄 自动化工作流

- **零手动操作**：配置一次，自动处理整个文献库
- **智能去重**：自动跳过已处理的文献
- **批量处理**：支持按集合、类型筛选，灵活控制
- **Token 优化**：本地缓存 + 精简提示词，降低 API 成本

### 🛡️ 企业级错误处理 (NEW!)

- **全面的错误验证**：所有 API 响应和数据结构在使用前都经过验证
- **清晰的错误消息**：每个错误都有详细的中英文说明和建议解决方案
- **智能重试机制**：自动识别暂时性错误（超时、网络中断、速率限制）并使用指数退避重试
- **优雅降级**：部分失败时继续处理（如 PDF 单页读取失败）而不是完全崩溃
- **详细的错误分类**：区分权限错误、网络错误、数据格式错误等，便于快速定位问题
- **强大的数据验证**：
  - PDF 文件：完整性检查、权限验证、页数验证、内容验证
  - API 响应：结构验证、必需字段检查、类型验证
  - JSON 数据：Schema 验证、字段类型检查、默认值回退
  - 配置文件：必需属性检查、值验证、语法错误提示

### 🎨 完美集成

- **无缝对接 Zotero**：笔记直接保存为文献子项
- **智能 PDF 搜索**：多种策略自动定位 PDF 文件
- **标签管理**：自动添加处理标记，便于管理

---

## 💡 使用场景

### 📖 研究生/博士生

- **文献综述**：快速理解大量相关论文，提取关键信息
- **开题准备**：系统分析领域现状，发现研究缺口
- **论文写作**：快速回顾已读文献，引用关键观点
- **主题整理**：双轨自动分类到学科 + 问题两个维度

### 👨‍🏫 研究人员

- **领域追踪**：定期批量分析新发表的论文
- **灵感激发**：通过 Idea Lab 发现论文之间的内在联系
- **基金申请**：系统梳理相关研究，支撑申请材料
- **知识库构建**：自动建立双轨清晰的文献知识库

### 📚 学术爱好者

- **知识管理**：建立结构化的文献知识库
- **快速学习**：高效理解新领域的核心论文
- **笔记整理**：自动生成标准化笔记，便于检索

---

## 📁 项目结构

```
zotero-ai-reader/
├── student_pack/                # 🎓 学生独立分发包（仅小米 MIMO + 图形界面，见 student_pack/README.md）
│   ├── gui_mimo_student.py      # 学生版 GUI 入口
│   ├── reader_mimo_student.py   # 学生版阅读核心（无 Gemini）
│   ├── config.example.py        # 配置模板（复制为 config.py）
│   ├── prompt.md                # 与主项目一致的提示词模板
│   ├── requirements.txt         # 精简依赖（无 google-genai）
│   └── README.md                # 学生使用说明
├── reader.py                    # 🎯 Step 1: AI 论文分析工具 (支持 Gemini/小米 MIMO 双模型)
├── reader_gui.py                # 🖥️ 完整版图形界面（Gemini / MIMO 可选）
├── profiler.py                  # 👤 Step 2: 研究品味提取器
├── organizer.py                 # 🗂️ Step 3: 双轨智能分类工具 (MAIN!)
├── tag_cleaner.py               # 🧹 标签清理工具
├── keyword_classifier.py        # 🔍 关键词分类分析工具
├── config_loader.py             # 🔧 配置加载工具（交互式选择config.py）
├── prompt.md                    # 📋 AI 分析提示词模板
├── config.example.py            # ⚙️ 配置文件模板（⚠️ 请复制为 config.py）
├── config.py                    # ⚙️ 实际配置文件（⚠️ 包含敏感信息，不在Git中）
├── requirements.txt             # 📦 依赖包列表
├── collections_cache.json       # 💾 集合缓存（自动生成，已加入.gitignore）
├── user_profile.json            # 👤 用户画像（自动生成，已加入.gitignore）
├── keyword_analysis/             # 📊 关键词分析结果目录
│   ├── keyword_categories.json  # 关键词分类结果（自动生成）
│   ├── keyword_statistics.json  # 统计信息（自动生成）
│   ├── keyword_top20.json       # Top20关键词（自动生成）
│   ├── keyword_top20_report.txt # Top20报告（自动生成）
│   └── keyword_top20_analyzer.py  # Top20分析工具脚本
├── analysis_json/               # 📊 深度分析结果目录（自动生成）
│   ├── *_deep_analysis_results.json      # 单篇论文深度分析结果
│   └── *_research_opportunities_report.json  # 全局研究机会报告
└── README.md                    # 📖 本文件
```

**注意**：

- `config.py` 文件包含敏感信息（API密钥），已在 `.gitignore` 中，不会被提交到Git
- 所有自动生成的文件（缓存、分析结果等）也已加入 `.gitignore`
- 首次使用前，请复制 `config.example.py` 为 `config.py` 并填入您的配置

### 🎓 学生分发包 `student_pack/`

若只需向学生提供**小米 MIMO** 单模型、**图形界面**及**固定提示词模板**，可直接打包或分享 **`student_pack/`** 文件夹：

- **入口**：在 `student_pack` 目录执行 `python gui_mimo_student.py`（详见该目录内 [student_pack/README.md](student_pack/README.md)）。
- **依赖更少**：`requirements.txt` 不含 `google-genai`；无需完整仓库中的 `config_loader.py` 等。
- **命令行备用**：在同目录准备好 `config.py` 后，可运行 `python reader_mimo_student.py --cli`。

完整功能（Gemini、双轨 `organizer.py` 等）仍以仓库根目录脚本为准。

---

## 📋 脚本功能总览

| 脚本名称                      | 主要功能        | 输入                    | 输出                  | 使用频率           |
| ----------------------------- | --------------- | ----------------------- | --------------------- | ------------------ |
| `reader.py`                 | AI论文分析      | Zotero文献库 + PDF文件  | AI阅读报告笔记        | 首次分析时         |
| `profiler.py`               | 研究品味提取    | 已分析的论文笔记        | `user_profile.json` | 定期更新（如每周） |
| `organizer.py`              | 双轨智能分类    | 已分析的论文 + 用户画像 | 分类到集合 + 分析报告 | 每次分析后         |
| `tag_cleaner.py`            | 标签清理        | Zotero文献库            | 清理后的标签          | 按需使用           |
| `keyword_classifier.py`     | 关键词聚类分析  | 所有论文的AI笔记        | 关键词分类结果        | 按需使用           |
| `keyword_top20_analyzer.py` | Top20关键词提取 | 关键词分类结果          | Top20关键词报告       | 按需使用           |
| `config_loader.py`          | 配置加载        | 命令行参数或交互选择    | 配置对象              | 所有脚本自动调用   |

**典型工作流程**：

1. **首次使用**：运行 `reader.py` → `profiler.py` → `organizer.py`
2. **持续使用**：定期运行 `reader.py`（新论文）→ `organizer.py`（分类）
3. **定期更新**：每周运行一次 `profiler.py`（更新画像）
4. **按需分析**：运行 `keyword_classifier.py` 和 `keyword_top20_analyzer.py`（关键词分析）

---

## 🎯 核心文件说明

### 1. `reader.py` - 论文分析工具 🚀

**这是第一步！** 它会自动分析你的 Zotero 文献。

**工作流程**：

```
📥 连接 Zotero → 🔍 查找 PDF → 📖 提取文本 → 🤖 AI 分析 → 💾 保存笔记
```

**核心能力**：

- ✅ 双AI引擎支持（启动时交互式选择使用 Google Gemini 还是 小米 MIMO，支持配置文件设定默认选项）
- ✅ 智能 PDF 搜索（支持多种匹配策略：file_key、文件名关键词、递归搜索）
- ✅ 批量处理（支持集合筛选、类型过滤、测试模式）
- ✅ 自动去重（通过 `gemini_read` 标签识别已处理文献）
- ✅ 错误恢复（完善的异常处理机制，包括PDF验证、API重试）
- ✅ 交互式路径选择（Zotero Storage路径可选择、自动搜索或手动输入）
- ✅ 笔记自动保存（Markdown转HTML，提取一句话总结作为标题）

**快速上手**：

```bash
# 1. 配置 config.py（见下方）
# 2. 运行程序
python reader.py
```

---

### 2. `profiler.py` - 研究品味提取器 👤 (NEW!)

**第二步（可选但推荐）！** 分析你的阅读历史，生成个性化画像。

**工作流程**：

```
📥 获取最近 20 篇已读文献 → 📝 提取 AI 笔记 → 🧠 分析品味 → 💾 保存画像
```

**核心能力**：

- ✅ **动态品味识别**：分析最近20篇已读论文，理解当前研究关注点
- ✅ **趋势发现**：识别新兴兴趣方向和方法论变化
- ✅ **个性化建议**：基于实际阅读历史推荐 Idea Lab 分类结构
- ✅ **持续进化**：定期更新画像，分类越用越精准
- ✅ **AI驱动分析**：使用Gemini AI分析阅读模式，生成结构化画像
- ✅ **多维度分析**：关注研究主题、方法论、科学问题等多个维度

**生成的画像包含**：

```json
{
  "base_info": {
    "name": "Your Name",
    "field": "Your Research Field",
    "core_interests": ["Interest1", "Interest2", "Interest3"]
  },
  "dynamic_analysis": {
    "summary": "当前关注点总结...",
    "focus_areas": ["具体研究方向1", "方向2"],
    "idea_lab_suggestions": [...]
  }
}
```

**使用方法**：

```bash
# 在运行 organizer.py 之前，先生成画像
python profiler.py
```

---

### 3. `organizer.py` - 双轨智能分类工具 🗂️ (MAIN!)

**第三步！这是主力脚本！** 自动将论文整理到双轨集合结构。

**工作流程**：

```
📥 获取已分析文献 → 📝 提取笔记关键词 → 👤 加载画像 → 🧠 AI 双轨分类 → 🗂️ 同时添加到两个集合
```

**核心能力**：

- ✅ **双轨分类**：一篇论文同时归入 Archive + Idea Lab 两个分类体系
- ✅ **画像驱动**：读取 `user_profile.json` 定制分类逻辑，个性化分类结果
- ✅ **深度笔记解析**：提取完整的AI阅读报告，包括研究问题、核心亮点、主要不足、未来工作方向、数据表等结构化信息
- ✅ **关键词精准度评估**：AI分析当前关键词准确性，提供改进建议和评估理由
- ✅ **论文关联分析**：发现同批次论文之间的潜在关联（基于研究问题、方法、关键词、数据源）
- ✅ **创新点洞察**：基于论文内容思考新的研究方向和机会
- ✅ **全局分析报告**：汇总所有论文，生成跨论文研究机会报告和数据景观分析
- ✅ **分析结果保存**：将深度分析结果保存到JSON文件（`analysis_json/`目录），便于后续查看和分析
- ✅ **Token 优化**：本地缓存 + 精简提示词，节省 API 成本
- ✅ **批量处理**：一次处理多篇论文（默认 5 篇/批，可配置）
- ✅ **测试模式**：DRY_RUN 模式先预览再执行，避免误操作
- ✅ **自动创建**：不存在的集合路径自动创建（支持多层级嵌套）
- ✅ **子集合递归**：支持递归处理目标集合的所有子集合

**双轨分类体系示例**：

```
📚 Archive (学科分类)                💡 Idea Lab (问题驱动)
├── Processes                        ├── Mechanism
│   ├── Evapotranspiration (ET)     │   ├── Abrupt Transitions/Phase Change
│   ├── Runoff & Streamflow         │   ├── Land-Atmosphere Coupling
│   └── Soil Moisture               │   └── Threshold Behavior
├── Hazards                          ├── Data Philosophy
│   ├── Drought/Flash Drought       │   ├── Signal Purification/Uncertainty
│   ├── Flood                        │   └── Scale Issues
│   └── Compound Events/DFA         ├── Modeling
└── Methodology                      │   ├── Physics-Informed AI
    ├── Remote Sensing/Retrieval    │   ├── Causal Inference
    ├── Deep Learning (LSTM_CNN)    │   └── Hybrid Modeling
    └── Triple Collocation           └── Dynamics
                                         ├── Tipping Points
                                         └── Drought-Flood Transitions
```

**使用方法**：

```bash
# 1. 先运行 reader.py 分析论文
python reader.py

# 2. (可选) 运行 profiler.py 生成画像
python profiler.py

# 3. 运行 organizer.py 双轨分类
python organizer.py
```

**重要配置**：

```python
DRY_RUN = True              # 测试模式（推荐首次使用）
BATCH_SIZE = 5              # 每批处理论文数
TARGET_COLLECTION_PATH = None  # 指定处理某个集合（如 "00_Inbox"）
```

**深度分析输出格式**：

每篇论文的分析结果保存在 `analysis_json/{collection}_deep_analysis_results.json` 文件中，包含：

```json
{
  "paper_title": {
    "archive": "📚 Archive/Category/Subcategory",
    "idea": "💡 Idea Lab/Category/Subcategory",
    "keyword_assessment": {
      "current": "当前关键词列表",
      "suggested": "建议改进的关键词（如果需要）",
      "reason": "评估理由和改进建议"
    },
    "related_papers": ["相关论文1标题", "相关论文2标题"],
    "innovation_insights": [
      "创新点1：可以做什么新研究",
      "创新点2：可以填补什么空白"
    ]
  }
}
```

**分析能力矩阵**：

| 功能             | 状态 | 完成度         |
| ---------------- | ---- | -------------- |
| 读取论文笔记     | ✅   | 100%           |
| 论文双轨分类     | ✅   | 100%           |
| 关键词精准度评估 | ✅   | 100%           |
| 论文关联分析     | ⚠️ | 60% (批次内)   |
| 创新点思考       | ✅   | 80% (单篇级别) |
| 归纳整理         | ✅   | 100%           |

**未来增强计划**：

- 🔄 全局论文关联分析（跨批次、跨集合）
- 📊 全局创新点汇总报告
- 🌐 跨论文研究机会发现
- 📈 研究趋势分析和热点识别

---

### 4. `tag_cleaner.py` - 标签清理工具 🧹

**文献库标签太多太乱？** 这个工具帮你一键清理！

**功能**：

- 🎯 批量清理标签，只保留重要标签（在 `config.py` 中配置 `KEEP_TAGS`）
- 🔍 支持按文献类型过滤（通过 `ITEM_TYPES_TO_PROCESS` 配置）
- 📊 实时显示清理进度和统计
- ✅ 自动跳过无标签的文献
- 🔄 支持分页获取，处理大型文献库

**配置**（在 `config.py` 中）：

```python
KEEP_TAGS = ["精读", "重要", "可行", "参考"]  # 要保留的标签列表
ITEM_TYPES_TO_PROCESS = None  # None表示处理所有类型，或指定如 ['journalArticle']
```

**使用方法**：

```bash
python tag_cleaner.py
```

**输出**：

- 实时显示清理进度和统计信息
- 最终统计：已处理、已清理、已跳过、错误数量

### 5. `keyword_classifier.py` - 关键词分类分析工具 🔍

**从Zotero库中提取所有文献的AI笔记关键词，进行智能聚类和分类分析。**

**功能**：

- ✅ 自动检索所有文献的"AI 深度阅读报告"笔记（支持模糊匹配）
- ✅ 提取Keywords关键词部分（支持多种格式）
- ✅ 关键词归一化（去重、同义词识别、缩写展开）
- ✅ 基于TF-IDF向量化和余弦相似度的语义分析
- ✅ 基于共现关系的关联分析
- ✅ 层次聚类算法（支持自定义相似度阈值）
- ✅ 支持多标签分类（一个关键词可属于多个类目）
- ✅ 生成层次化分类结构和统计报告
- ✅ 完善的错误处理和重试机制

**使用方法**：

```bash
python keyword_classifier.py
```

**配置参数**（可在脚本中修改）：

- `SEMANTIC_SIMILARITY_THRESHOLD = 0.6` - 语义相似度阈值
- `STRING_SIMILARITY_THRESHOLD = 0.8` - 字符串相似度阈值
- `MIN_CLUSTER_SIZE = 2` - 最小聚类大小
- `DEBUG_MODE = True` - 是否显示详细调试信息

**输出文件**（保存在 `keyword_analysis/` 目录）：

- `keyword_categories.json` - JSON格式的分类结果（包含类别和关键词分配）
- `keyword_report.txt` - 文本格式的详细报告（包含统计和多标签列表）
- `keyword_statistics.json` - 统计信息（总文献数、唯一关键词数、分类数等）

### 6. `keyword_top20_analyzer.py` - 关键词Top20分析工具 📊

**从关键词分类结果中提取Top20关键词，使用Gemini AI进行智能合并和规范化。**

**功能**：

- ✅ 从 `keyword_categories.json` 提取所有关键词
- ✅ 拆分关键词短语（处理连字符、斜杠等分隔符）
- ✅ 统计关键词频次
- ✅ 使用Gemini AI识别同义词并智能合并
- ✅ 生成Top20关键词报告（JSON和文本格式）

**使用方法**：

```bash
cd keyword_analysis
python keyword_top20_analyzer.py
```

**前置要求**：

- 需要先运行 `keyword_classifier.py` 生成 `keyword_categories.json` 和 `keyword_statistics.json`

**输出文件**：

- `keyword_top20.json` - JSON格式的Top20关键词（包含合并规则和统计信息）
- `keyword_top20_report.txt` - 文本格式的详细报告

### 7. `config_loader.py` - 配置加载工具 🔧

**所有脚本的统一配置加载模块，提供灵活的配置文件选择机制。**

**功能**：

- ✅ 支持命令行参数指定配置文件：`--config /path/to/config.py`
- ✅ 交互式选择界面（4种方式）
- ✅ 自动搜索配置文件（当前目录、脚本目录、项目根目录）
- ✅ GUI文件浏览器选择（需要tkinter支持）
- ✅ 配置文件验证（检查必需属性和值有效性）

**用户通常不需要直接使用**，所有脚本都会自动调用此模块加载配置。

**交互式选择选项**：

1. 使用建议位置（如果自动找到config.py）
2. 手动输入config.py的完整路径
3. 使用GUI文件浏览器选择
4. 自动搜索配置文件

**配置验证**：

- 检查必需属性：`LIBRARY_ID`, `API_KEY`, `LIBRARY_TYPE`, `AI_API_KEY`
- 验证属性值不为空
- 验证 `LIBRARY_TYPE` 值有效性（'user' 或 'group'）

---

## 🚀 快速开始

### 📋 前置要求

- 🐍 Python 3.7+
- 📚 Zotero 账户（免费注册：https://www.zotero.org/）
- 🤖 Google Gemini API Key（选用，免费获取：https://makersuite.google.com/app/apikey）
- 🟠 **小米 MIMO API Key**（选用，前往 [小米 MIMO 开放平台](https://platform.xiaomimimo.com/) 注册。**注意：需要完成实名认证并进行预充值后才能正常调用 API**）

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

**💡 提示**：运行脚本时，如果没有找到config.py文件，会弹出交互式选择界面，你可以：

- 选择自动搜索（在当前目录或项目根目录查找）
- 手动输入config.py的路径
- 使用GUI文件浏览器选择（需要tkinter支持）
- 使用命令行参数：`python reader.py --config /path/to/config.py`

**⚠️ 安全提示**：

- `config.py` 文件包含敏感信息（API密钥），已在 `.gitignore` 中
- 请勿将 `config.py` 提交到版本控制系统
- 如果使用Git，请确保 `.gitignore` 包含 `config.py`

#### 4️⃣ 运行完整工作流

```bash
# Step 1: 分析论文（推荐首次使用测试模式）
# 在 config.py 中设置：TEST_MODE = True, TEST_LIMIT = 3
python reader.py

# Step 2: 生成研究品味画像
python profiler.py

# Step 3: 双轨自动分类（推荐首次使用 DRY_RUN 模式）
# 在 organizer.py 中确保：DRY_RUN = True
python organizer.py

# Step 4: 检查结果无误后，关闭测试模式重新运行
# config.py: TEST_MODE = False
# organizer.py: DRY_RUN = False
python reader.py
python profiler.py
python organizer.py
```

**🎉 完成！** 你的论文已经被 AI 分析并自动分类到双轨结构了！

---

## ⚙️ 配置说明

### 🔐 安全配置（重要！）

**⚠️ 所有脚本都统一从 `config.py` 文件读取API密钥，请勿在代码中硬编码密钥！**

为了保护你的 API 密钥，我们使用了配置文件分离机制和交互式配置选择：

1. **复制模板**：

   ```bash
   cp config.example.py config.py
   ```
2. **编辑配置**：
   打开 `config.py`，填入你的真实配置：

   ```python
   # --- Zotero 设置 ---
   LIBRARY_ID = '你的库ID'                    # 在 Zotero 设置页面获取
   API_KEY = '你的Zotero_API密钥'             # 需要读写权限
   LIBRARY_TYPE = 'user'                      # 'user' 或 'group'
   ZOTERO_STORAGE_PATH = r'你的PDF存储路径'

   # --- AI 模型设置 ---
   # 1. Gemini 配置
   AI_API_KEY = '你的Gemini_API密钥'          # 在 Google AI Studio 获取
   AI_MODEL = 'gemini-3.1-flash-lite-preview'

   # 2. XiaoMi MIMO 配置
   XiaoMi_API_KEY = '你的XiaoMi_API密钥'      # 在小米 MIMO 开放平台获取
   XIAOMI_MODEL = 'mimo-v2-pro'
   
   DEFAULT_AI_PROVIDER = None                 # 'gemini'，'xiaomi'，或 None (交互式选择)
   ```
3. **运行脚本时的配置选择**：

   当你运行任何脚本时，如果没有找到config.py，会弹出**交互式选择界面**：

   ```bash
   python reader.py
   # 或指定配置文件路径
   python reader.py --config /path/to/config.py
   ```

   **交互式界面提供以下选项**：

   - **选项1**：使用建议位置（如果自动找到config.py）
   - **选项2**：手动输入config.py的完整路径
   - **选项3**：使用GUI文件浏览器选择（需要tkinter支持）
   - **选项4**：自动搜索（在当前目录、脚本目录、项目根目录中搜索）
4. **自动保护**：

   - ✅ `config.py` 已在 `.gitignore` 中
   - ✅ 不会被提交到 Git
   - ✅ 所有脚本统一从 `config.py` 读取配置
   - ✅ 代码中不会硬编码任何真实密钥
   - ✅ 支持灵活指定配置文件位置
   - ✅ 你的密钥安全无忧
5. **配置使用说明**：

   - **所有脚本**（`reader.py`, `profiler.py`, `organizer.py`, `tag_cleaner.py`, `keyword_classifier.py`, `keyword_top20_analyzer.py`）都使用 `config_loader.py` 统一加载配置
   - 支持命令行参数：`--config /path/to/config.py`
   - 支持交互式选择配置文件位置
   - 如果未找到 `config.py`，脚本会提示交互式选择或退出
   - 不要将 `config.py` 文件提交到版本控制系统

### 📝 配置项说明

| 配置项                     | 说明             | 示例                                                             |
| -------------------------- | ---------------- | ---------------------------------------------------------------- |
| `LIBRARY_ID`             | Zotero 库 ID     | `'4084102'`                                                    |
| `API_KEY`                | Zotero API 密钥  | 在[Zotero 设置](https://www.zotero.org/settings/keys) 获取          |
| `AI_API_KEY`             | Gemini API 密钥  | 在[Google AI Studio](https://makersuite.google.com/app/apikey) 获取 |
| `ZOTERO_STORAGE_PATH`    | PDF 存储路径     | `r'C:\Users\Name\Zotero\storage'`                              |
| `TARGET_COLLECTION_PATH` | 目标集合（可选） | `"0 2025/12"` 或 `None`                                      |
| `TEST_MODE`              | 测试模式         | `True` / `False`                                             |

### 🗂️ 自定义双轨分类体系

在 `organizer.py` 中修改 `PREFERRED_TAXONOMY` 变量，自定义分类逻辑。每个 Track 包含多个分类和子分类，系统会自动创建相应的集合结构。

**💡 提示**：运行 `profiler.py` 后，会基于你的阅读历史给出个性化的 Idea Lab 建议，帮助你优化分类体系！

---

## 🔧 使用技巧

### 💡 完整工作流程

#### 🎓 场景：批量处理 50 篇新下载的论文

**Step 1: 分析论文**

```bash
# 1. 配置集合路径
TARGET_COLLECTION_PATH = "00_Inbox"

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

**Step 2: 生成研究画像**

```bash
# 基于已分析的论文生成画像
python profiler.py
```

**Step 3: 双轨分类**

```bash
# 1. 在 organizer.py 中设置
DRY_RUN = True  # 测试模式
TARGET_COLLECTION_PATH = "00_Inbox"  # 处理同一个集合

# 2. 运行分类（预览）
python organizer.py

# 3. 查看预览结果，确认无误后
DRY_RUN = False

# 4. 正式分类
python organizer.py
```

**预期结果**：

- ✅ 50 篇论文全部分析完成，每篇都有详细笔记
- ✅ 生成个性化研究画像
- ✅ 每篇论文同时归入两个集合：
  - 📚 Archive: 如 "Archive/Hazards/Flash Drought"
  - 💡 Idea Lab: 如 "Idea Lab/Mechanism/Abrupt Transitions"
- ✅ 所有文献标记 `gemini_read` 和 `auto_organized` 标签

---

### 🧪 测试模式

#### reader.py 测试

首次使用建议开启测试模式：

```python
TEST_MODE = True
TEST_LIMIT = 3  # 只处理前 3 篇
```

#### organizer.py 测试

使用 DRY_RUN 模式预览分类结果：

```python
DRY_RUN = True  # 不会真的移动文献，只显示将要执行的操作
```

---

### 🔄 重新处理

**重新分析某篇文献**：

1. 在 Zotero 中删除该文献的 `gemini_read` 标签
2. 重新运行 `reader.py`

**重新分类某篇文献**：

1. 在 Zotero 中删除该文献的 `auto_organized` 标签
2. 重新运行 `organizer.py`

**更新研究画像**：

```bash
# 定期运行以保持画像最新
python profiler.py
```

---

### 💾 清除缓存

如果集合结构发生变化，删除缓存文件：

```bash
rm collections_cache.json
```

下次运行时会自动重建缓存。

---

## 📊 工作流程图

### 完整三步工作流

```
┌─────────────────────────────────────────────────────────┐
│  1. 运行 reader.py                                        │
│     - 自动读取 PDF 内容                                    │
│     - AI 生成结构化笔记                                    │
│     - 保存到 Zotero，添加 gemini_read 标签                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  2. 运行 profiler.py (可选但推荐)                          │
│     - 读取最近 20 篇已分析论文的笔记                        │
│     - AI 分析研究品味和当前关注点                           │
│     - 生成 user_profile.json                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  3. 运行 organizer.py                                     │
│     - 加载用户画像 (user_profile.json)                     │
│     - 提取笔记中的关键词                                   │
│     - AI 双轨智能分类                                      │
│     - 同时添加到 Archive + Idea Lab 集合                   │
│     - 添加 auto_organized 标签                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  4. 在 Zotero 中查看                                      │
│     - 论文按双轨分类（学科 + 问题）                        │
│     - 每篇都有 AI 笔记                                    │
│     - 既可按传统方式检索，又能按灵感探索                    │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ 注意事项

### 🔒 API 密钥安全（重要！）

**⚠️ 安全提示**：

- ✅ **所有脚本统一从 `config.py` 读取API密钥**，代码中不会硬编码真实密钥
- ✅ `config.py` 文件已在 `.gitignore` 中，不会被提交到版本控制
- ✅ 请勿在代码文件中直接写入API密钥
- ✅ 请勿将 `config.py` 文件分享给他人或提交到公开仓库
- ⚠️ 如果 `config.py` 不存在，部分脚本会使用占位符并退出，这是安全的行为

**如何检查API密钥是否泄漏**：

```bash
# 搜索代码中是否包含真实API密钥（替换为你的实际密钥）
grep -r "你的Zotero_API密钥" --include="*.py" .
grep -r "你的Gemini_API密钥" --include="*.py" .

# 搜索常见的API密钥模式（应该只有config.py包含，且config.py在.gitignore中）
grep -r "API_KEY.*=" --include="*.py" . | grep -v "config" | grep -v "YOUR_" | grep -v "example"

# 检查.gitignore是否包含config.py
grep "config.py" .gitignore
```

**安全检查清单**：

- ✅ `config.py` 在 `.gitignore` 中
- ✅ 代码中没有硬编码的真实API密钥
- ✅ `config.example.py` 中只包含占位符（YOUR_*）
- ✅ 所有脚本都通过 `config_loader.py` 统一加载配置

### 🔒 API 限制

- **Zotero API**：有频率限制，程序已内置延迟机制（0.5-2 秒）
- **Gemini API**：有调用次数和 Token 限制，注意控制使用量
- 💡 **建议**：大批量处理时，可以分批进行

### 💰 成本优化

`organizer.py` 已做以下优化以降低 API 成本：

- ✅ **本地缓存**：集合 ID 缓存到本地，减少 Zotero API 调用
- ✅ **精简提示词**：只发送分类体系，不发送所有已有集合（节省 60% Token）
- ✅ **批量处理**：一次分类多篇论文（默认 5 篇），减少 API 调用次数
- ✅ **智能画像**：用户画像仅需定期更新（如每周一次），无需每次运行

### 📁 PDF 路径

- 确保 `ZOTERO_STORAGE_PATH` 路径正确
- 如果 PDF 不在标准位置，程序会尝试智能搜索
- 💡 **提示**：程序支持多种 PDF 搜索策略，通常能找到文件

### 🏷️ 标签管理

- 已分析的文献会自动添加 `gemini_read` 标签
- 已分类的文献会自动添加 `auto_organized` 标签
- 💡 **技巧**：删除标签可以重新处理

---

## 🛡️ 错误处理

本项目实现了完善的错误处理机制，确保程序稳定运行：

- ✅ **PDF 文件验证**：完整性、格式、权限、内容验证
- ✅ **API 响应验证**：结构、类型、必需字段检查
- ✅ **智能重试**：自动识别可重试错误（超时、网络中断），指数退避策略
- ✅ **数据验证**：JSON 解析、Schema 验证、默认值回退
- ✅ **详细错误提示**：清晰的错误信息和建议解决方案

程序会自动处理各种异常情况，并提供明确的错误提示，帮助你快速定位和解决问题。

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

### ❓ 分类结果不准确？

**A**:

1. **运行 profiler.py**：生成个性化画像会显著提升分类准确度
2. 检查 AI 生成的笔记质量（关键词是否准确）
3. 在 `organizer.py` 中调整 `PREFERRED_TAXONOMY` 以更精确描述你的领域
4. 定期更新用户画像（每周运行一次 profiler.py）

### ❓ 双轨分类有什么好处？

**A**:

1. **Archive 轨**：传统学科分类，便于系统性检索（如"所有关于 ET 的论文"）
2. **Idea Lab 轨**：问题驱动分类，激发科研灵感（如"所有关于突变机制的论文"）
3. **互补性**：同一篇论文从不同视角组织，满足不同使用场景
4. **无冲突**：利用 Zotero 多集合特性，一篇论文可以同时出现在多个集合

### ❓ 如何重新分析/分类已处理的文献？

**A**:

1. 在 Zotero 中找到该文献
2. 删除相应标签（`gemini_read` 或 `auto_organized`）
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

**可选依赖**（用于GUI文件选择）：

```
tkinter              # GUI文件浏览器（通常Python自带）
```

**安装方法**：

```bash
pip install -r requirements.txt
```

**注意**：

- Python 3.7+ 必需
- 某些Linux发行版可能需要单独安装 `python3-tkinter` 以支持GUI功能

---

## 🎓 使用示例

### 示例 1：快速了解新领域

**场景**：你刚进入"Flash Drought"研究领域，需要快速理解 20 篇核心论文。

**操作**：

1. 在 Zotero 中创建集合 "00_Inbox/Flash Drought"
2. 添加 20 篇论文到该集合
3. 配置并运行：

```python
# config.py
TARGET_COLLECTION_PATH = "00_Inbox/Flash Drought"

# 运行完整工作流
python reader.py
python profiler.py
python organizer.py
```

**结果**：

- 每篇论文都有详细的 AI 笔记
- 自动双轨分类到：
  - 📚 "Archive/Hazards/Drought/Flash Drought"
  - 💡 "Idea Lab/Dynamics/Rapid Onset Events"
- 快速建立领域知识框架，既能系统检索又能探索机制

---

### 示例 2：持续跟踪研究前沿

**场景**：每周有新论文入库，需要持续处理。

**操作**：

```bash
# 创建周期性任务（Linux/Mac）
# crontab -e 添加：
0 2 * * 0 cd /path/to/zotero-ai-reader && python reader.py && python organizer.py
0 2 1 * * cd /path/to/zotero-ai-reader && python profiler.py  # 每月更新画像
```

**结果**：

- 每周日凌晨自动处理新论文
- 每月初更新研究画像
- 完全自动化，无需人工干预

---

## 🤝 贡献

欢迎贡献代码、提出建议、报告问题！

### 贡献方向

- 🐛 Bug 修复
- ✨ 新功能开发
- 📝 文档改进
- 🗂️ 更多领域的双轨分类模板
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

---

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**

Made with ❤️ by the community

</div>
