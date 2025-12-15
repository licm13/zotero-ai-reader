#!/usr/bin/env python3
"""
Zotero 关键词分类分析工具
============================

从Zotero库中提取所有文献的AI笔记关键词，进行智能聚类和分类分析。

功能特性：
- 自动检索所有文献的"AI 深度阅读报告"笔记
- 提取Keywords关键词部分
- 关键词归一化（去重、同义词识别、缩写展开）
- 基于语义相似度和共现关系的智能聚类
- 支持多标签分类（一个关键词可属于多个类目）
- 生成层次化分类结构和统计报告

作者：Prof. Chengming Li (SCUT)
"""

import os
import re
import json
import math
import time
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
from pyzotero import zotero

try:
    import config
    LIBRARY_ID = config.LIBRARY_ID
    API_KEY = config.API_KEY
    LIBRARY_TYPE = config.LIBRARY_TYPE
    print("✅ 已从 config.py 加载配置")
except ImportError:
    print("⚠️  未找到 config.py 文件！")
    print("📋 请复制 config.example.py 为 config.py 并填入您的配置信息")
    exit(1)

# ================= 配置参数 =================

NOTE_TITLE = "AI 深度阅读报告"  # 目标笔记标题
NOTE_TITLE_KEYWORDS = ["AI", "深度阅读", "阅读报告"]  # 用于模糊匹配的关键词
OUTPUT_DIR = "keyword_analysis"  # 输出目录
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "keyword_categories.json")  # JSON输出
OUTPUT_REPORT = os.path.join(OUTPUT_DIR, "keyword_report.txt")  # 文本报告
OUTPUT_STATS = os.path.join(OUTPUT_DIR, "keyword_statistics.json")  # 统计信息

# 相似度阈值
SEMANTIC_SIMILARITY_THRESHOLD = 0.6  # 语义相似度阈值（0-1）
STRING_SIMILARITY_THRESHOLD = 0.8    # 字符串相似度阈值（0-1）
COOCCURRENCE_WEIGHT = 0.3             # 共现关系权重
MIN_CLUSTER_SIZE = 2                  # 最小聚类大小

# 调试模式
DEBUG_MODE = True  # 是否显示详细调试信息

# ================= 辅助函数 =================

def normalize_keyword(keyword: str) -> str:
    """
    关键词归一化：
    - 去除首尾空格
    - 小写化
    - 去除特殊字符（保留字母、数字、空格、连字符）
    """
    # 去除HTML标签
    keyword = re.sub(r'<[^>]+>', '', keyword)
    # 转换为小写
    keyword = keyword.lower().strip()
    # 保留字母、数字、空格、连字符、中文
    keyword = re.sub(r'[^\w\s\-一-龥]', '', keyword)
    # 规范化空格
    keyword = re.sub(r'\s+', ' ', keyword).strip()
    return keyword

def split_keywords(keywords_text: str) -> List[str]:
    """
    从关键词文本中提取单个关键词列表
    支持多种分隔符：逗号、分号、换行、竖线等
    """
    # 替换各种分隔符为统一的分隔符
    text = re.sub(r'[，；、\n\r|]', ',', keywords_text)
    # 按逗号分割
    keywords = [normalize_keyword(kw.strip()) for kw in text.split(',')]
    # 过滤空字符串和太短的关键词
    keywords = [kw for kw in keywords if kw and len(kw) >= 2]
    return keywords

