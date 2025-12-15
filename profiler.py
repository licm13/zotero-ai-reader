#!/usr/bin/env python3
"""
Zotero AI Research Taste Profiler
==================================

Analyzes your recent reading patterns to generate a dynamic user profile.
This profile is used by organizer.py to customize classification logic.

Workflow:
1. Fetches recent papers with 'gemini_read' tag
2. Extracts content from AI-generated notes
3. Uses AI to analyze research taste and current focus
4. Outputs user_profile.json for organizer.py

Author: Prof. Chengming Li (SCUT)
"""

import json
import os
import re
import sys
from datetime import datetime
from pyzotero import zotero
from google import genai

# 配置加载
from config_loader import get_config_from_args_or_interactive

config = get_config_from_args_or_interactive()
if config is None:
    print("❌ 无法加载配置文件，程序退出")
    sys.exit(1)

# ================= Configuration =================

PROFILE_FILE = 'user_profile.json'
ANALYSIS_LIMIT = 20  # Analyze last N papers with gemini_read tag

# Base profile (static information)
BASE_PROFILE = {
    "name": "Prof. Chengming Li",
    "affiliation": "SCUT / Tsinghua University",
    "field": "Hydrology, Remote Sensing, Hydro-climatology",
    "core_interests": [
        "Evapotranspiration (ET) & Vegetation Processes",
        "Hydrological Extremes: Flash Drought, Flood, DFA",
        "Deep Learning (LSTM/CNN) for Hydrology",
        "Triple Collocation & Uncertainty Analysis",
        "Data Fusion & Remote Sensing Retrieval"
    ],
    "methodologies": [
        "Physics-informed Deep Learning",
        "Triple Collocation",
        "Multi-source Data Fusion",
        "Remote Sensing Retrieval"
    ]
}

# ================= Helper Functions =================

def extract_content_from_note(note_html):
    """Extract plain text from HTML note, limit length to save tokens"""
    text = re.sub(r'<[^>]+>', ' ', note_html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:2000]  # Limit to 2000 chars per note

def generate_dynamic_profile(notes_text):
    """
    Use AI to analyze research taste from recent reading patterns
    Returns dynamic profile dict or None if failed
    """
    print("🧠 Analyzing your research taste with AI...")

    client = genai.Client(api_key=config.AI_API_KEY)

    # Format base profile for prompt
    base_info = f"""
Name: {BASE_PROFILE['name']} ({BASE_PROFILE['affiliation']})
Field: {BASE_PROFILE['field']}
Core Interests: {', '.join(BASE_PROFILE['core_interests'])}
Methodologies: {', '.join(BASE_PROFILE['methodologies'])}
"""

    prompt = f"""You are a Research Assistant analyzing the "Research Taste" of a Professor in Hydrology.

BASE PROFILE (Static Information):
{base_info}

RECENT READING HISTORY (Last {ANALYSIS_LIMIT} Papers):
{notes_text}

TASK:
Analyze the user's recent reading patterns and generate a dynamic profile that captures:
1. **Current Research Focus**: What specific problems/questions are they exploring RIGHT NOW?
2. **Emerging Interests**: Any new directions or methodologies they're moving toward?
3. **Key Themes**: What underlying themes or mechanisms appear repeatedly?
4. **Idea Lab Suggestions**: Based on their taste, suggest 3-5 scientific question categories for their "Idea Lab" structure.

OUTPUT JSON FORMAT:
{{
    "summary": "A 2-3 sentence summary of current research taste and focus...",
    "focus_areas": ["Area 1", "Area 2", "Area 3"],
    "emerging_interests": ["Interest 1", "Interest 2"],
    "key_themes": ["Theme 1", "Theme 2", "Theme 3"],
    "idea_lab_suggestions": [
        {{
            "category": "Mechanism/Phase Transitions",
            "description": "For studying DFA, flash drought, and abrupt transitions",
            "rationale": "Strong interest in threshold behavior and rapid onset events"
        }},
        {{
            "category": "Data Philosophy/Signal Purification",
            "description": "For uncertainty analysis and quality control",
            "rationale": "Frequent use of triple collocation and data fusion methods"
        }}
    ]
}}

Important: Base suggestions on ACTUAL patterns in the reading history, not just the base profile.
"""

    try:
        response = client.models.generate_content(
            model=config.AI_MODEL,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )

        result = json.loads(response.text)
        print("✅ AI analysis completed")
        return result

    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        return None

