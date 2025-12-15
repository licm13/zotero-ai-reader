#!/usr/bin/env python3
"""
关键词Top20分析工具
====================

从keyword_categories.json和keyword_statistics.json中提取关键词，
使用Gemini AI进行智能合并和规范化，生成Top20关键词列表。

功能：
1. 提取并拆分关键词
2. 统计频次
3. 使用Gemini识别同义词并合并
4. 生成Top20关键词报告
"""

import os
import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
from google import genai

# ================= 配置 =================

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

API_KEY = "AIzaSyCq8R1HDwiU8dEQDFxpLo-JVYKeIYAWDog"
MODEL = "gemini-3-pro-preview"

KEYWORD_CATEGORIES_FILE = os.path.join(SCRIPT_DIR, "keyword_categories.json")
KEYWORD_STATISTICS_FILE = os.path.join(SCRIPT_DIR, "keyword_statistics.json")
OUTPUT_TOP20_FILE = os.path.join(SCRIPT_DIR, "keyword_top20.json")
OUTPUT_TOP20_REPORT = os.path.join(SCRIPT_DIR, "keyword_top20_report.txt")

# 停用词（常见的无意义词）
STOP_WORDS = {
    'tags', 'tag', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 
    'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
    'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
    'must', 'can', 'this', 'that', 'these', 'those', 'data', 'model',
    'analysis', 'study', 'research', 'method', 'approach'
}

# ================= 数据预处理函数 =================

def load_json_file(filepath: str) -> dict:
    """加载JSON文件"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def remove_tags_prefix(keyword: str) -> str:
    """移除'tags'前缀"""
    if keyword.startswith('tags'):
        return keyword[4:].strip()
    return keyword.strip()

def split_keywords(keyword_string: str) -> List[str]:
    """
    将关键词字符串拆分成单个关键词
    处理连字符、斜杠等分隔符
    """
    # 移除tags前缀
    keyword_string = remove_tags_prefix(keyword_string)
    
    # 先处理常见的分隔符，统一为空格
    keyword_string = re.sub(r'[-/|]', ' ', keyword_string)
    
    # 按空格分割
    words = keyword_string.split()
    
    # 过滤和清理
    keywords = []
    for word in words:
        # 去除标点符号（保留字母、数字、连字符）
        word = re.sub(r'[^\w-]', '', word)
        word = word.strip()
        
        # 过滤空字符串、太短的词、停用词
        if word and len(word) >= 3 and word.lower() not in STOP_WORDS:
            keywords.append(word.lower())
    
    return keywords

def extract_and_count_keywords(categories_data: dict) -> Counter:
    """
    从keyword_assignments中提取所有关键词并统计频次
    """
    keyword_counter = Counter()
    keyword_assignments = categories_data.get('keyword_assignments', {})
    
    print("📊 正在提取和拆分关键词...")
    
    total_phrases = len(keyword_assignments)
    for i, (keyword_phrase, _) in enumerate(keyword_assignments.items()):
        if (i + 1) % 500 == 0:
            print(f"   进度: {i + 1}/{total_phrases}...", end='\r')
        
        # 拆分关键词短语
        keywords = split_keywords(keyword_phrase)
        
        # 统计每个关键词的频次
        for kw in keywords:
            keyword_counter[kw] += 1
    
    print(f"\n   ✅ 提取完成，共 {len(keyword_counter)} 个唯一关键词")
    return keyword_counter

# ================= Gemini AI分析函数 =================

def prepare_keywords_for_gemini(keyword_counter: Counter, top_n: int = 100) -> List[Dict]:
    """
    准备Top N关键词供Gemini分析
    """
    # 获取频次最高的前N个关键词
    top_keywords = keyword_counter.most_common(top_n)
    
    keywords_data = []
    for keyword, frequency in top_keywords:
        keywords_data.append({
            "keyword": keyword,
            "frequency": frequency
        })
    
    return keywords_data

def merge_keywords_with_gemini(keywords_data: List[Dict]) -> Dict:
    """
    使用Gemini API识别同义词并合并关键词
    """
    print("\n🤖 正在使用Gemini AI进行关键词合并分析...")
    
    client = genai.Client(api_key=API_KEY)
    
    # 准备紧凑格式的关键词列表（参考organizer.py的格式）
    keywords_text = "\n".join([
        f"{i+1}|{item['keyword']}|{item['frequency']}"
        for i, item in enumerate(keywords_data)
    ])
    
    prompt = f"""You are a Research Assistant for Prof. Chengming Li (Hydrology/Hydro-climatology/Remote Sensing).