def extract_keywords_from_note(note_content: str) -> List[str]:
    """
    从笔记内容中提取Keywords部分
    """
    if not note_content:
        return []
    
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', note_content)
    
    # 查找Keywords部分（支持多种格式，包括更宽松的匹配）
    patterns = [
        r'(?:Keywords|关键词|论文关键词|关键词：|Keywords:|Key\s*words)[：:\s]*\n?\s*(.+?)(?:\n\n|\n(?:Summary|总结|Abstract|摘要|要点|核心|主要)|$)',
        r'(?:Keywords|关键词|论文关键词)[：:\s]+(.+?)(?:\n\n|\n(?:Summary|总结|Abstract|摘要)|$)',
        r'(?:Keywords|关键词)[：:\s]*(.+?)(?:\n{2,}|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match:
            keywords_text = match.group(1).strip()
            # 去除可能的后续标题（如"Summary"、"Abstract"等）
            keywords_text = re.split(r'\n(?:Summary|总结|Abstract|摘要|要点|核心|主要|研究|方法)', keywords_text, flags=re.IGNORECASE)[0]
            keywords = split_keywords(keywords_text)
            if keywords:
                if DEBUG_MODE:
                    print(f"      ✨ 提取到关键词: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
                return keywords
    
    # 如果找不到明确的关键词部分，尝试查找包含"关键词"的行
    if "关键词" in text or "Keywords" in text or "keywords" in text.lower():
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'(?:关键词|Keywords)', line, re.IGNORECASE):
                # 取该行及后续几行作为关键词
                keywords_text = '\n'.join(lines[i:i+3])
                keywords = split_keywords(keywords_text)
                if keywords:
                    if DEBUG_MODE:
                        print(f"      ✨ 从行中提取到关键词: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
                    return keywords
    
    if DEBUG_MODE:
        print(f"      ⚠️  未找到关键词部分（内容前100字符: {text[:100]}...）")
    
    return []

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    计算两个字符串的编辑距离（Levenshtein距离）
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def string_similarity(s1: str, s2: str) -> float:
    """
    计算字符串相似度（基于编辑距离）
    返回值：0-1之间，1表示完全相同
    """
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0
    
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    
    distance = levenshtein_distance(s1, s2)
    return 1.0 - (distance / max_len)

def jaccard_similarity(set1: Set, set2: Set) -> float:
    """
    计算两个集合的Jaccard相似度
    """
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    if union == 0:
        return 0.0
    return intersection / union

def tfidf_vectorize(keywords_list: List[List[str]]) -> Tuple[Dict[str, int], List[Dict[str, float]]]:
    """
    将关键词列表转换为TF-IDF向量
    返回：(词汇表字典, TF-IDF向量列表)
    """
    # 构建词汇表
    vocab = {}
    doc_freq = defaultdict(int)  # 文档频率（包含该词的文档数）
    
    for doc_keywords in keywords_list:
        unique_keywords = set(doc_keywords)
        for kw in unique_keywords:
            if kw not in vocab:
                vocab[kw] = len(vocab)
            doc_freq[kw] += 1
    
    total_docs = len(keywords_list)
    vocab_size = len(vocab)
    
    # 计算TF-IDF向量
    tfidf_vectors = []
    for doc_keywords in keywords_list:
        vector = {}
        kw_count = Counter(doc_keywords)
        max_count = max(kw_count.values()) if kw_count else 1
        
        for kw, count in kw_count.items():
            # TF (Term Frequency)
            tf = count / max_count
            # IDF (Inverse Document Frequency)
            idf = math.log(total_docs / (doc_freq[kw] + 1))
            # TF-IDF
            vector[kw] = tf * idf
        
        tfidf_vectors.append(vector)
    
    return vocab, tfidf_vectors

def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """
    计算两个TF-IDF向量的余弦相似度
    """
    # 获取所有唯一的键
    all_keys = set(vec1.keys()) | set(vec2.keys())
    
    if not all_keys:
        return 0.0
    
    dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

def build_cooccurrence_matrix(keywords_list: List[List[str]]) -> Dict[Tuple[str, str], int]:
    """
    构建关键词共现矩阵
    返回：{(keyword1, keyword2): count, ...}
    """
    cooccurrence = defaultdict(int)
    
    for doc_keywords in keywords_list:
        unique_keywords = list(set(doc_keywords))
        # 每对关键词在同一文档中出现，共现次数+1
        for i, kw1 in enumerate(unique_keywords):
            for kw2 in unique_keywords[i+1:]:
                # 确保有序（避免重复）
                pair = tuple(sorted([kw1, kw2]))
                cooccurrence[pair] += 1
    
    return dict(cooccurrence)

def calculate_keyword_similarity(kw1: str, kw2: str, 
                                  vocab: Dict[str, int],
                                  tfidf_vectors: List[Dict[str, float]],
                                  keywords_list: List[List[str]],
                                  cooccurrence: Dict[Tuple[str, str], int]) -> float:
    """
    计算两个关键词的综合相似度
    结合：字符串相似度、TF-IDF语义相似度、共现关系
    """
    # 1. 字符串相似度
    str_sim = string_similarity(kw1, kw2)
    
    # 2. 语义相似度（基于TF-IDF）
    # 找到包含这两个关键词的文档，计算它们的向量相似度
    semantic_sim = 0.0
    docs_with_kw1 = [i for i, doc in enumerate(keywords_list) if kw1 in doc]
    docs_with_kw2 = [i for i, doc in enumerate(keywords_list) if kw2 in doc]
    
    if docs_with_kw1 and docs_with_kw2:
        # 计算包含kw1和kw2的文档向量的平均相似度
        similarities = []
        for i in docs_with_kw1:
            for j in docs_with_kw2:
                sim = cosine_similarity(tfidf_vectors[i], tfidf_vectors[j])
                similarities.append(sim)
        
        if similarities:
            semantic_sim = sum(similarities) / len(similarities)
    
    # 3. 共现关系
    cooccurrence_sim = 0.0
    pair = tuple(sorted([kw1, kw2]))
    if pair in cooccurrence:
        # 归一化共现次数（使用对数缩放）
        cooccurrence_sim = min(1.0, math.log(cooccurrence[pair] + 1) / math.log(10))
    
    # 综合相似度（加权平均）
    # 字符串相似度权重最高（处理缩写和拼写变体）
    # 语义相似度次之（理解语义关系）
    # 共现关系权重较低（作为补充）
    combined_sim = (0.5 * str_sim + 
                    0.3 * semantic_sim + 
                    COOCCURRENCE_WEIGHT * cooccurrence_sim)
    
    return combined_sim

def hierarchical_clustering(keywords_list: List[List[str]],
                            all_keywords: Set[str],
                            vocab: Dict[str, int],
                            tfidf_vectors: List[Dict[str, float]],
                            cooccurrence: Dict[Tuple[str, str], int]) -> Dict[str, List[str]]:
    """
    层次聚类算法：将相似的关键词归为一类
    
    返回：{category_name: [keyword1, keyword2, ...], ...}
    """
    # 计算所有关键词对的相似度
    keyword_pairs = []
    keyword_list = list(all_keywords)
    
    print(f"   🔄 计算 {len(keyword_list)} 个关键词之间的相似度...")
    for i, kw1 in enumerate(keyword_list):
        for kw2 in keyword_list[i+1:]:
            sim = calculate_keyword_similarity(kw1, kw2, vocab, tfidf_vectors, 
                                              keywords_list, cooccurrence)
            if sim >= SEMANTIC_SIMILARITY_THRESHOLD or string_similarity(kw1, kw2) >= STRING_SIMILARITY_THRESHOLD:
                keyword_pairs.append((sim, kw1, kw2))
    
    # 按相似度排序
    keyword_pairs.sort(reverse=True, key=lambda x: x[0])
    
    # 聚类：使用并查集思想
    keyword_to_cluster = {kw: i for i, kw in enumerate(keyword_list)}
    clusters = {i: [kw] for i, kw in enumerate(keyword_list)}
    
    for sim, kw1, kw2 in keyword_pairs:
        cluster1 = keyword_to_cluster[kw1]
        cluster2 = keyword_to_cluster[kw2]
        
        if cluster1 != cluster2:
            # 合并两个聚类
            # 将cluster2中的所有关键词移到cluster1
            for kw in clusters[cluster2]:
                keyword_to_cluster[kw] = cluster1
                clusters[cluster1].append(kw)
            del clusters[cluster2]
    
    # 生成类别名称和结果
    categories = {}
    for cluster_id, keywords in clusters.items():
        if len(keywords) >= MIN_CLUSTER_SIZE:
            # 选择最长的关键词作为类别名称（或出现频率最高的）
            category_name = max(keywords, key=lambda x: (len(x), keywords.count(x)))
            categories[category_name] = sorted(set(keywords))
    
    return categories

def assign_multi_category(keywords_list: List[List[str]],
                          categories: Dict[str, List[str]],
                          all_keywords: Set[str]) -> Dict[str, List[str]]:
    """
    多标签分配：允许一个关键词属于多个类别
    基于关键词在不同文档中的共现模式
    """
    keyword_categories = defaultdict(set)
    
    # 首先，将关键词分配到它们所在的聚类类别
    for category, keywords in categories.items():
        for kw in keywords:
            keyword_categories[kw].add(category)
    
    # 然后，基于共现关系，扩展多标签
    # 如果一个关键词经常与某个类别的其他关键词共同出现，也加入该类别
    for doc_keywords in keywords_list:
        unique_doc_kws = set(doc_keywords)
        
        # 找到文档中已有的类别
        doc_categories = set()
        for kw in unique_doc_kws:
            doc_categories.update(keyword_categories[kw])
        
        # 将该文档中的所有关键词都关联到这些类别
        for kw in unique_doc_kws:
            keyword_categories[kw].update(doc_categories)
    
    # 转换为列表格式
    result = {kw: sorted(list(cats)) for kw, cats in keyword_categories.items()}
    return result

# ================= 主处理函数 =================

def is_target_note(note_title: str, note_content: str = "") -> bool:
    """
    判断是否是目标笔记（支持模糊匹配）
    不仅检查标题，也检查内容
    """
    # 检查标题
    if note_title:
        note_title_lower = note_title.lower()
        
        # 完全匹配
        if NOTE_TITLE in note_title or note_title == NOTE_TITLE:
            return True
        
        # 模糊匹配：包含关键词中的至少一个
        for keyword in NOTE_TITLE_KEYWORDS:
            if keyword.lower() in note_title_lower:
                return True
        
        # 检查是否包含"AI"和"阅读"或"报告"
        if "ai" in note_title_lower and ("阅读" in note_title or "报告" in note_title):
            return True
    
    # 如果标题为空或不匹配，检查内容
    if note_content:
        note_content_lower = note_content.lower()
        # 检查内容中是否包含"AI 深度阅读报告"或相关关键词
        if "ai 深度阅读报告" in note_content_lower or "ai深度阅读报告" in note_content_lower:
            return True
        
        # 检查是否包含关键词组合
        has_ai = "ai" in note_content_lower or "🤖" in note_content
        has_reading = "深度阅读" in note_content or "阅读报告" in note_content
        if has_ai and has_reading:
            return True
        
        # 检查HTML格式的标题
        if "<h1>" in note_content and "ai" in note_content_lower and "阅读" in note_content:
            return True
    
    return False

def fetch_items_with_retry(zot, limit, start, max_retries=3):
    """
    带重试机制的获取文献项
    """
    for attempt in range(max_retries):
        try:
            items = zot.items(limit=limit, start=start)
            return items
        except Exception as e:
            error_str = str(e)
            # 如果是502错误，等待后重试
            if "502" in error_str or "Bad Gateway" in error_str:
                wait_time = (attempt + 1) * 2  # 递增等待时间：2s, 4s, 6s
                print(f"\n   ⚠️  遇到502错误，等待{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
                continue
            else:
                # 其他错误直接抛出
                raise
    # 所有重试都失败
    raise Exception(f"获取文献失败，已重试{max_retries}次")

def is_item_type_supported(item):
    """
    检查文献类型是否支持children调用
    只有主要文献类型（journalArticle, conferencePaper等）才支持，附件不支持
    """
    item_type = item['data'].get('itemType', '')
    # 支持的类型：主要文献类型
    supported_types = {
        'journalArticle', 'conferencePaper', 'book', 'bookSection',
        'thesis', 'report', 'presentation', 'document', 'manuscript',
        'preprint', 'patent', 'dataset', 'webpage', 'blogPost'
    }
    return item_type in supported_types

def fetch_all_items_with_keywords(zot):
    """
    从Zotero获取所有文献及其关键词（检索所有文献，无数量限制）
    """
    print("\n📚 正在检索Zotero库中的所有文献...")
    
    # 获取所有文献项（分页获取，确保获取全部）
    all_items = []
    start = 0
    batch_size = 100  # 每批获取100个
    
    try:
        while True:
            # 使用重试机制获取
            items = fetch_items_with_retry(zot, batch_size, start)
            
            if not items:
                break
            
            # 过滤出支持的类型
            valid_items = [item for item in items if is_item_type_supported(item)]
            all_items.extend(valid_items)
            
            print(f"   📄 已获取 {len(all_items)} 个有效文献项 (本批: {len(items)}个，有效: {len(valid_items)}个)...", end='\r')
            
            # 如果返回的数量少于batch_size，说明已经获取完所有项
            if len(items) < batch_size:
                break
            
            start += batch_size
            
            # 添加延迟，避免API限制
            time.sleep(0.5)
            
            # 安全限制：最多获取10000篇（防止无限循环）
            if len(all_items) >= 10000:
                print(f"\n   ⚠️  已达到最大限制（10000篇），停止检索")
                break
        
        print(f"\n   ✅ 共找到 {len(all_items)} 个有效文献项")
    except Exception as e:
        print(f"\n   ❌ 获取文献失败: {e}")
        if all_items:
            print(f"   ⚠️  已获取 {len(all_items)} 个文献项，将继续处理已获取的项")
        else:
            return []
    
    print(f"\n🔍 正在查找包含 '{NOTE_TITLE}' 的笔记并提取关键词...")
    print(f"   🔎 匹配模式: 完全匹配或包含关键词 {NOTE_TITLE_KEYWORDS}")
    
    items_with_keywords = []
    notes_found = 0
    notes_checked = 0
    notes_with_target_title = 0
    errors_count = 0
    skipped_count = 0
    
    for i, item in enumerate(all_items):
        if (i + 1) % 50 == 0:
            print(f"   进度: {i + 1}/{len(all_items)} (目标笔记: {notes_with_target_title}, 提取成功: {notes_found}, 错误: {errors_count})...")
        
        try:
            # 获取子项（笔记）- 添加重试机制
            children = None
            max_retries = 2
            for retry in range(max_retries):
                try:
                    children = zot.children(item['key'])
                    break
                except Exception as e:
                    error_str = str(e)
                    # 检查是否是"can only be called on PDF, EPUB, and snapshot attachments"错误
                    if "can only be called on" in error_str or "PDF, EPUB" in error_str:
                        # 这种情况是正常的，某些项目类型不支持children
                        skipped_count += 1
                        if DEBUG_MODE and skipped_count <= 3:
                            item_title = item['data'].get('title', 'Untitled')[:50]
                            item_type = item['data'].get('itemType', 'unknown')
                            print(f"      ⏭️  跳过项目 (类型: {item_type}): {item_title}...")
                        children = []
                        break
                    # 502错误，等待后重试
                    elif "502" in error_str or "Bad Gateway" in error_str:
                        if retry < max_retries - 1:
                            wait_time = (retry + 1) * 1
                            print(f"      ⚠️  API错误，等待{wait_time}秒后重试...")
                            time.sleep(wait_time)
                            continue
                        else:
                            raise
                    else:
                        raise
            
            if children is None:
                errors_count += 1
                if DEBUG_MODE and errors_count <= 3:
                    print(f"      ❌ 无法获取子项: {item['data'].get('title', 'Untitled')[:50]}...")
                continue
            
            found_keywords = False
            for child in children:
                if child['data']['itemType'] == 'note':
                    notes_checked += 1
                    note_title = child['data'].get('title', '')
                    note_content = child['data'].get('note', '')
                    
                    # 检查是否是目标笔记（模糊匹配，包括标题和内容）
                    if is_target_note(note_title, note_content):
                        notes_with_target_title += 1
                        display_title = note_title if note_title else "(无标题，从内容识别)"
                        if DEBUG_MODE:
                            print(f"\n      ✅ [{notes_with_target_title}] 找到目标笔记: '{display_title}'")
                            print(f"         文献: {item['data'].get('title', 'Untitled')[:60]}...")
                        
                        keywords = extract_keywords_from_note(note_content)
                        
                        if keywords:
                            items_with_keywords.append({
                                'key': item['key'],
                                'title': item['data'].get('title', 'Untitled'),
                                'keywords': keywords,
                                'note_title': note_title
                            })
                            notes_found += 1
                            found_keywords = True
                            if DEBUG_MODE:
                                print(f"         ✨ 成功提取 {len(keywords)} 个关键词")
                        elif DEBUG_MODE:
                            print(f"         ⚠️  未提取到关键词")
                    
                    # 如果已经找到关键词，跳过该文献的其他笔记
                    if found_keywords:
                        break
            
            # 添加小延迟，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(0.1)
            
        except Exception as e:
            errors_count += 1
            # 跳过错误项，继续处理
            if DEBUG_MODE and errors_count <= 5:
                item_title = item['data'].get('title', 'Untitled')[:50]
                print(f"      ❌ 处理文献时出错: {item_title}... - {str(e)[:100]}")
            continue
    
    print(f"\n   📊 统计信息:")
    print(f"      - 处理了 {len(all_items)} 个有效文献项")
    print(f"      - 检查了 {notes_checked} 个笔记")
    print(f"      - 找到 {notes_with_target_title} 个目标笔记")
    print(f"      - 成功提取 {notes_found} 篇文献的关键词")
    if skipped_count > 0:
        print(f"      - 跳过了 {skipped_count} 个不支持的项目")
    if errors_count > 0:
        print(f"      - 遇到 {errors_count} 个错误（已跳过）")
    
    return items_with_keywords

def analyze_and_classify_keywords(items_with_keywords: List[Dict]) -> Dict:
    """
    分析关键词并进行分类
    """
    if not items_with_keywords:
        print("\n⚠️  没有找到包含关键词的文献！")
        return {}
    
    print(f"\n📊 正在分析 {len(items_with_keywords)} 篇文献的关键词...")
    
    # 提取所有关键词列表
    keywords_list = [item['keywords'] for item in items_with_keywords]
    all_keywords = set()
    for kws in keywords_list:
        all_keywords.update(kws)
    
    print(f"   📝 共发现 {len(all_keywords)} 个唯一关键词")
    
    # 构建TF-IDF向量
    print("   🔄 构建TF-IDF向量...")
    vocab, tfidf_vectors = tfidf_vectorize(keywords_list)
    
    # 构建共现矩阵
    print("   🔄 构建关键词共现矩阵...")
    cooccurrence = build_cooccurrence_matrix(keywords_list)
    print(f"   ✅ 发现 {len(cooccurrence)} 对共现关键词")
    
    # 层次聚类
    print("\n🎯 正在进行关键词聚类分析...")
    categories = hierarchical_clustering(keywords_list, all_keywords, vocab, 
                                        tfidf_vectors, cooccurrence)
    print(f"   ✅ 生成 {len(categories)} 个类别")
    
    # 多标签分配
    print("\n🏷️  正在分配多标签分类...")
    keyword_categories = assign_multi_category(keywords_list, categories, all_keywords)
    
    # 生成统计信息
    stats = {
        'total_items': len(items_with_keywords),
        'total_unique_keywords': len(all_keywords),
        'total_categories': len(categories),
        'keywords_per_category': {cat: len(kws) for cat, kws in categories.items()},
        'multi_category_keywords': sum(1 for cats in keyword_categories.values() if len(cats) > 1),
        'total_cooccurrences': len(cooccurrence)
    }
    
    return {
        'categories': categories,
        'keyword_assignments': keyword_categories,
        'statistics': stats,
        'raw_data': items_with_keywords
    }

def save_results(results: Dict):
    """
    保存分析结果
    """
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 保存JSON格式的分类结果
    output_data = {
        'categories': results['categories'],
        'keyword_assignments': results['keyword_assignments'],
        'statistics': results['statistics']
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 分类结果已保存至: {OUTPUT_JSON}")
    
    # 保存统计信息
    with open(OUTPUT_STATS, 'w', encoding='utf-8') as f:
        json.dump(results['statistics'], f, indent=2, ensure_ascii=False)
    print(f"✅ 统计信息已保存至: {OUTPUT_STATS}")
    
    # 生成文本报告
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("关键词分类分析报告\n")
        f.write("=" * 70 + "\n\n")
        
        # 统计信息
        stats = results['statistics']
        f.write("📊 统计信息\n")
        f.write("-" * 70 + "\n")
        f.write(f"总文献数: {stats['total_items']}\n")
        f.write(f"唯一关键词数: {stats['total_unique_keywords']}\n")
        f.write(f"分类类别数: {stats['total_categories']}\n")
        f.write(f"多标签关键词数: {stats['multi_category_keywords']}\n")
        f.write(f"关键词共现对数: {stats['total_cooccurrences']}\n")
        f.write("\n")
        
        # 类别详情
        f.write("=" * 70 + "\n")
        f.write("📂 分类类别详情\n")
        f.write("=" * 70 + "\n\n")
        
        categories = results['categories']
        for i, (category, keywords) in enumerate(sorted(categories.items(), 
                                                        key=lambda x: len(x[1]), 
                                                        reverse=True), 1):
            f.write(f"{i}. {category} ({len(keywords)} 个关键词)\n")
            f.write("-" * 70 + "\n")
            for kw in keywords:
                assignments = results['keyword_assignments'].get(kw, [])
                if len(assignments) > 1:
                    f.write(f"   • {kw} [多标签: {', '.join(assignments)}]\n")
                else:
                    f.write(f"   • {kw}\n")
            f.write("\n")
        
        # 多标签关键词列表
        f.write("=" * 70 + "\n")
        f.write("🏷️  多标签关键词列表\n")
        f.write("=" * 70 + "\n\n")
        
        multi_label_kws = [(kw, cats) for kw, cats in results['keyword_assignments'].items() 
                          if len(cats) > 1]
        multi_label_kws.sort(key=lambda x: len(x[1]), reverse=True)
        
        for kw, cats in multi_label_kws:
            f.write(f"• {kw}\n")
            f.write(f"  所属类别: {', '.join(cats)}\n\n")
    
    print(f"✅ 分析报告已保存至: {OUTPUT_REPORT}")

def main():
    """
    主函数
    """
    print("=" * 70)
    print("🔍 Zotero 关键词分类分析工具")
    print("=" * 70)
    
    # 初始化Zotero连接
    try:
        zot = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY)
        print(f"✅ 已连接到Zotero库 (ID: {LIBRARY_ID})")
    except Exception as e:
        print(f"❌ 连接Zotero失败: {e}")
        return
    
    # 获取所有文献及其关键词
    items_with_keywords = fetch_all_items_with_keywords(zot)
    
    if not items_with_keywords:
        print("\n⚠️  未找到包含关键词的文献，请检查：")
        print(f"   1. 笔记标题是否包含 '{NOTE_TITLE}'")
        print(f"   2. 笔记中是否包含Keywords部分")
        return
    
    # 分析并分类关键词
    results = analyze_and_classify_keywords(items_with_keywords)
    
    if not results:
        return
    
    # 保存结果
    save_results(results)
    
    # 打印摘要
    print("\n" + "=" * 70)
    print("📊 分析摘要")
    print("=" * 70)
    stats = results['statistics']
    print(f"总文献数: {stats['total_items']}")
    print(f"唯一关键词数: {stats['total_unique_keywords']}")
    print(f"分类类别数: {stats['total_categories']}")
    print(f"多标签关键词数: {stats['multi_category_keywords']}")
    print("\n✅ 分析完成！")
    print(f"📁 结果文件保存在: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()