# ================= Main Processing =================

def main():
    print("=" * 70)
    print("🚀 Zotero Research Taste Profiler")
    print("=" * 70)
    print(f"Analyzing last {ANALYSIS_LIMIT} papers with 'gemini_read' tag...")
    print("=" * 70)

    # Initialize Zotero
    zot = zotero.Zotero(config.LIBRARY_ID, config.LIBRARY_TYPE, config.API_KEY)

    # Fetch recent papers with gemini_read tag
    print(f"\n📥 Fetching recent papers...")
    try:
        items = zot.items(
            tag='gemini_read',
            limit=ANALYSIS_LIMIT,
            sort='dateModified',
            direction='desc'
        )
        print(f"   Found: {len(items)} papers")
    except Exception as e:
        print(f"❌ Failed to fetch items: {e}")
        return

    if not items:
        print("\n⚠️  No papers found with 'gemini_read' tag.")
        print("💡 Tip: Run reader.py first to analyze some papers.")
        return

    # Extract notes content
    print("\n📝 Extracting notes content...")
    notes_content = []
    processed_count = 0

    for item in items:
        title = item['data'].get('title', 'Untitled')

        # Get child notes
        try:
            children = zot.children(item['key'])

            for child in children:
                if child['data']['itemType'] == 'note':
                    note_html = child['data'].get('note', '')
                    note_text = extract_content_from_note(note_html)

                    if len(note_text) > 50:  # Ignore very short notes
                        notes_content.append(f"--- Paper: {title} ---\n{note_text}")
                        processed_count += 1
                        break  # Only take first note per paper

        except Exception as e:
            print(f"   ⚠️  Failed to process: {title[:50]}... ({e})")
            continue

    print(f"   Processed: {processed_count} notes")

    if not notes_content:
        print("\n⚠️  No valid notes found.")
        print("💡 Tip: Ensure reader.py has generated notes for your papers.")
        return

    # Generate dynamic profile with AI
    print("\n🔍 Analyzing research patterns...")
    combined_text = "\n\n".join(notes_content)
    dynamic_profile = generate_dynamic_profile(combined_text)

    if not dynamic_profile:
        print("❌ Failed to generate profile")
        return

    # Combine with base profile
    final_profile = {
        "base_info": BASE_PROFILE,
        "dynamic_analysis": dynamic_profile,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "papers_analyzed": processed_count,
            "analysis_limit": ANALYSIS_LIMIT
        }
    }

    # Save to file
    try:
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_profile, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Profile saved to: {PROFILE_FILE}")

    except Exception as e:
        print(f"\n❌ Failed to save profile: {e}")
        return

    # Display summary
    print("\n" + "=" * 70)
    print("📊 Profile Summary")
    print("=" * 70)
    print(f"Papers Analyzed: {processed_count}")
    print(f"\nCurrent Focus:")
    print(f"  {dynamic_profile.get('summary', 'N/A')}")
    print(f"\nFocus Areas:")
    for area in dynamic_profile.get('focus_areas', []):
        print(f"  • {area}")
    print(f"\nIdea Lab Suggestions:")
    for suggestion in dynamic_profile.get('idea_lab_suggestions', []):
        print(f"  • {suggestion.get('category', 'N/A')}")
        print(f"    → {suggestion.get('description', '')}")
    print("=" * 70)
    print("\n🎉 Done! You can now run organizer.py to classify papers using this profile.")

if __name__ == "__main__":
    main()