TASK: Analyze keyword list and identify synonyms/similar terms for intelligent merging.

CONTEXT:
- Domain: Hydrology, Remote Sensing, Climate Science, Water Resources
- Focus Areas: Evapotranspiration (ET), Soil Moisture, Drought, Data Fusion, Triple Collocation, Machine Learning

KEYWORDS (Format: ID|Keyword|Frequency):
{keywords_text}

MERGE RULES:
1. **Synonyms**: Merge (e.g., evapotranspiration ↔ transpiration, soil moisture ↔ soil-moisture)
2. **Hierarchy**: Merge specific to general (e.g., "satellite remote sensing" → "remote sensing")
3. **Format Variants**: Unify format (e.g., "climate-change" → "climate change")
4. **Related but Different**: DO NOT merge (e.g., climate change ≠ climate warming, drought ≠ flood)

EXAMPLES:
- ✅ MERGE: evapotranspiration (150) + transpiration (80) → evapotranspiration (230)
- ✅ MERGE: remote sensing (200) + satellite remote sensing (50) → remote sensing (250)
- ✅ MERGE: soil moisture (120) + soil-moisture (30) → soil moisture (150)
- ❌ DO NOT MERGE: climate change (100) vs climate warming (60) [related but distinct concepts]
- ❌ DO NOT MERGE: drought (80) vs flood (70) [opposite concepts]

OUTPUT REQUIREMENTS:
- Return top 20 most important keywords after merging
- Merged frequency = sum of all variants' frequencies
- Sort by merged frequency (descending)
- Use standardized keyword forms

OUTPUT: JSON format:
{{
    "normalized_keywords": [
        {{
            "keyword": "evapotranspiration",
            "frequency": 230,
            "variants": ["evapotranspiration", "transpiration"],
            "description": "Merged synonyms: evapotranspiration includes transpiration"
        }},
        ...
    ],
    "merge_rules": [
        {{
            "from": "transpiration",
            "to": "evapotranspiration",
            "reason": "synonym: transpiration is a component of evapotranspiration"
        }},
        ...
    ]
}}

