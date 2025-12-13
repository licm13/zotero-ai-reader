#!/usr/bin/env python3
"""
Zotero AI-Powered Paper Organizer
Automatically classifies papers into collections based on AI-generated notes.

Key Optimizations:
1. Local caching of collection IDs to minimize API calls
2. Compact prompt design to reduce token usage
3. Batch processing for efficiency
4. Support for targeted collection processing
"""

import time
import json
import math
import os
from pyzotero import zotero
from google import genai
import config

# ================= 1. Configuration =================

# Target collection to process (None = process entire library)
TARGET_COLLECTION_PATH = getattr(config, 'TARGET_COLLECTION_PATH', None)

# Processing settings
DRY_RUN = True                      # True = test mode, False = actually move items
BATCH_SIZE = 5                      # Number of papers to classify per API call
AUTO_TAG_NAME = "auto_organized"    # Tag to prevent duplicate processing
CACHE_FILE = "collections_cache.json"  # Local cache for collection IDs

# ================= 2. Taxonomy Definition =================

# Idea-driven taxonomy structure (optimized for token usage)
TAXONOMY_STRUCTURE = """
Preferred Collection Taxonomy (User: Hydrology Professor, Focus: ET/Flash Drought/DFA/AI):

1. Extremes×Mechanisms
   - Flash Drought Dynamics
   - DFA×Land-Atmosphere
   - Flood Early Warning

2. AI×Hydrology Applications
   - Physics-Informed ML
   - Deep Learning for Extremes
   - Hybrid Modeling

3. Data×Uncertainty
   - Triple Collocation & QA
   - Multi-Source Fusion
   - Satellite×In-situ Integration

4. Vegetation×Water Coupling
   - VOD×Plant Hydraulics
   - ET×GPP Coupling
   - Drought×Vegetation Response

5. Global Products×Datasets
   - GRACE×Water Storage
   - ET Product Intercomparison
   - Precipitation Products

6. Reviews×Synthesis
   - Methodology Reviews
   - Domain Reviews

Notes:
- Use exact paths (e.g., "Extremes×Mechanisms/Flash Drought Dynamics")
- Return "Unclassified" if unsure
- Match papers to most specific subcategory
"""

# ================= 3. Cache Management =================

def load_cache():
    """Load collection ID cache from disk"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load cache: {e}")
    return {}

def save_cache(cache):
    """Save collection ID cache to disk"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  Failed to save cache: {e}")

def refresh_cache_from_zotero(zot):
    """Fetch all collections from Zotero and build cache"""
    print("🔄 Refreshing collection cache from Zotero...")
    try:
        all_colls = zot.collections()
        cache = {}

        # Build mapping: {name: key, parent: parent_key}
        for c in all_colls:
            name = c['data']['name']
            key = c['key']
            parent = c['data'].get('parentCollection', None)

            cache[name] = {
                'key': key,
                'parent': parent if parent else None
            }

        save_cache(cache)
        print(f"✅ Cached {len(cache)} collections")
        return cache
    except Exception as e:
        print(f"❌ Failed to fetch collections: {e}")
        return {}

# ================= 4. Collection Management =================

def find_collection_by_path(zot, collection_path, cache):
    """
    Find collection key by path (e.g., "Parent/Child")
    Uses cache first, falls back to Zotero API if needed
    """
    if not collection_path:
        return None

    parts = [p.strip() for p in collection_path.split('/') if p.strip()]
    if not parts:
        return None

    # Try to find in cache
    current_parent = None
    for i, part in enumerate(parts):
        if part not in cache:
            print(f"   ⚠️  Collection '{part}' not in cache, refreshing...")
            cache = refresh_cache_from_zotero(zot)
            if part not in cache:
                print(f"   ❌ Collection '{part}' not found")
                return None

        # Verify parent relationship (except for top level)
        if i > 0:
            expected_parent = cache[parts[i-1]]['key']
            actual_parent = cache[part].get('parent')
            if actual_parent != expected_parent:
                # Multiple collections with same name - need to disambiguate
                # For now, just warn
                print(f"   ⚠️  Warning: '{part}' has different parent than expected")

        current_parent = cache[part]['key']

    return current_parent

