"""
学生分发版：仅通过小米 MIMO（OpenAI 兼容接口）调用模型，无 Gemini 分支。
默认与本文件夹内的 config.py、prompt.md 配套使用。
"""
import os
import sys
import time
import importlib.util
import markdown
import fitz  # PyMuPDF
from pyzotero import zotero
from openai import OpenAI


# ================= 1. 运行时全局变量 =================
config = None
LIBRARY_ID = ""
API_KEY = ""
LIBRARY_TYPE = "user"
ZOTERO_STORAGE_PATH = ""
PROMPT_FILE_NAME = "prompt.md"
ITEM_TYPES_TO_PROCESS = None
TARGET_COLLECTION_PATH = None
TEST_MODE = False
TEST_LIMIT = 3
ACTIVE_API_KEY = ""
ACTIVE_MODEL = "mimo-v2-pro"
MIMO_BASE_URL = None
SUCCESS_TAG = "MIMO_read"
NON_LIT_TAG = "non-read-mimo"
TAGS_SKIP_IF_PRESENT = None
_PROMPT_TEMPLATE_OVERRIDE = None


def _load_config_py(path: str):
    spec = importlib.util.spec_from_file_location("student_zotero_config", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载配置文件")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bootstrap_cli():
    """读取本文件夹内的 config.py（无交互菜单，仅小米 MIMO）。"""
    global config, LIBRARY_ID, API_KEY, LIBRARY_TYPE, ZOTERO_STORAGE_PATH
    global PROMPT_FILE_NAME, ITEM_TYPES_TO_PROCESS, TARGET_COLLECTION_PATH, TEST_MODE, TEST_LIMIT
    global ACTIVE_API_KEY, ACTIVE_MODEL, SUCCESS_TAG, NON_LIT_TAG
    global _PROMPT_TEMPLATE_OVERRIDE, TAGS_SKIP_IF_PRESENT

    base = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(base, "config.py")
    if not os.path.isfile(cfg_path):
        print(f"❌ 未找到配置文件: {cfg_path}")
        print("   请将 config.example.py 复制为 config.py 并填写密钥与路径。")
        sys.exit(1)

    _PROMPT_TEMPLATE_OVERRIDE = None
    TAGS_SKIP_IF_PRESENT = None
    config = _load_config_py(cfg_path)

    LIBRARY_ID = config.LIBRARY_ID
    API_KEY = config.API_KEY
    LIBRARY_TYPE = config.LIBRARY_TYPE
    ZOTERO_STORAGE_PATH = config.ZOTERO_STORAGE_PATH
    PROMPT_FILE_NAME = getattr(config, "PROMPT_FILE_NAME", "prompt.md")
    ITEM_TYPES_TO_PROCESS = getattr(config, "ITEM_TYPES_TO_PROCESS", None)
    TARGET_COLLECTION_PATH = getattr(config, "TARGET_COLLECTION_PATH", None)
    TEST_MODE = getattr(config, "TEST_MODE", False)
    TEST_LIMIT = getattr(config, "TEST_LIMIT", 3)

    ACTIVE_API_KEY = getattr(config, "XiaoMi_API_KEY", None) or getattr(config, "MIMO_API_KEY", None)
    ACTIVE_MODEL = getattr(config, "XIAOMI_MODEL", "mimo-v2-pro")
    MIMO_BASE_URL = getattr(config, "MIMO_BASE_URL", None)
    SUCCESS_TAG = getattr(config, "SUCCESS_TAG", "MIMO_read")
    NON_LIT_TAG = getattr(config, "NON_LIT_TAG", "non-read-mimo")

    tskip = getattr(config, "TAGS_SKIP_IF_PRESENT", None)
    if tskip:
        if isinstance(tskip, str):
            TAGS_SKIP_IF_PRESENT = [p.strip() for p in tskip.split(",") if p.strip()]
        else:
            TAGS_SKIP_IF_PRESENT = list(tskip)

    if not ACTIVE_API_KEY:
        print("❌ 请在 config.py 中填写 XiaoMi_API_KEY（小米 MIMO OpenAPI）。")
        sys.exit(1)

    print("✅ 已从本目录加载 config.py（小米 MIMO）")
    print(f"   模型: {ACTIVE_MODEL} | 成功标签: {SUCCESS_TAG}")


def apply_gui_settings(
    *,
    library_id: str,
    api_key: str,
    library_type: str,
    zotero_storage_path: str,
    mimo_api_key: str,
    mimo_model: str,
    prompt_file_name: str = "prompt.md",
    prompt_template: str,
    item_types_to_process,
    target_collection_path,
    test_mode: bool,
    test_limit: int,
    success_tag: str,
    non_lit_tag: str,
    tags_skip_if_present=None,
    mimo_base_url: str = None,
):
    """由 GUI 注入参数；仅使用小米 MIMO。"""
    global config, LIBRARY_ID, API_KEY, LIBRARY_TYPE, ZOTERO_STORAGE_PATH
    global PROMPT_FILE_NAME, ITEM_TYPES_TO_PROCESS, TARGET_COLLECTION_PATH, TEST_MODE, TEST_LIMIT
    global ACTIVE_API_KEY, ACTIVE_MODEL, SUCCESS_TAG, NON_LIT_TAG
    global _PROMPT_TEMPLATE_OVERRIDE, TAGS_SKIP_IF_PRESENT

    config = None
    LIBRARY_ID = library_id
    API_KEY = api_key
    LIBRARY_TYPE = library_type
    ZOTERO_STORAGE_PATH = zotero_storage_path
    PROMPT_FILE_NAME = prompt_file_name
    ITEM_TYPES_TO_PROCESS = item_types_to_process
    TARGET_COLLECTION_PATH = target_collection_path
    TEST_MODE = test_mode
    TEST_LIMIT = test_limit
    ACTIVE_API_KEY = mimo_api_key
    ACTIVE_MODEL = mimo_model
    SUCCESS_TAG = success_tag
    NON_LIT_TAG = non_lit_tag
    _PROMPT_TEMPLATE_OVERRIDE = prompt_template
    MIMO_BASE_URL = mimo_base_url

    if tags_skip_if_present is None:
        TAGS_SKIP_IF_PRESENT = None
    elif isinstance(tags_skip_if_present, str):
        parts = [p.strip() for p in tags_skip_if_present.split(",") if p.strip()]
        TAGS_SKIP_IF_PRESENT = parts if parts else None
    else:
        TAGS_SKIP_IF_PRESENT = list(tags_skip_if_present)


# ================= 2. 功能函数定义 =================

def load_prompt(filename):
    """读取同目录下的 MD 提示词文件"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"错误：未找到文件 '{filename}'，请确保它和脚本在同一目录下。")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_keywords_from_filename(filename):
    """从文件名中提取关键词（标题部分）"""
    # 去除扩展名
    name = filename.replace('.pdf', '').strip()
    
    # 常见的文件名格式：
    # "作者 - 年份 - 标题.pdf"
    # "作者等 - 年份 - 标题.pdf"
    # "标题.pdf"
    
    # 尝试提取标题部分（通常在最后一个 " - " 之后）
    if ' - ' in name:
        parts = name.split(' - ')
        # 取最后一部分作为标题（通常是标题）
        if len(parts) >= 2:
            title = parts[-1].strip()
        else:
            title = name
    else:
        title = name
    
    # 提取关键词：去除短词（<3个字符）和常见停用词
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
    
    # 分割成单词，提取有意义的关键词
    # 先按空格分割，然后处理连字符
    words = []
    for part in title.lower().split():
        # 如果包含连字符，分别处理每个部分
        if '-' in part:
            words.extend(part.split('-'))
        else:
            words.append(part)
    
    keywords = []
    for word in words:
        # 去除标点符号，但保留字母和数字
        word_clean = ''.join(c for c in word if c.isalnum())
        # 只保留长度>=4的单词，且不在停用词列表中
        if len(word_clean) >= 4 and word_clean not in stop_words:
            keywords.append(word_clean)
    
    # 如果关键词太少，降低阈值
    if len(keywords) < 3:
        for word in words:
            word_clean = ''.join(c for c in word if c.isalnum())
            if len(word_clean) >= 3 and word_clean not in stop_words:
                keywords.append(word_clean)
    
    # 去重但保持顺序
    seen = set()
    keywords_unique = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            keywords_unique.append(kw)
    keywords = keywords_unique
    
    return keywords, title

def find_pdf_file(filename, search_dir):
    """根据文件名中的关键词在整个目录下递归搜索 PDF 文件"""
    if not os.path.exists(search_dir):
        return None
    
    # 提取关键词
    keywords, title = extract_keywords_from_filename(filename)
    
    if not keywords:
        print(f"   ⚠️  无法从文件名提取关键词: {filename}")
        return None
    
    print(f"   🔍 提取关键词: {', '.join(keywords[:8])}...")  # 显示前8个
    print(f"   🔍 标题: {title[:80]}...")  # 显示标题前80个字符
    
    # 递归搜索所有 PDF 文件
    best_match = None
    best_score = 0
    
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_lower = file.lower()
                file_no_ext = file_lower.replace('.pdf', '')
                
                # 方法1: 完全匹配优先
                if file == filename or file_no_ext == filename.lower().replace('.pdf', ''):
                    print(f"   ✅ 完全匹配: {file}")
                    return os.path.join(root, file)
                
                # 方法2: 检查标题是否包含在文件名中（去除作者和年份后）
                # 提取文件名中的标题部分（最后一个 " - " 之后）
                if ' - ' in file_no_ext:
                    file_title = file_no_ext.split(' - ')[-1].strip()
                else:
                    file_title = file_no_ext
                
                title_lower = title.lower().strip()
                file_title_lower = file_title.lower().strip()
                
                # 如果标题完全包含在文件名中，或者文件名完全包含在标题中
                # 使用更宽松的匹配：去除所有空格和标点后比较
                title_clean = ''.join(c for c in title_lower if c.isalnum() or c.isspace())
                file_title_clean = ''.join(c for c in file_title_lower if c.isalnum() or c.isspace())
                
                if title_lower in file_title_lower or file_title_lower in title_lower:
                    print(f"   ✅ 标题匹配: {file}")
                    return os.path.join(root, file)
                
                # 更宽松的匹配：检查标题的主要部分是否在文件名中
                if len(title_clean) > 20:  # 如果标题较长
                    title_main = title_clean[:50]  # 取前50个字符
                    if title_main in file_title_clean:
                        print(f"   ✅ 标题部分匹配: {file}")
                        return os.path.join(root, file)
                
                # 方法3: 计算关键词匹配分数
                matched_keywords = sum(1 for keyword in keywords if keyword in file_lower)
                score = matched_keywords / len(keywords) if keywords else 0
                
                # 记录最佳匹配（降低阈值到30%，并至少匹配3个关键词）
                if score > best_score and (score >= 0.3 or matched_keywords >= 3):
                    best_score = score
                    best_match = os.path.join(root, file)
    
    if best_match:
        print(f"   ✅ 找到匹配文件 (匹配度: {best_score*100:.1f}%): {os.path.basename(best_match)}")
        return best_match
    
    # 如果没找到，尝试更宽松的搜索：只匹配前几个关键词
    if len(keywords) >= 3:
        print(f"   🔄 尝试更宽松的搜索（只匹配前5个关键词）...")
        top_keywords = keywords[:5]
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_lower = file.lower()
                    matched = sum(1 for kw in top_keywords if kw in file_lower)
                    if matched >= 3:  # 至少匹配3个关键词
                        print(f"   ✅ 宽松匹配找到: {file}")
                        return os.path.join(root, file)
    
    print(f"   ❌ 未找到匹配文件")
    return None

def get_pdf_content(file_key, filename=None):
    """根据 Zotero 的 file_key 或文件名在本地查找 PDF 并提取文本"""
    pdf_path = None

    # 方法1: 如果提供了文件名，使用关键词在整个 zotero-pdf 目录下递归搜索
    if filename:
        pdf_path = find_pdf_file(filename, ZOTERO_STORAGE_PATH)

    # 方法2: 尝试使用 file_key 作为子目录名（标准 storage 结构）
    if not pdf_path:
        target_dir = os.path.join(ZOTERO_STORAGE_PATH, file_key)
        if os.path.exists(target_dir):
            try:
                pdf_files = [f for f in os.listdir(target_dir) if f.lower().endswith('.pdf')]
                if pdf_files:
                    pdf_path = os.path.join(target_dir, pdf_files[0])
            except (PermissionError, OSError) as e:
                print(f"   ⚠️  访问目录失败: {target_dir} - {str(e)}")

    # 方法3: 尝试标准 storage 目录（备选路径，如果需要可以配置）
    # 注意：如果您的 Zotero storage 路径与 ZOTERO_STORAGE_PATH 不同，可以在这里添加备选路径
    # 示例：
    # if not pdf_path:
    #     alt_path = r'C:\Users\YourName\Zotero\storage'  # 替换为您的备选路径
    #     alt_dir = os.path.join(alt_path, file_key)
    #     if os.path.exists(alt_dir):
    #         pdf_files = [f for f in os.listdir(alt_dir) if f.lower().endswith('.pdf')]
    #         if pdf_files:
    #             pdf_path = os.path.join(alt_dir, pdf_files[0])

    # 方法4: 如果还是找不到，在整个 zotero-pdf 目录下递归搜索所有 PDF
    if not pdf_path:
        # 尝试搜索包含 file_key 的文件名
        try:
            for root, dirs, files in os.walk(ZOTERO_STORAGE_PATH):
                for file in files:
                    if file.lower().endswith('.pdf') and file_key in file:
                        pdf_path = os.path.join(root, file)
                        break
                if pdf_path:
                    break
        except (PermissionError, OSError) as e:
            print(f"   ⚠️  搜索PDF文件时出错: {str(e)}")

    if not pdf_path:
        return None, f"未找到 PDF 文件 (file_key: {file_key}, filename: {filename})"

    # 验证文件是否可读且非空
    if not os.path.isfile(pdf_path):
        return None, f"PDF路径不是有效文件: {pdf_path}"

    if not os.access(pdf_path, os.R_OK):
        return None, f"PDF文件无读取权限: {pdf_path}"

    file_size = os.path.getsize(pdf_path)
    if file_size == 0:
        return None, f"PDF文件为空: {pdf_path}"

    if file_size < 100:  # 小于100字节的PDF很可能损坏
        return None, f"PDF文件过小可能已损坏 ({file_size} 字节): {pdf_path}"

    # 提取文本
    text_content = ""
    doc = None
    try:
        # 尝试打开PDF
        try:
            doc = fitz.open(pdf_path)
        except fitz.FileDataError as e:
            return None, f"PDF文件损坏或格式不正确: {str(e)}"
        except fitz.FileNotFoundError as e:
            return None, f"PDF文件未找到: {str(e)}"
        except Exception as e:
            return None, f"无法打开PDF文件: {str(e)}"

        # 验证PDF是否有页面
        if doc.page_count == 0:
            return None, f"PDF文件没有页面: {pdf_path}"

        # 为了节省 Token，通常只读前 30 页（涵盖正文，跳过部分参考文献）
        # 如果需要全文，去掉 [:30] 即可
        pages_to_read = min(30, doc.page_count)

        for page_num in range(pages_to_read):
            try:
                page = doc[page_num]
                page_text = page.get_text()
                # 确保返回的是字符串
                if isinstance(page_text, str):
                    text_content += page_text
                else:
                    text_content += str(page_text)
            except Exception as e:
                print(f"   ⚠️  读取第{page_num+1}页时出错: {str(e)}")
                # 继续处理其他页面而不是完全失败
                continue

        # 验证提取的文本是否有意义
        if not text_content or len(text_content.strip()) < 50:
            return None, f"PDF文本提取失败或内容过少 (提取了 {len(text_content)} 字符)"

    except Exception as e:
        return None, f"PDF 解析失败: {str(e)}"
    finally:
        # 确保文档被正确关闭
        if doc:
            try:
                doc.close()
            except Exception as e:
                print(f"   ⚠️  关闭PDF文档时出错: {str(e)}")

    return text_content, "Success"
    

def resolve_dynamic_path(path: str) -> str:
    """解析动态路径占位符
    - {{mmdd}} -> 当前月日 (如 0419)
    - 0-New/mmdd -> 0-New/0419
    """
    if not path:
        return path
    
    import datetime
    # 使用本地时间
    mmdd = datetime.datetime.now().strftime('%m%d')
    
    # 1. 替换通用占位符
    resolved = path.replace('{{mmdd}}', mmdd)
    
    # 2. 特殊处理：如果路径恰好是 "0-New/mmdd" (用户习惯)
    if resolved == '0-New/mmdd':
        resolved = f'0-New/{mmdd}'
        
    return resolved


def call_ai_analysis(paper_text, system_prompt):
    """调用小米 MIMO（OpenAI 兼容接口）"""
    import traceback

    max_retries = 2
    for attempt in range(max_retries):
        try:
            print(f"   🔄 尝试连接 MIMO API (尝试 {attempt + 1}/{max_retries})...")

            full_content = f"{system_prompt}\n\nPaper Content:\n\n{paper_text}"

            print(f"   📤 正在发送请求 (模型: {ACTIVE_MODEL})...")
            print(f"   ⏳ 请稍候，这可能需要 30-120 秒...")

            start_time = time.time()

            # 优先级：1. 手动指定 2. tp- 前缀自动检测 3. 默认
            if MIMO_BASE_URL:
                xiaomi_base_url = MIMO_BASE_URL
                print(f"   ℹ️  使用配置文件指定的 Base URL: {xiaomi_base_url}")
            elif ACTIVE_API_KEY and str(ACTIVE_API_KEY).startswith('tp-'):
                xiaomi_base_url = "https://token-plan-cn.xiaomimimo.com/v1"
                print(f"   ℹ️  检测到 Token Plan 密钥，自动切换至专属接口: {xiaomi_base_url}")
            else:
                xiaomi_base_url = "https://api.xiaomimimo.com/v1"

            client = OpenAI(
                api_key=ACTIVE_API_KEY,
                base_url=xiaomi_base_url,
            )
            response = client.chat.completions.create(
                model=ACTIVE_MODEL,
                messages=[{"role": "user", "content": full_content}],
            )
            elapsed_time = time.time() - start_time
            print(f"   ✅ API 响应成功 (耗时: {elapsed_time:.1f}秒)")
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            print(f"   ⚠️  响应为空，尝试重新生成...")

        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ AI 调用出错: {error_msg}")

            if "402" in error_msg or "insufficient_balance" in error_msg.lower():
                print(f"   💰 错误提示: 您的 API 账户余额不足！请前往小米 MIMO 开放平台充值或检查免费额度。")
                return None
            
            if '401' in error_msg or 'invalid_key' in error_msg.lower() or 'invalid api key' in error_msg.lower():
                print(f"   ❌ API Key 无效，请检查配置。如果是刚更新的 Token Plan Key，请确保已正确保存。")
                return None

            # 检查是否是模型名称错误
            if 'model' in error_msg.lower() or 'not found' in error_msg.lower():
                print(f"   ⚠️  模型名称可能不正确: {ACTIVE_MODEL}")
                if attempt < max_retries - 1:
                    pass # 会继续重试
                else:
                    return None
            # 如果是网络或超时错误，尝试重试
            if attempt < max_retries - 1:
                print(f"   🔄 等待 3 秒后重试...")
                time.sleep(3)
                continue
            else:
                # 最后一次尝试失败，打印详细错误
                print(f"   📋 详细错误信息:")
                traceback.print_exc()
                return None
    
    return None

def extract_one_sentence_summary(markdown_content):
    """从 Markdown 内容中提取一句话总结，返回简短的标题"""
    import re
    
    # 尝试多种可能的格式匹配
    patterns = [
        # 匹配：**一句话总结 (One-Sentence Summary)**：实际内容
        r'\*\*一句话总结[^*]*\*\*[：:]\s*([^<\n]{5,100})',  
        # 匹配：一句话总结：实际内容（无粗体）
        r'一句话总结[^：:]*[：:]\s*([^<\n]{5,100})',
        # 匹配：One-Sentence Summary：实际内容
        r'One-Sentence Summary[^：:]*[：:]\s*([^<\n]{5,100})',
        # 更宽松的匹配：包含"一句话总结"的行，提取冒号后的内容
        r'[一1][句话句].*?[总总][结结][^：:]*[：:]\s*([^<\n]{5,100})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, markdown_content, re.IGNORECASE | re.MULTILINE)
        if match:
            summary = match.group(1).strip()
            # 清理可能的标记符号和特殊字符
            summary = summary.replace('<', '').replace('>', '').replace('（', '').replace('）', '')
            # 移除LaTeX公式和其他特殊字符
            summary = re.sub(r'\$[^$]*\$', '', summary)  # 移除 $...$ 格式的LaTeX
            summary = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', summary)  # 移除 \command{...} 格式
            summary = re.sub(r'[^\w\s\u4e00-\u9fff，。、；：！？]', '', summary)  # 只保留中文、英文、数字和基本标点
            summary = summary.strip()
            
            # 如果清理后太短，返回None使用默认标题
            if len(summary) < 3:
                return None
                
            return summary
    
    # 如果没找到，返回默认值
    return None

def find_collection_by_path(zot, collection_path):
    """根据路径查找集合
    
    Args:
        zot: Zotero 客户端
        collection_path: 集合路径，用 '/' 分隔，如 "0 2025/12"
    
    Returns:
        集合的 key，如果找不到返回 None
    """
    if not collection_path:
        return None
    
    # 分割路径
    path_parts = [part.strip() for part in collection_path.split('/') if part.strip()]
    if not path_parts:
        return None
    
    # 获取所有集合（使用分页方式确保获取所有 collections）
    all_collections = []
    try:
        start = 0
        page_size = 100
        
        while True:
            try:
                page = zot.collections(limit=page_size, start=start)
                if not page:
                    break
                all_collections.extend(page)
                
                # 如果返回的数量少于 page_size，说明已经获取完所有数据
                if len(page) < page_size:
                    break
                
                start += page_size
            except Exception as page_error:
                error_msg = str(page_error)
                if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                    print(f"   ⚠️  获取集合列表超时（start={start}）: {page_error}")
                elif '403' in error_msg or 'Forbidden' in error_msg:
                    print(f"   ⚠️  获取集合列表权限不足（start={start}）: {page_error}")
                elif '404' in error_msg:
                    print(f"   ⚠️  库未找到（start={start}）: {page_error}")
                else:
                    print(f"   ⚠️  获取集合列表失败（start={start}）: {page_error}")
                break
    except Exception as e:
        error_msg = str(e)
        if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
            print(f"   ⚠️  获取集合列表超时: {e}")
        elif '403' in error_msg or 'Forbidden' in error_msg:
            print(f"   ⚠️  获取集合列表权限不足: {e}")
        elif '404' in error_msg:
            print(f"   ⚠️  库未找到: {e}")
        else:
            print(f"   ⚠️  获取集合列表失败: {e}")
        return None

    # 验证返回的数据
    if not all_collections:
        print(f"   ⚠️  未找到任何集合")
        return None

    if not isinstance(all_collections, (list, tuple)):
        print(f"   ⚠️  API返回的集合数据格式不正确: {type(all_collections)}")
        return None

    # 构建集合名称到key的映射（包括父集合信息）
    collections_map = {}
    for coll in all_collections:
        # 验证集合数据结构
        if not isinstance(coll, dict):
            print(f"   ⚠️  跳过无效的集合项（不是字典）: {type(coll)}")
            continue

        if 'data' not in coll:
            print(f"   ⚠️  跳过缺少'data'字段的集合: {coll.get('key', 'unknown')}")
            continue

        if 'key' not in coll:
            print(f"   ⚠️  跳过缺少'key'字段的集合")
            continue

        coll_data = coll['data']
        if not isinstance(coll_data, dict):
            print(f"   ⚠️  跳过'data'字段不是字典的集合: {coll.get('key', 'unknown')}")
            continue

        coll_name = coll_data.get('name', '')
        coll_key = coll['key']
        parent_key = coll_data.get('parentCollection', None)

        # 处理 parentCollection 可能是 False 的情况
        if parent_key is False:
            parent_key = None

        collections_map[coll_key] = {
            'name': coll_name,
            'parent': parent_key,
            'key': coll_key
        }

    if not collections_map:
        print(f"   ⚠️  没有有效的集合数据")
        return None
    
    # 打印所有集合信息（用于调试）
    print(f"   🔍 找到 {len(collections_map)} 个集合")
    
    # 搜索所有集合，找到目标路径
    # 先找到第一层的集合（不限制是否有父集合）
    first_level_candidates = []
    for coll_key, coll_info in collections_map.items():
        if coll_info['name'] == path_parts[0]:
            first_level_candidates.append((coll_key, coll_info))
    
    if not first_level_candidates:
        print(f"   ⚠️  未找到集合路径中的 '{path_parts[0]}' (层级 1)")
        # 显示所有第一层集合（没有父集合的）
        top_level = [c['name'] for c in collections_map.values() if c['parent'] is None]
        print(f"   💡 可用的顶级集合（前20个）: {', '.join(top_level[:20])}")
        # 也显示所有包含该名称的集合（模糊匹配，包括有父集合的）
        similar = [c['name'] for c in collections_map.values() if path_parts[0].lower() in c['name'].lower() or c['name'].lower() in path_parts[0].lower()]
        if similar:
            print(f"   💡 相似的集合名称（包含 '{path_parts[0]}'，包括所有层级）: {', '.join(similar[:20])}")
            # 显示这些相似集合的详细信息
            print(f"   🔍 相似集合的详细信息:")
            for coll_key, coll_info in collections_map.items():
                if path_parts[0].lower() in coll_info['name'].lower() or coll_info['name'].lower() in path_parts[0].lower():
                    parent_name = collections_map.get(coll_info['parent'], {}).get('name', 'None') if coll_info['parent'] else 'None'
                    print(f"      - {coll_info['name']} (Key: {coll_key}, 父集合: {parent_name})")
        # 搜索所有集合，看是否有完全匹配的（包括有父集合的）
        all_names = [c['name'] for c in collections_map.values()]
        exact_matches = [name for name in all_names if name == path_parts[0]]
        if exact_matches:
            print(f"   ⚠️  奇怪：找到了完全匹配的名称，但之前没找到")
        return None
    
    # 如果有多个匹配的第一层集合，打印它们的信息
    if len(first_level_candidates) > 1:
        print(f"   🔍 找到 {len(first_level_candidates)} 个匹配 '{path_parts[0]}' 的集合:")
        for coll_key, coll_info in first_level_candidates:
            parent_name = collections_map.get(coll_info['parent'], {}).get('name', 'None') if coll_info['parent'] else 'None'
            print(f"      - {coll_info['name']} (Key: {coll_key}, 父集合: {parent_name})")
    
    # 从第一层开始查找
    current_key = None
    for i, part in enumerate(path_parts):
        found = False
        candidates = []
        
        # 找到所有名称匹配的集合
        for coll_key, coll_info in collections_map.items():
            if coll_info['name'] == part:
                candidates.append((coll_key, coll_info))
        
        if not candidates:
            print(f"   ⚠️  未找到集合路径中的 '{part}' (层级 {i+1})")
            if i > 0:
                parent_name = collections_map.get(current_key, {}).get('name', 'unknown') if current_key else 'unknown'
                # 显示父集合下的所有子集合
                children = [c['name'] for c in collections_map.values() if c['parent'] == current_key]
                print(f"   💡 在父集合 '{parent_name}' 下的子集合: {', '.join(children[:20])}")
            return None
        
        # 根据层级选择正确的集合
        if i == 0:
            # 第一层：如果有多个匹配，优先选择没有父集合的
            candidates_without_parent = [c for c in candidates if c[1]['parent'] is None]
            if candidates_without_parent:
                current_key = candidates_without_parent[0][0]
            else:
                # 如果都有父集合，选择第一个
                current_key = candidates[0][0]
            found = True
            parent_name = collections_map.get(collections_map[current_key]['parent'], {}).get('name', 'None') if collections_map[current_key]['parent'] else 'None'
            print(f"   ✅ 找到第一层集合: {collections_map[current_key]['name']} (Key: {current_key}, 父集合: {parent_name})")
        else:
            # 后续层：必须父集合是上一层的key
            for coll_key, coll_info in candidates:
                if coll_info['parent'] == current_key:
                    current_key = coll_key
                    found = True
                    print(f"   ✅ 找到第{i+1}层集合: {coll_info['name']} (Key: {coll_key}, 父集合: {collections_map[current_key]['name']})")
                    break
        
        if not found:
            parent_name = collections_map.get(current_key, {}).get('name', 'unknown') if current_key else 'unknown'
            print(f"   ⚠️  未找到集合路径中的 '{part}' (层级 {i+1})，父集合: {parent_name}")
            # 显示父集合下的所有子集合
            children = [c['name'] for c in collections_map.values() if c['parent'] == current_key]
            print(f"   💡 在父集合 '{parent_name}' 下的子集合: {', '.join(children[:20])}")
            return None
    
    if current_key:
        final_name = collections_map[current_key]['name']
        print(f"   ✅ 找到目标集合: {final_name} (Key: {current_key})")
        return current_key
    else:
        print(f"   ⚠️  未找到集合路径: {collection_path}")
        return None

def add_tag_to_item(zot, item_key, tag_name):
    """给 Zotero 项目添加标签"""
    try:
        # 获取当前项目
        item = zot.item(item_key)
        current_tags = item['data'].get('tags', [])
        
        # 检查标签是否已存在
        tag_exists = any(tag.get('tag') == tag_name for tag in current_tags)
        
        if not tag_exists:
            # 添加新标签
            current_tags.append({'tag': tag_name})
            item['data']['tags'] = current_tags
            zot.update_item(item)
            print(f"   ✅ 已添加标签 '{tag_name}' 到论文")
        else:
            print(f"   ℹ️  标签 '{tag_name}' 已存在")
    except Exception as e:
        print(f"   ⚠️  添加标签失败: {str(e)}")

def save_note_to_zotero(zot, item_key, markdown_content):
    """将 AI 生成的 Markdown 转换为 HTML 并存入 Zotero
    
    Args:
        zot: Zotero 客户端
        item_key: 论文的 key
        markdown_content: AI 生成的 Markdown 内容
    """
    
    # 提取一句话总结作为笔记标题（简短版本，最多20字符）
    summary = extract_one_sentence_summary(markdown_content)
    if not summary:
        # 使用简短的默认标题
        note_title = "AI报告"
        print(f"   ⚠️  未能提取一句话总结，使用默认标题")
    else:
        # 限制summary在20字符以内
        max_summary_len = 20
        if len(summary) > max_summary_len:
            # 尝试在标点处截断
            for sep in ['。', '，', '.', ',', '；', ';']:
                idx = summary.find(sep, 0, max_summary_len)
                if idx > 5:  # 至少保留5个字符
                    summary = summary[:idx]
                    break
            else:
                # 如果没有合适的截断点，直接截断
                summary = summary[:max_summary_len]
        
        # 直接使用总结作为标题，不加前缀
        note_title = summary
        print(f"   📝 笔记标题: {note_title} (长度: {len(note_title)})")
    
    # Zotero 笔记本质是 HTML，为了让格式好看（表格、粗体），我们将 MD 转 HTML
    html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
    
    # 获取提供商后缀
    provider_name = "MIMO"
    
    # 加上标题和原始 MD 的提示
    final_note = f"""
    <h1>🤖 AI 深度阅读报告 - {provider_name}</h1>
    <hr>
    {html_content}
    <hr>
    <p style="color:gray; font-size:10px;">Generated by {provider_name} based on {PROMPT_FILE_NAME}</p>
    """
    
    try:
        # 创建笔记条目
        # 根据pyzotero文档，parentItem应该在顶层
        # 注意：Zotero的note类型不支持title字段，标题已包含在note内容的HTML中
        note_data = {
            'itemType': 'note',
            'parentItem': str(item_key),  # 确保是字符串
            'note': final_note,
            'tags': [{'tag': SUCCESS_TAG}]  # 给笔记打上标签
        }
        
        # 打印准备创建的数据结构
        print(f"   🔍 准备创建笔记:")
        print(f"      - 父项 Key: {item_key}")
        print(f"      - 笔记标题（在内容中）: {note_title}")
        print(f"      - 笔记内容长度: {len(final_note)} 字符")
        
        # 创建笔记
        print(f"   📤 正在调用 zot.create_items()...")
        try:
            created_items = zot.create_items([note_data])
        except Exception as api_error:
            error_msg = str(api_error)
            if '400' in error_msg:
                raise Exception(f"Zotero API请求格式错误: {error_msg}")
            elif '403' in error_msg or 'Write access denied' in error_msg:
                raise Exception(f"Zotero API写入权限不足: {error_msg}")
            elif '404' in error_msg:
                raise Exception(f"Zotero父项未找到 (key: {item_key}): {error_msg}")
            elif 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                raise Exception(f"Zotero API请求超时: {error_msg}")
            else:
                raise Exception(f"Zotero API调用失败: {error_msg}")

        # 验证返回值不为空
        if not created_items:
            raise Exception("Zotero API返回空响应，笔记创建状态未知")

        # 检查返回值
        print(f"   🔍 create_items() 返回类型: {type(created_items).__name__}")
        created_note_key = None
        if created_items:
            if isinstance(created_items, dict):
                print(f"   🔍 返回字典的键: {list(created_items.keys())[:5]}")

                # 验证响应结构包含expected keys
                if 'successful' not in created_items and 'failed' not in created_items:
                    print(f"   ⚠️  警告: API响应缺少'successful'和'failed'键")

                if 'successful' in created_items:
                    successful = created_items['successful']
                    if successful is None:
                        print(f"   ⚠️  'successful'字段为None")
                    elif isinstance(successful, dict):
                        # successful是一个字典，键是索引
                        for key, item in successful.items():
                            if isinstance(item, dict) and 'key' in item:
                                created_note_key = item['key']
                                print(f"   🔍 成功创建的笔记 Key: {created_note_key}")
                                print(f"   🔍 成功创建的笔记数据: {list(item.keys())[:5]}")
                            else:
                                print(f"   ⚠️  成功项缺少'key'字段: {item}")
                    elif isinstance(successful, (list, tuple)) and len(successful) > 0:
                        first_item = successful[0]
                        if isinstance(first_item, dict) and 'key' in first_item:
                            created_note_key = first_item['key']
                            print(f"   🔍 成功创建的笔记 Key: {created_note_key}")
                        else:
                            print(f"   ⚠️  成功项缺少'key'字段: {first_item}")
                    print(f"   🔍 成功创建: {len(successful) if isinstance(successful, (list, tuple, dict)) else 1} 个")

                if 'failed' in created_items:
                    failed = created_items['failed']
                    if failed:  # 如果有失败项
                        if isinstance(failed, dict):
                            print(f"   ⚠️  失败的项目详情:")
                            for key, error in failed.items():
                                print(f"      - 索引 {key}: {error}")
                            # 如果所有项都失败了，抛出异常
                            if not created_items.get('successful'):
                                first_error = next(iter(failed.values())) if failed else "未知错误"
                                raise Exception(f"Zotero笔记创建失败: {first_error}")
                        elif isinstance(failed, (list, tuple)):
                            for i, error in enumerate(failed):
                                print(f"      - 索引 {i}: {error}")
                            if not created_items.get('successful'):
                                first_error = failed[0] if failed else "未知错误"
                                raise Exception(f"Zotero笔记创建失败: {first_error}")
                        print(f"   ⚠️  失败: {len(failed) if isinstance(failed, (list, tuple, dict)) else 1} 个")
            elif isinstance(created_items, (list, tuple)):
                print(f"   🔍 返回列表长度: {len(created_items)}")
                if len(created_items) > 0:
                    first_item = created_items[0]
                    if isinstance(first_item, dict):
                        print(f"   🔍 第一个返回项的键: {list(first_item.keys())[:5]}")
                        if 'key' in first_item:
                            created_note_key = first_item['key']
                            print(f"   🔍 创建的笔记 Key: {created_note_key}")
                        else:
                            print(f"   ⚠️  返回项缺少'key'字段")
                else:
                    print(f"   ⚠️  API返回空列表")
            else:
                print(f"   ⚠️  意外的返回类型: {type(created_items)}")
        
        print(f"   ✅ API调用完成")
        
        # 验证笔记是否真的创建了 - 多次尝试，因为可能需要时间同步
        print(f"   🔍 验证笔记是否创建成功...")
        note_found = False
        note_key = None
        
        for attempt in range(3):  # 尝试3次
            time.sleep(2 if attempt > 0 else 1)  # 第一次等1秒，之后等2秒
            
            # 重新获取子项，检查笔记是否存在
            try:
                children_after = zot.children(item_key)
                print(f"   🔍 第{attempt+1}次验证：找到 {len(children_after)} 个子项")
                
                # 打印所有子项的类型（用于调试）
                print(f"   🔍 所有子项详细信息:")
                for child in children_after:
                    child_type = child['data'].get('itemType', 'unknown')
                    child_key = child.get('key', 'unknown')
                    child_title = child['data'].get('title', '')[:30] if child['data'].get('title') else '(无标题)'
                    parent_key = child['data'].get('parentItem', 'none')
                    # 如果是笔记类型，也打印部分内容
                    if child_type == 'note':
                        note_preview = child['data'].get('note', '')[:50].replace('\n', ' ')
                        print(f"      - {child_type}: {child_title}... (Key: {child_key}, 父项: {parent_key})")
                        print(f"        内容预览: {note_preview}...")
                    else:
                        print(f"      - {child_type}: {child_title}... (Key: {child_key}, 父项: {parent_key})")
                
                # 列出所有找到的笔记（用于调试）
                all_notes = [c for c in children_after if c['data']['itemType'] == 'note']
                print(f"   🔍 找到 {len(all_notes)} 个笔记子项")
                
                # 如果创建时返回了note_key，直接检查这个key是否存在
                if created_note_key:
                    matching_child = [c for c in children_after if c.get('key') == created_note_key]
                    if matching_child:
                        print(f"   ✅ 通过创建的Key找到了笔记: {created_note_key}")
                        note_found = True
                        note_key = created_note_key
                        child = matching_child[0]
                        child_title = child['data'].get('title', '')
                        parent_key = child['data'].get('parentItem', 'none')
                        print(f"      - 笔记 Key: {note_key}")
                        print(f"      - 笔记标题: {child_title}")
                        print(f"      - 父项 Key: {parent_key}")
                        if str(parent_key) == str(item_key):
                            print(f"      - ✅ 父项关联正确")
                        break
                
                for child in all_notes:
                    # Note类型没有title字段，所以child_title可能为空
                    child_title = child['data'].get('title', '') or '(无标题)'
                    child_note = child['data'].get('note', '')
                    child_key = child['key']
                    parent_key = child['data'].get('parentItem', 'none')
                    
                    # 打印所有笔记信息（用于调试）
                    note_preview = child_note[:50].replace('\n', ' ') if child_note else '(无内容)'
                    print(f"      - 笔记: {note_preview}... (Key: {child_key}, 父项: {parent_key})")
                    
                    # 检查是否是刚创建的笔记
                    # 优先检查父项是否匹配（最可靠的判断）
                    parent_matches = str(parent_key) == str(item_key)
                    
                    # 检查内容匹配（检查HTML转义后的内容）
                    # Note类型没有title字段，所以主要依赖内容匹配
                    content_matches = ("AI 深度阅读报告" in child_note or 
                                     "AI 深度阅读报告" in child_note.replace('&lt;', '<').replace('&gt;', '>') or
                                     "🤖" in child_note or
                                     note_title in child_note)  # 标题可能在内容中
                    
                    # 如果父项匹配且内容匹配，就认为找到了
                    if parent_matches and content_matches:
                        note_found = True
                        note_key = child_key
                        print(f"   ✅ 验证成功：找到笔记 (第{attempt+1}次尝试)")
                        print(f"      - 笔记 Key: {note_key}")
                        print(f"      - 父项 Key: {parent_key}")
                        print(f"      - ✅ 父项关联正确")
                        print(f"      - ✅ 内容匹配（包含AI报告标识）")
                        break
                    # 如果只有父项匹配且只有一个笔记，也认为找到了
                    elif parent_matches and len(all_notes) == 1:
                        note_found = True
                        note_key = child_key
                        print(f"   ✅ 验证成功：找到笔记（通过父项匹配，第{attempt+1}次尝试）")
                        print(f"      - 笔记 Key: {note_key}")
                        print(f"      - 父项 Key: {parent_key}")
                        print(f"      - ✅ 父项关联正确")
                        print(f"      - ⚠️  注意：这是唯一的笔记子项，已确认是刚创建的笔记")
                        break
                
                if note_found:
                    break
                    
            except Exception as verify_error:
                print(f"   ⚠️  验证时出错 (第{attempt+1}次): {verify_error}")
        
        if not note_found:
            print(f"   ⚠️  警告：保存后未找到笔记")
            print(f"      - 父项 Key: {item_key}")
            print(f"      - 期望标题: {note_title}")
            print(f"      - 可能原因：")
            print(f"        1. Zotero服务器需要更多时间同步")
            print(f"        2. 笔记可能创建在根目录而非子项")
            print(f"        3. 请手动刷新Zotero客户端查看")
        
        # 给父项（论文本身）也打上标签
        # 测试阶段暂时注释掉，后续可以补回来
        # add_tag_to_item(zot, item_key, 'AI_Read')
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ 保存笔记失败: {error_msg}")
        
        # 检查是否是权限错误
        if '403' in error_msg or 'Write access denied' in error_msg or 'UserNotAuthorisedError' in error_msg:
            print(f"\n   ⚠️  Zotero API Key 缺少写入权限！")
            print(f"   📋 请按以下步骤修复：")
            print(f"   1. 访问: https://www.zotero.org/settings/keys")
            print(f"   2. 找到您的 API Key (或创建新的)")
            print(f"   3. 确保勾选了 'Allow library access' 和 'Allow notes creation' 权限")
            print(f"   4. 如果使用现有 Key，点击 'Edit' 添加写入权限")
            print(f"   5. 如果创建新 Key，确保选择 'Read/Write' 权限")
            print(f"   6. 更新代码中的 API_KEY 配置\n")
        
        # 重新抛出异常，让调用者知道保存失败
        raise

# ================= 3. 主程序流程 =================

def main():
    global _PROMPT_TEMPLATE_OVERRIDE
    print("🚀 程序启动...")

    # 1. 初始化 Zotero 客户端
    zot = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY)

    # 2. 读取提示词模板（GUI 可注入全文，否则从文件加载）
    try:
        if _PROMPT_TEMPLATE_OVERRIDE is not None:
            prompt_template = _PROMPT_TEMPLATE_OVERRIDE
            print(f"✅ 已使用界面中的提示词模板 ({len(prompt_template)} 字符)")
        else:
            prompt_template = load_prompt(PROMPT_FILE_NAME)
            print(f"✅ 已加载提示词模板: {PROMPT_FILE_NAME}")
    except Exception as e:
        print(f"❌ 加载提示词模板失败: {e}")
        return

    # 3. 查找目标集合（如果指定了）
    target_collection_key = None
    if TARGET_COLLECTION_PATH:
        # 解析动态路径
        resolved_path = resolve_dynamic_path(TARGET_COLLECTION_PATH)
        if resolved_path != TARGET_COLLECTION_PATH:
            print(f"📅 动态路径解析: {TARGET_COLLECTION_PATH} -> {resolved_path}")
            
        print(f"📁 正在查找目标集合: {resolved_path}")
        target_collection_key = find_collection_by_path(zot, resolved_path)
        if not target_collection_key:
            print(f"❌ 未找到目标集合，程序退出")
            return
        print(f"✅ 将只处理该集合中的文献")
    else:
        print(f"📁 未指定集合，将处理整个库中的所有文献")
    
    # 4. 获取文献列表
    if target_collection_key:
        # 使用 collection_items() 方法获取集合中的文献
        collection_info = f"集合 '{TARGET_COLLECTION_PATH}'"
        print(f"📥 正在获取 {collection_info} 中的文献列表...")
        try:
            all_items = zot.collection_items(target_collection_key)
            print(f"✅ 总共找到 {len(all_items)} 个文献")
            
            # 过滤掉 note 和 attachment 类型的项目，只保留真正的文献
            valid_items = []
            skipped_types = []
            for item in all_items:
                item_type = item['data'].get('itemType', 'unknown')
                if item_type in ['note', 'attachment']:
                    skipped_types.append(item_type)
                    continue
                valid_items.append(item)
            
            if skipped_types:
                print(f"   ⚠️  过滤掉 {len(skipped_types)} 个非文献项目 (类型: {set(skipped_types)})")
            
            all_items = valid_items
            print(f"✅ 过滤后找到 {len(all_items)} 个文献项目")
            
            # 打印获取到的文献信息（用于调试）
            if all_items:
                print(f"   🔍 目标集合中的文献列表:")
                for i, item in enumerate(all_items, 1):
                    title = item['data'].get('title', '无标题')[:50]
                    item_type = item['data'].get('itemType', 'unknown')
                    item_key = item.get('key', 'unknown')
                    print(f"      {i}. [{item_type}] {title}... (Key: {item_key})")
        except Exception as e:
            print(f"   ⚠️  获取集合文献时出错: {e}")
            return
    else:
        # 获取整个库的文献
        if TEST_MODE:
            print(f"📥 正在获取 Zotero 文献列表（测试模式：仅获取前 {TEST_LIMIT} 个）...")
            try:
                all_items = zot.items(start=0, limit=TEST_LIMIT)
                print(f"✅ 已获取 {len(all_items)} 个文献（测试模式）")
            except Exception as e:
                print(f"   ⚠️  获取文献时出错: {e}")
                return
        else:
            print("📥 正在获取整个库中的文献列表...")
            # 获取所有项目（使用分页）
            all_items = []
            start = 0
            batch_size = 100  # 每次获取100个
            
            while True:
                try:
                    batch = zot.items(start=start, limit=batch_size)
                    if not batch:
                        break
                    all_items.extend(batch)
                    print(f"   已获取 {len(all_items)} 个文献...")
                    
                    # 如果返回的数量少于 batch_size，说明已经获取完所有数据
                    if len(batch) < batch_size:
                        break
                    
                    start += batch_size
                except Exception as e:
                    print(f"   ⚠️  获取文献时出错: {e}")
                    break
            
            print(f"✅ 总共找到 {len(all_items)} 个文献")
    
    # 统计信息
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, item in enumerate(all_items, 1):
        title = item['data'].get('title', '无标题')
        item_key = item['key']
        item_type = item['data'].get('itemType', '')
        
        # 跳过 note 和 attachment 类型（这些不能作为父项），并加对应 non-read 标签
        if item_type in ['note', 'attachment']:
            print(f"\n[{idx}/{len(all_items)}] 跳过非文献项目: {title[:60]}... (类型: {item_type})")
            add_tag_to_item(zot, item_key, NON_LIT_TAG)
            skipped_count += 1
            continue
        
        # 如果设置了文献类型过滤，只处理指定类型，不符合的也加 NON_LIT_TAG
        if ITEM_TYPES_TO_PROCESS is not None:
            if item_type not in ITEM_TYPES_TO_PROCESS:
                add_tag_to_item(zot, item_key, NON_LIT_TAG)
                continue  # 跳过不符合类型的文献
        
        # --- 检查：是否已经分析过？ ---
        item_tags = item['data'].get('tags', [])
        skip_set = TAGS_SKIP_IF_PRESENT
        if skip_set is None:
            skip_set = {SUCCESS_TAG, "MIMO_read"}
        else:
            skip_set = set(skip_set)
        has_processed_tag = any(tag.get("tag") in skip_set for tag in item_tags)
        
        # 获取子条目，寻找 PDF 附件
        children = zot.children(item_key)
        pdf_key = None
        pdf_filename = None
        
        for child in children:
            # 寻找 PDF 附件的 key 和文件名
            if child['data']['itemType'] == 'attachment' and child['data'].get('contentType') == 'application/pdf':
                if not pdf_key:  # 只取第一个 PDF 附件
                    pdf_key = child['key']
                    # 尝试多个可能的字段名获取文件名
                    pdf_filename = (child['data'].get('filename') or 
                                  child['data'].get('title') or 
                                  child['data'].get('name') or 
                                  '')  # 获取文件名
        
        # 显示进度
        print(f"\n[{idx}/{len(all_items)}] 处理文献: {title[:60]}...")
        
        # 如果已有处理成功的标签，说明已处理过，跳过
        if has_processed_tag:
            print(f"   ⏭️  跳过 (已处理 - 检测到模型分析标签)")
            skipped_count += 1
            continue
            
        # --- 处理：读取 PDF -> AI 分析 -> 保存 ---
        print(f"📖 正在读取: {title} ...")
        
        # 如果没有找到PDF附件，尝试使用标题在ZOTERO_STORAGE_PATH中搜索
        if not pdf_key:
            print(f"   ⚠️  Zotero中未找到PDF附件，尝试在本地存储路径中搜索...")
            # 使用论文标题搜索PDF文件
            pdf_path = find_pdf_file(title, ZOTERO_STORAGE_PATH)
            if pdf_path:
                print(f"   ✅ 在本地找到PDF文件: {os.path.basename(pdf_path)}")
                # 直接读取PDF文件
                try:
                    doc = fitz.open(pdf_path)
                    pdf_text = ""
                    for page in doc[:30]:  # 只读前30页
                        page_text = page.get_text()
                        if isinstance(page_text, str):
                            pdf_text += page_text
                        else:
                            pdf_text += str(page_text)
                    doc.close()
                    status = "Success"
                    print(f"   ✅ PDF读取成功 (内容长度: {len(pdf_text)} 字符)")
                except Exception as e:
                    print(f"   ❌ PDF读取失败: {str(e)}")
                    error_count += 1
                    continue
            else:
                print(f"   ❌ 在本地存储路径中也未找到PDF文件")
                skipped_count += 1
                continue
        else:
            # 使用Zotero附件的方式读取
            if pdf_filename:
                print(f"   🔍 Zotero 文件名: {pdf_filename}")
            else:
                print(f"   ⚠️  未获取到文件名，尝试使用论文标题搜索")
                # 如果没有文件名，使用论文标题作为搜索关键词
                pdf_filename = title
            
            pdf_text, status = get_pdf_content(pdf_key, pdf_filename)
            if not pdf_text:
                print(f"   ❌ 读取失败: {status}")
                error_count += 1
                continue
            
        print(f"🧠 正在请求 AI 分析 (约需 30-60秒)...")
        ai_result = call_ai_analysis(pdf_text, prompt_template)
        
        if ai_result:
            print(f"   💾 正在保存笔记到 Zotero...")
            try:
                save_note_to_zotero(zot, item_key, ai_result)
                # 保存成功后，添加成功标签
                add_tag_to_item(zot, item_key, SUCCESS_TAG)
                print(f"   ✅ 完成!")
                processed_count += 1
            except Exception as e:
                print(f"   ⚠️  保存失败，跳过...")
                error_count += 1
                # 不中断程序，继续处理下一个项目
        else:
            print(f"   ⚠️  AI 分析失败，跳过此项目")
            error_count += 1
        
        # 显示当前统计
        print(f"   📊 进度: 已处理 {processed_count} | 已跳过 {skipped_count} | 错误 {error_count}")
        
        # 休息一下，避免触发 API 频率限制
        time.sleep(2)
    
    # 最终统计
    print(f"\n{'='*60}")
    if TEST_MODE:
        print(f"📊 测试处理完成！(测试模式：仅处理前 {TEST_LIMIT} 个)")
    else:
        print(f"📊 处理完成！")
    print(f"   处理文献数: {len(all_items)} 个")
    print(f"   成功处理: {processed_count} 个")
    print(f"   已跳过: {skipped_count} 个（已处理或无PDF）")
    print(f"   错误: {error_count} 个")
    print(f"{'='*60}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        bootstrap_cli()
        main()
    else:
        print("学生版默认使用图形界面。请运行：")
        print("  python gui_mimo_student.py")
        print("若仅需命令行（读取本目录 config.py），请运行：")
        print("  python reader_mimo_student.py --cli")