JSON:"""

    try:
        print("   正在调用Gemini API...")
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        result = json.loads(response.text)
        print("   ✅ Gemini分析完成")
        return result
        
    except Exception as e:
        print(f"   ❌ Gemini API调用失败: {e}")
        # 如果API失败，返回原始数据的前20个
        print("   ⚠️  使用原始频次排序...")
        return {
            "normalized_keywords": [
                {
                    "keyword": item['keyword'],
                    "frequency": item['frequency'],
                    "variants": [item['keyword']],
                    "description": "原始关键词"
                }
                for item in keywords_data[:20]
            ],
            "merge_rules": []
        }

def apply_merge_to_all_keywords(keyword_counter: Counter, merge_result: Dict) -> Counter:
    """
    将Gemini的合并规则应用到所有关键词
    """
    merge_rules = merge_result.get('merge_rules', [])
    normalized_keywords = merge_result.get('normalized_keywords', [])
    
    # 构建映射：从变体到标准关键词
    variant_to_normalized = {}
    for item in normalized_keywords:
        normalized = item['keyword']
        for variant in item.get('variants', [normalized]):
            variant_to_normalized[variant.lower()] = normalized
    
    # 应用到所有合并规则
    for rule in merge_rules:
        from_kw = rule.get('from', '').lower()
        to_kw = rule.get('to', '').lower()
        if from_kw and to_kw:
            variant_to_normalized[from_kw] = to_kw
    
    # 应用合并
    merged_counter = Counter()
    for keyword, frequency in keyword_counter.items():
        normalized = variant_to_normalized.get(keyword.lower(), keyword)
        merged_counter[normalized] += frequency
    
    return merged_counter

# ================= 主函数 =================

def main():
    """
    主分析流程
    """
    print("=" * 70)
    print("🔍 关键词Top20分析工具")
    print("=" * 70)
    
    # 1. 加载数据
    print("\n📂 正在加载数据文件...")
    try:
        categories_data = load_json_file(KEYWORD_CATEGORIES_FILE)
        statistics_data = load_json_file(KEYWORD_STATISTICS_FILE)
        print(f"   ✅ 已加载 {KEYWORD_CATEGORIES_FILE}")
        print(f"   ✅ 已加载 {KEYWORD_STATISTICS_FILE}")
        print(f"   📊 统计信息：")
        print(f"      - 总文献数: {statistics_data.get('total_items', 0)}")
        print(f"      - 唯一关键词数: {statistics_data.get('total_unique_keywords', 0)}")
        print(f"      - 分类数: {statistics_data.get('total_categories', 0)}")
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
        return
    
    # 2. 提取和统计关键词
    keyword_counter = extract_and_count_keywords(categories_data)
    
    # 3. 准备Top 100供Gemini分析
    print(f"\n📋 准备Top 100关键词供AI分析...")
    top_keywords = prepare_keywords_for_gemini(keyword_counter, top_n=100)
    print(f"   ✅ 已准备 {len(top_keywords)} 个关键词")
    
    # 4. 使用Gemini进行智能合并
    merge_result = merge_keywords_with_gemini(top_keywords)
    
    # 5. 应用合并规则到所有关键词
    print("\n🔄 正在应用合并规则到所有关键词...")
    merged_counter = apply_merge_to_all_keywords(keyword_counter, merge_result)
    
    # 6. 获取Top20
    top20 = merged_counter.most_common(20)
    
    # 7. 构建详细结果
    result = {
        "top20_keywords": [
            {
                "rank": i + 1,
                "keyword": keyword,
                "frequency": frequency,
                "percentage": round(frequency / len(keyword_counter) * 100, 2) if len(keyword_counter) > 0 else 0,
                "gemini_info": next(
                    (item for item in merge_result.get('normalized_keywords', []) 
                     if item['keyword'].lower() == keyword.lower()),
                    None
                )
            }
            for i, (keyword, frequency) in enumerate(top20)
        ],
        "statistics": {
            "total_keywords_before_merge": len(keyword_counter),
            "total_keywords_after_merge": len(merged_counter),
            "merge_rules_count": len(merge_result.get('merge_rules', [])),
            "total_frequency": sum(keyword_counter.values())
        },
        "merge_details": merge_result
    }
    
    # 8. 保存结果
    print("\n💾 正在保存结果...")
    with open(OUTPUT_TOP20_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"   ✅ 已保存到: {OUTPUT_TOP20_FILE}")
    
    # 9. 生成文本报告
    with open(OUTPUT_TOP20_REPORT, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("关键词Top20分析报告\n")
        f.write("=" * 70 + "\n\n")
        
        # 统计信息
        stats = result['statistics']
        f.write("📊 统计信息\n")
        f.write("-" * 70 + "\n")
        f.write(f"合并前关键词数: {stats['total_keywords_before_merge']}\n")
        f.write(f"合并后关键词数: {stats['total_keywords_after_merge']}\n")
        f.write(f"合并规则数: {stats['merge_rules_count']}\n")
        f.write(f"总频次: {stats['total_frequency']}\n")
        f.write("\n")
        
        # Top20列表
        f.write("=" * 70 + "\n")
        f.write("🏆 Top20关键词\n")
        f.write("=" * 70 + "\n\n")
        
        for item in result['top20_keywords']:
            rank = item['rank']
            keyword = item['keyword']
            frequency = item['frequency']
            percentage = item['percentage']
            gemini_info = item.get('gemini_info')
            
            f.write(f"{rank:2d}. {keyword}\n")
            f.write(f"    频次: {frequency} ({percentage}%)\n")
            
            if gemini_info:
                variants = gemini_info.get('variants', [])
                if len(variants) > 1:
                    f.write(f"    合并的变体: {', '.join(variants)}\n")
                desc = gemini_info.get('description', '')
                if desc:
                    f.write(f"    说明: {desc}\n")
            f.write("\n")
        
        # 合并规则详情
        merge_rules = merge_result.get('merge_rules', [])
        if merge_rules:
            f.write("=" * 70 + "\n")
            f.write("🔀 合并规则详情\n")
            f.write("=" * 70 + "\n\n")
            for i, rule in enumerate(merge_rules, 1):
                f.write(f"{i}. {rule.get('from', '')} → {rule.get('to', '')}\n")
                f.write(f"   原因: {rule.get('reason', 'N/A')}\n\n")
    
    print(f"   ✅ 已保存到: {OUTPUT_TOP20_REPORT}")
    
    # 10. 打印摘要
    print("\n" + "=" * 70)
    print("📊 分析摘要")
    print("=" * 70)
    print(f"合并前关键词数: {stats['total_keywords_before_merge']}")
    print(f"合并后关键词数: {stats['total_keywords_after_merge']}")
    print(f"合并规则数: {stats['merge_rules_count']}")
    print("\n🏆 Top10关键词:")
    for item in result['top20_keywords'][:10]:
        print(f"  {item['rank']:2d}. {item['keyword']:30s} (频次: {item['frequency']})")
    print("\n✅ 分析完成！")

if __name__ == "__main__":
    main()