def ensure_collection_path(zot, path, cache):
    """
    Create collection path if it doesn't exist
    Returns the final collection key
    """
    if not path or path == "Unclassified":
        return None

    parts = [p.strip() for p in path.split('/') if p.strip()]
    parent_key = None

    for part in parts:
        # Check if collection exists in cache
        if part in cache:
            coll_info = cache[part]

            # Verify parent matches (except top level)
            if parent_key and coll_info.get('parent') != parent_key:
                # Collision: same name, different parent
                # Need to create new collection
                found_key = None
            else:
                found_key = coll_info['key']
        else:
            found_key = None

        # Create if doesn't exist
        if not found_key:
            if DRY_RUN:
                print(f"      [Dry Run] Would create: {part}")
                found_key = f"fake_{part}_{parent_key or 'root'}"
            else:
                print(f"      🔨 Creating collection: {part}")
                try:
                    payload = {'name': part}
                    if parent_key:
                        payload['parentCollection'] = parent_key

                    res = zot.create_collections([payload])
                    if res and 'successful' in res:
                        # Extract key from response
                        success_dict = res['successful']
                        found_key = list(success_dict.values())[0]['key']

                        # Update cache
                        cache[part] = {
                            'key': found_key,
                            'parent': parent_key
                        }
                        save_cache(cache)
                        print(f"      ✅ Created: {part} (Key: {found_key})")
                    else:
                        print(f"      ❌ Creation failed: {res}")
                        return None
                except Exception as e:
                    print(f"      ❌ Error creating '{part}': {e}")
                    return None

        parent_key = found_key

    return parent_key

# ================= 5. AI Classification =================

