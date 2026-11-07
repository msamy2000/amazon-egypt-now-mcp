#!/usr/bin/env python3
"""
Amazon Egypt Now - Main Chrome Profile Cart Stager
Drives your active Google Chrome window (where your signed-in
account, address, and Amazon Now session already exist) via AppleScript with Apple Events JavaScript.
"""

import sys
import subprocess
import json
from grocery_profile_resolver import lookup_preferred_item

STORE_URL = "https://www.amazon.eg/-/en/tez/browse?qcbrand=sAuWWBROaG&ref_=nav_cs_yalla"

def stage_items_in_active_session(queries):
    """
    Looks up products in grocery-profile and adds them directly inside your
    active signed-in Google Chrome browser instance.
    """
    resolved_list = []
    for q in queries:
        res = lookup_preferred_item(q)
        if res.get("status") == "resolved":
            resolved_list.append(res)
        else:
            print(f"[!] Could not resolve: {q}")

    if not resolved_list:
        print("No items to stage.")
        return

    # Check that main Chrome window is available
    script = f'''
    tell application "Google Chrome"
        tell front window
            set target_tab_index to missing value
            repeat with i from 1 to (count of tabs)
                set t_url to URL of tab i
                if t_url contains "tez/browse" or t_url contains "amazon.eg" then
                    set target_tab_index to i
                    exit repeat
                end if
            end repeat
            
            if target_tab_index is missing value then
                make new tab at end of tabs with properties {{URL:"{STORE_URL}"}}
                set active tab index to (count of tabs)
            else
                set active tab index to target_tab_index
                if (URL of active tab) does not contain "tez/browse" then
                    set URL of active tab to "{STORE_URL}"
                end if
            end if
        end tell
        activate
    end tell
    delay 3
    '''
    subprocess.run(["osascript", "-e", script], check=True)

    for item in resolved_list:
        brand = item["primary"].get("brand", "")
        asin = item["primary"].get("asin", "")
        title = item["primary"].get("product_name", "")
        qty = item.get("quantity", 1)
        search_kw = item.get("search_term", title)

        print(f"🛒 Adding {qty}x {brand} {title} (ASIN: {asin}) directly to Amazon Now cart...")

        js_code = f'''
        (function() {{
            let asin = "{asin}";
            let brand = "{brand}".toLowerCase();
            let qty = {qty};
            
            // 1. Look for existing stepper with this ASIN
            let stepper = document.querySelector('[data-csa-c-content-id*="' + asin + '"]');
            if (stepper) {{
                let incBtn = document.querySelector('button[aria-label="Increase quantity"][data-csa-c-content-id*="' + asin + '"]');
                let currentStatus = stepper.closest('[aria-label="Quantity stepper"]')?.querySelector('[role="status"]')?.innerText || "0";
                let currentQty = parseInt(currentStatus) || 0;
                let needed = qty - currentQty;
                if (needed > 0 && incBtn) {{
                    for (let i = 0; i < needed; i++) {{
                        incBtn.click();
                    }}
                    return "Increased quantity by " + needed + " to reach " + qty;
                }}
                return "Already at quantity: " + currentQty;
            }}
            
            // 2. Look for item card by brand/title and click +
            let all = Array.from(document.querySelectorAll("*"));
            let matchEl = all.find(el => el.children.length === 0 && el.innerText && el.innerText.toLowerCase().includes(brand));
            if (matchEl) {{
                let p = matchEl.parentElement;
                while (p && p.innerText && !p.innerText.includes("+")) {{
                    p = p.parentElement;
                }}
                if (p) {{
                    let plusBtns = Array.from(p.querySelectorAll("button, [role='button'], div")).filter(b => b.innerText && b.innerText.trim() === "+");
                    if (plusBtns.length > 0) {{
                        plusBtns[0].click();
                        return "Clicked + button for " + brand;
                    }}
                }}
            }}
            return "Item not visible on current screen - recommend search: " + brand;
        }})()
        '''

        escaped_js = js_code.replace('"', '\\"')
        exec_script = f'''
        tell application "Google Chrome"
            tell front window
                execute active tab javascript "{escaped_js}"
            end tell
        end tell
        '''
        res = subprocess.run(["osascript", "-e", exec_script], capture_output=True, text=True)
        print(f"   Result: {res.stdout.strip()}")

if __name__ == "__main__":
    queries = sys.argv[1:] if len(sys.argv) > 1 else ["2 bottles of milk"]
    stage_items_in_active_session(queries)
