#!/usr/bin/env python3
"""
Grocery Profile Context Server & Resolver
Implements the grocery-profile-ctx tools:
- lookup_preferred_item: Maps generic terms to specific preferred brand/size configurations.
- check_order_history: Checks past orders to resolve conflicts/alternates.
- stage_amazon_now_items: Generates the Amazon Now (Yalla) target cart URLs and search deep-links.
"""

import json
import os
import re
import urllib.parse
from pathlib import Path

PROFILE_PATH = Path(__file__).parent / "grocery-profile.json"
SAMPLE_PROFILE_PATH = Path(__file__).parent / "grocery-profile.sample.json"

def load_profile():
    path = PROFILE_PATH if PROFILE_PATH.exists() else SAMPLE_PROFILE_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def lookup_preferred_item(query: str):
    """
    Looks up preferred brand, packaging, size, and search term.
    """
    profile = load_profile()
    query_clean = query.lower().strip()
    
    # Extract quantity if present
    qty_match = re.search(r'\b(\d+)\b', query_clean)
    quantity = int(qty_match.group(1)) if qty_match else 1
    
    matched_key = None
    matched_item = None
    
    for key, item in profile["items"].items():
        if key in query_clean:
            matched_key = key
            matched_item = item
            break
        for kw in item.get("generic_keywords", []):
            if kw in query_clean:
                matched_key = key
                matched_item = item
                break
        if matched_item:
            break
            
    if not matched_item:
        return {
            "status": "not_found",
            "query": query,
            "message": f"No preconfigured mapping found for '{query}' in grocery-profile-ctx."
        }

    primary = matched_item["primary"]
    brand = primary.get("brand", "")
    prod_name = primary.get("product_name", "")
    size = primary.get("size", "")
    
    # Avoid repeating brand if already in product name
    display_title = prod_name if brand.lower() in prod_name.lower() else f"{brand} {prod_name}"
    resolved_description = f"{quantity} {'pack' if quantity == 1 else 'packs'} of {display_title} {size}"
    
    return {
        "status": "resolved",
        "category": matched_key,
        "quantity": quantity,
        "primary": primary,
        "alternates": matched_item.get("alternates", []),
        "resolved_string": resolved_description,
        "search_term": primary["search_term"]
    }

def check_order_history(category: str):
    """
    Checks historical order logs for preference stability or availability fallbacks.
    """
    profile = load_profile()
    history = profile.get("order_history", [])
    past_matches = []
    
    for order in history:
        for it in order.get("items", []):
            if it.get("item") == category:
                past_matches.append({
                    "date": order.get("date"),
                    "brand": it.get("brand"),
                    "size": it.get("size"),
                    "quantity": it.get("quantity")
                })
    return {
        "category": category,
        "historical_orders": past_matches,
        "total_orders": len(past_matches)
    }

def stage_amazon_now_items(items_to_stage):
    """
    Stages items to Amazon Now Egypt store URL.
    Generates direct search deep-links scoped to Amazon Now / Tez store.
    """
    profile = load_profile()
    base_store_url = profile["store"]["base_url"]
    
    staged = []
    for item in items_to_stage:
        encoded_query = urllib.parse.quote_plus(item["search_term"])
        # Direct Amazon Egypt search link within the Tez / Now store context
        item_url = f"https://www.amazon.eg/s?k={encoded_query}&i=nowstore&ref=nb_sb_noss"
        staged.append({
            "resolved_string": item["resolved_string"],
            "quantity": item["quantity"],
            "search_term": item["search_term"],
            "direct_url": item_url
        })
        
    return {
        "store_name": profile["store"]["name"],
        "store_base_url": base_store_url,
        "staged_items": staged
    }

if __name__ == "__main__":
    import sys
    test_query = sys.argv[1] if len(sys.argv) > 1 else "2 bottles of milk"
    print(f"Resolving: '{test_query}'")
    res = lookup_preferred_item(test_query)
    print(json.dumps(res, indent=2))
    staged = stage_amazon_now_items([res])
    print(json.dumps(staged, indent=2))