def extract_keywords_from_note(note_content):
    """Extract keywords/tags from AI-generated note"""
    import re

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', note_content)

    # Look for common keyword patterns
    patterns = [
        r'(?:Keywords|关键词|论文分类|Tags)[：:]\s*(.+?)(?:\n|$)',
        r'(?:分类|Classification)[：:]\s*(.+?)(?:\n|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()

    # Fallback: extract first 200 chars after "Summary" or "总结"
    summary_match = re.search(r'(?:Summary|总结)[：:]\s*(.{1,200})', text, re.IGNORECASE)
    if summary_match:
        return summary_match.group(1).strip()

    return ""

def ai_classify_batch(batch_items, ai_model, ai_key):
    """
    Classify a batch of papers using AI

    Optimizations:
    - Sends only taxonomy structure (not all existing collections)
    - Compact prompt format
    - JSON output for easy parsing
    """
    client = genai.Client(api_key=ai_key)

    # Format papers (compact)
    papers_list = []
    for i, item in enumerate(batch_items):
        papers_list.append(f"{i}|{item['title'][:80]}|{item['keywords'][:100]}")

    papers_text = "\n".join(papers_list)

    # Compact prompt (reduced tokens)
    prompt = f"""{TAXONOMY_STRUCTURE}

TASK: Classify papers by format "ID|Title|Keywords". Return JSON: {{"0": "Path/Subpath", "1": "Path/Subpath", ...}}

Papers:
{papers_text}

JSON:"""

    try:
        response = client.models.generate_content(
            model=ai_model,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )

        result = json.loads(response.text)
        print(f"   🤖 AI classified {len(result)} papers")
        return result

    except Exception as e:
        print(f"   ❌ AI classification error: {e}")
        return {}

# ================= 6. Item Processing =================

def move_item_to_collection(zot, item, target_key):
    """Move item to target collection and add tag"""
    if not target_key or target_key.startswith("fake_"):
        return

    if DRY_RUN:
        return

    try:
        # Check if already in collection
        current_colls = item.get('collections', [])
        if target_key in current_colls:
            print(f"      ℹ️  Already in target collection")
            return

        # Add to collection
        zot.addto_collection(target_key, item)

        # Add tag
        current_tags = item.get('tags', [])
        tag_names = [t.get('tag', '') for t in current_tags]

        if AUTO_TAG_NAME not in tag_names:
            current_tags.append({'tag': AUTO_TAG_NAME})
            item['tags'] = current_tags
            zot.update_item(item)

        print(f"      ✅ Moved to collection")

    except Exception as e:
        print(f"      ❌ Move failed: {e}")

# ================= 7. Main Processing =================

def main():
    print("=" * 60)
    print("🤖 Zotero AI Paper Organizer")
    print("=" * 60)
    print(f"Mode: {'🧪 DRY RUN (Test Mode)' if DRY_RUN else '🚀 LIVE MODE'}")
    print(f"Batch Size: {BATCH_SIZE}")
    print(f"Target Collection: {TARGET_COLLECTION_PATH or 'Entire Library'}")
    print("=" * 60)

    # Initialize
    zot = zotero.Zotero(config.LIBRARY_ID, config.LIBRARY_TYPE, config.API_KEY)

    # Load or refresh cache
    cache = load_cache()
    if not cache:
        cache = refresh_cache_from_zotero(zot)
    else:
        print(f"✅ Loaded {len(cache)} collections from cache")

    # Find target collection if specified
    target_coll_key = None
    if TARGET_COLLECTION_PATH:
        print(f"\n📂 Looking for collection: {TARGET_COLLECTION_PATH}")
        target_coll_key = find_collection_by_path(zot, TARGET_COLLECTION_PATH, cache)

        if not target_coll_key:
            print("❌ Target collection not found. Exiting.")
            return

        print(f"✅ Found collection (Key: {target_coll_key})")

    # Fetch items to process
    print("\n🔍 Fetching items...")

    if target_coll_key:
        # Get items from specific collection with gemini_read tag
        items = zot.collection_items(target_coll_key, tag='gemini_read', limit=100)
        print(f"   Scope: Collection '{TARGET_COLLECTION_PATH}'")
    else:
        # Get items from entire library with gemini_read tag
        items = zot.items(tag='gemini_read', limit=100)
        print(f"   Scope: Entire library")

    print(f"   Found: {len(items)} items with 'gemini_read' tag")

    # Filter items that haven't been organized yet
    todo_items = []

    for item in items:
        # Skip if already has auto_organized tag
        tags = [t.get('tag', '') for t in item['data'].get('tags', [])]
        if AUTO_TAG_NAME in tags:
            continue

        # Get AI-generated note
        children = zot.children(item['key'])
        keywords = ""

        for child in children:
            if child['data']['itemType'] == 'note':
                note_content = child['data'].get('note', '')
                extracted = extract_keywords_from_note(note_content)
                if extracted:
                    keywords = extracted
                    break

        if keywords:
            todo_items.append({
                'key': item['key'],
                'data': item['data'],
                'title': item['data'].get('title', 'Untitled'),
                'keywords': keywords
            })

    print(f"✅ Items to organize: {len(todo_items)}")

    if not todo_items:
        print("\n🎉 No items to process!")
        return

    # Process in batches
    total_batches = math.ceil(len(todo_items) / BATCH_SIZE)
    organized_count = 0

    for batch_idx in range(total_batches):
        batch = todo_items[batch_idx * BATCH_SIZE : (batch_idx + 1) * BATCH_SIZE]

        print(f"\n📦 Batch {batch_idx + 1}/{total_batches} ({len(batch)} items)")
        print("-" * 60)

        # AI classification
        print("   🧠 Calling AI for classification...")
        classifications = ai_classify_batch(batch, config.AI_MODEL, config.AI_API_KEY)

        # Process each classification
        for idx_str, path in classifications.items():
            try:
                idx = int(idx_str)
                if idx >= len(batch):
                    continue

                item_info = batch[idx]
                print(f"\n   [{idx}] {item_info['title'][:50]}...")
                print(f"      📍 Target: {path}")

                # Ensure collection path exists
                target_key = ensure_collection_path(zot, path, cache)

                if target_key:
                    # Move item
                    if DRY_RUN:
                        print(f"      [Dry Run] Would move to: {path}")
                    else:
                        move_item_to_collection(zot, item_info['data'], target_key)

                    organized_count += 1

            except Exception as e:
                print(f"   ❌ Error processing item {idx_str}: {e}")

        # Rate limiting
        if batch_idx < total_batches - 1:
            print("\n   ⏸️  Waiting 3s before next batch...")
            time.sleep(3)

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"Total items processed: {len(todo_items)}")
    print(f"Successfully organized: {organized_count}")
    print(f"Mode: {'DRY RUN (no changes made)' if DRY_RUN else 'LIVE MODE (changes saved)'}")
    print("=" * 60)
    print("\n🎉 Done!")

    if DRY_RUN:
        print("\n💡 Tip: Set DRY_RUN = False to actually move items")

if __name__ == "__main__":
    main()
