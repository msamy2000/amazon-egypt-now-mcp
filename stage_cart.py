#!/usr/bin/env python3
"""
Direct Cart Staging Service for Amazon Egypt
Takes generic phrases or resolved items and automatically adds them
directly into your active Amazon Egypt shopping cart!
"""

import sys
import subprocess
import urllib.parse
from grocery_profile_resolver import lookup_preferred_item

def build_cart_add_url(items):
    """
    Constructs the official Amazon remote cart add URL.
    Format: https://www.amazon.eg/gp/aws/cart/add.html?ASIN.1=...&Quantity.1=...
    """
    params = []
    for idx, it in enumerate(items, start=1):
        asin = it.get("asin") or it.get("primary", {}).get("asin")
        qty = it.get("quantity", 1)
        if asin:
            params.append(f"ASIN.{idx}={asin}&Quantity.{idx}={qty}")
            
    if not params:
        return None
    return f"https://www.amazon.eg/gp/aws/cart/add.html?{'&'.join(params)}"

def stage_items_in_chrome_cart(query_list):
    """
    Resolves generic items, constructs cart payload, and drives Chrome
    to stage them directly into your cart.
    """
    resolved_items = []
    for q in query_list:
        res = lookup_preferred_item(q)
        if res.get("status") == "resolved":
            resolved_items.append(res)
            
    cart_url = build_cart_add_url(resolved_items)
    if not cart_url:
        print("[Error] No valid ASINs found to stage.")
        return False
        
    print(f"\n🛒 Staging {len(resolved_items)} items to your Amazon Egypt Cart...")
    for it in resolved_items:
        print(f"  • {it['resolved_string']} (ASIN: {it['primary']['asin']})")
        
    # Drive Chrome to open the direct add URL
    script = f'''
    tell application "Google Chrome"
        make new tab at end of tabs of front window with properties {{URL:"{cart_url}"}}
        tell front window to set (active tab index) to (count of tabs)
        activate
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)
    print("✅ Successfully staged into your Amazon Cart in Google Chrome!")
    return True

if __name__ == "__main__":
    queries = sys.argv[1:] if len(sys.argv) > 1 else ["2 bottles of milk", "sugar", "2 bags of rice"]
    stage_items_in_chrome_cart(queries)
