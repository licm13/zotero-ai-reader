import json
import os
import re
from pyzotero import zotero
from google import genai
import config

# ================= 配置 =================
PROFILE_FILE = 'user_profile.json'
ANALYSIS_LIMIT = 20  # 分析最近多少篇文献的笔记来提取品味

# 您的基础画像 (静态部分)
BASE_PROFILE = """
Name: Chengming Li (Professor, SCUT/Tsinghua)
Field: Hydrology, Remote Sensing, Hydro-climatology.
Core Interests: 
- Evapotranspiration (ET) & Vegetation processes.
- Hydrological Extremes: Flash Drought, Flood, Drought-Flood Abrupt Alternation (DFA).
- Methodology: Deep Learning (LSTM/CNN), Triple Collocation, Data Fusion, Uncertainty Analysis.
"""

def extract_content_from_note(note_html):
    """从笔记HTML中提取纯文本内容"""
    text = re.sub(r'<[^>]+>', ' ', note_html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:2000]  # 限制长度以节省 Token

def generate_profile(notes_text):
    """调用 AI 生成画像"""
    print("🧠 正在分析您的科研品味...")
    client = genai.Client(api_key=config.AI_API_KEY)
    
    prompt = f"""
    You are a Research Assistant analyzing the "Research Taste" of a Professor in Hydrology.
    
    BASE PROFILE:
    {BASE_PROFILE}
    
    RECENTLY READ PAPERS (Notes):
    {notes_text}
    
    TASK:
    Analyze the user's recent reading patterns and generate a JSON profile.
    1. **Dynamic Interests**: What specific problems are they focusing on *right now*? (e.g., "Moving from pure deep learning to physics-informed AI")
    2. **Idea Lab Categories**: Suggest 3-5 high-level "Scientific Question" categories for their "Idea Lab" folder.
    
    OUTPUT JSON FORMAT:
    {{
        "summary": "A short summary of current research taste...",
        "focus_areas": ["Area 1", "Area 2"],
        "idea_lab_suggestions": [
            {{ "name": "Mechanism/Phase Transitions", "description": "For DFA and thresholds" }},
            {{ "name": "Methodology/Physics-AI Fusion", "description": "Combining physical laws with ML" }}
        ]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=config.AI_MODEL,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ AI 分析失败: {e}")
        return None

def main():
    print("🚀 启动 Profiler (品味提取器)...")
    zot = zotero.Zotero(config.LIBRARY_ID, config.LIBRARY_TYPE, config.API_KEY)
    
    # 获取最近有 gemini_read 标签的条目
    print(f"📥 获取最近 {ANALYSIS_LIMIT} 篇已读文献...")
    items = zot.items(tag='gemini_read', limit=ANALYSIS_LIMIT, sort='dateModified', direction='desc')
    
    notes_content = []
    for item in items:
        # 获取子笔记
        children = zot.children(item['key'])
        for child in children:
            if child['data']['itemType'] == 'note':
                note_text = extract_content_from_note(child['data']['note'])
                if len(note_text) > 50: # 忽略太短的
                    title = item['data'].get('title', 'Untitled')
                    notes_content.append(f"--- Paper: {title} ---\n{note_text}")
                    break
    
    if not notes_content:
        print("⚠️ 未找到足够的笔记内容。请先运行 reader.py 处理一些文献。")
        return

    # 生成画像
    combined_text = "\n".join(notes_content)
    profile_data = generate_profile(combined_text)
    
    if profile_data:
        # 融合基础信息
        final_profile = {
            "base_info": BASE_PROFILE,
            "dynamic_analysis": profile_data,
            "updated_at": "Today"
        }
        
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_profile, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 画像已更新并保存至: {PROFILE_FILE}")
        print(f"🔍 当前焦点: {json.dumps(profile_data.get('focus_areas', []), ensure_ascii=False)}")
    else:
        print("❌ 生成失败")

if __name__ == "__main__":
    main()