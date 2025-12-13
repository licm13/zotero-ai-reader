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
├── reader.py               # 🎯 Step 1: AI 论文分析工具
├── profiler.py             # 👤 Step 2: 研究品味提取器 (NEW!)
├── organizer.py            # 🗂️ Step 3: 双轨智能分类工具 (MAIN!)
├── tag_cleaner.py          # 🧹 标签清理工具
├── prompt.md               # 📋 AI 分析提示词模板
├── config.example.py       # ⚙️ 配置文件模板
├── requirements.txt        # 📦 依赖包列表
├── collections_cache.json  # 💾 集合缓存（自动生成）
├── user_profile.json       # 👤 用户画像（自动生成）
└── README.md               # 📖 本文件
```

---

## 🎯 核心文件说明

### 1. `reader.py` - 论文分析工具 🚀

**这是第一步！** 它会自动分析你的 Zotero 文献。

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

### 2. `profiler.py` - 研究品味提取器 👤 (NEW!)

**第二步（可选但推荐）！** 分析你的阅读历史，生成个性化画像。

**工作流程**：

```
📥 获取最近 20 篇已读文献 → 📝 提取 AI 笔记 → 🧠 分析品味 → 💾 保存画像
```

**核心能力**：

- ✅ **动态品味识别**：理解你当前的研究关注点
- ✅ **趋势发现**：识别新兴兴趣方向
- ✅ **个性化建议**：基于实际阅读历史推荐 Idea Lab 分类
- ✅ **持续进化**：定期更新，分类越用越精准

**生成的画像包含**：

```json
{
  "base_info": {
    "name": "Prof. Chengming Li",
    "field": "Hydrology, Remote Sensing",
    "core_interests": ["ET", "Flash Drought", "DFA", "Deep Learning"]
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

- ✅ **双轨分类**：一篇论文同时归入 Archive + Idea Lab
- ✅ **画像驱动**：读取 user_profile.json 定制分类逻辑
- ✅ **Token 优化**：本地缓存 + 精简提示词，节省 API 成本
- ✅ **批量处理**：一次处理多篇论文（默认 5 篇/批）
- ✅ **测试模式**：DRY_RUN 模式先预览再执行
- ✅ **自动创建**：不存在的集合路径自动创建

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

---

### 4. `tag_cleaner.py` - 标签清理工具 🧹

**文献库标签太多太乱？** 这个工具帮你一键清理！

**功能**：

- 🎯 批量清理标签，只保留重要标签
- 🔍 支持按文献类型过滤
- 📊 实时显示清理进度和统计

**使用方法**：

```bash
python tag_cleaner.py
```

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

### 🗂️ 自定义双轨分类体系

在 `organizer.py` 中修改 `PREFERRED_TAXONOMY` 变量，自定义你的分类逻辑：

```python
PREFERRED_TAXONOMY = {
    "Track_A_Archive": {
        "description": "Standard disciplinary classification",
        "emoji": "📚",
        "structure": {
            "Processes": ["ET", "Runoff", ...],
            "Hazards": ["Drought", "Flood", ...],
            "Methodology": ["Remote Sensing", "Deep Learning", ...]
        }
    },
    "Track_B_Idea_Lab": {
        "description": "Question-driven classification",
        "emoji": "💡",
        "structure": {
            "Mechanism": ["Abrupt Transitions", ...],
            "Data Philosophy": ["Signal Purification", ...],
            "Modeling": ["Physics-Informed AI", ...]
        }
    }
}
```

**💡 提示**：运行 `profiler.py` 后，它会基于你的阅读历史给出个性化的 Idea Lab 建议！

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
- 📧 **邮件联系**：licm@scut.com

---

## 🚨 重要提示

**⚠️ 请删除旧的 `organize.py` 文件以避免混淆！**

本项目已将 `organize.py` 和原 `organizer.py` 合并为新的 `organizer.py`。

请执行以下命令删除旧文件：

```bash
# 删除旧的单轨分类脚本
rm organize.py

# 或者重命名为备份
mv organize.py organize.py.deprecated
```

**现在只需使用 `organizer.py` 即可实现双轨分类！**

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**

Made with ❤️ by Prof. Chengming Li & community

</div>
