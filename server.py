#!/usr/bin/env python3
"""
Standard JSON-RPC 2.0 MCP (Model Context Protocol) Server
`grocery-profile-ctx`

Uses Python's standard library (sys, json, os) with ZERO external dependencies,
ensuring 100% instant startup and reliability over standard input/output (stdio).
"""

import sys
import json
import re
import urllib.parse
import difflib
from pathlib import Path

# Multilingual & Franco-Arabic semantic mapping dictionary for Egyptian groceries
ARABIC_SEMANTIC_SYNONYMS = {
    "لبن": "milk",
    "حليب": "milk",
    "laban": "milk",
    "7aleeb": "milk",
    "haleeb": "milk",
    
    "رز": "rice",
    "ارز": "rice",
    "أرز": "rice",
    "roz": "rice",
    "ruz": "rice",
    
    "سكر": "sugar",
    "سكرة": "sugar",
    "sokar": "sugar",
    "sukkar": "sugar",
    
    "جبنة": "cheese",
    "جبنه": "cheese",
    "جبن": "cheese",
    "رومي": "cheese",
    "رومى": "cheese",
    "قريش": "cheese",
    "شيدر": "cheese",
    "لبنة": "cheese",
    "لبنه": "cheese",
    "gebna": "cheese",
    "jebna": "cheese",
    "jibna": "cheese",
    "roumi": "cheese",
    "romy": "cheese",
    "romi": "cheese",
    
    "بيض": "eggs",
    "بيضة": "eggs",
    "بيضه": "eggs",
    "bayd": "eggs",
    "baid": "eggs",
    "beid": "eggs",
    
    "شاي": "tea",
    "شاى": "tea",
    "shai": "tea",
    "shay": "tea",
    
    "فول": "fava_beans",
    "فول مدمس": "fava_beans",
    "ful": "fava_beans",
    "foul": "fava_beans",
    
    "ملوخية": "molokhia",
    "ملوخيه": "molokhia",
    "molokhia": "molokhia",
    "molokheya": "molokhia",
    "mulukhiyah": "molokhia",
    
    "مكرونة": "pasta",
    "مكرونه": "pasta",
    "معكرونة": "pasta",
    "معكرونه": "pasta",
    "لسان عصفور": "pasta",
    "شعرية": "pasta",
    "شعيرية": "pasta",
    "makarona": "pasta",
    "pasta": "pasta",
    
    "فاصوليا": "green_beans",
    "فاصولياء": "green_beans",
    "fasolia": "green_beans",
    
    "بسلة": "peas_carrots",
    "بسله": "peas_carrots",
    "بازلاء": "peas_carrots",
    "besella": "peas_carrots",
    "basella": "peas_carrots",
    
    "مناديل": "toilet_paper",
    "ورق تواليت": "toilet_paper",
    "manadeel": "toilet_paper",
    
    "زبادي": "yoghurt",
    "زبادى": "yoghurt",
    "zabadi": "yoghurt",
    "yogurt": "yoghurt",
    "yoghurt": "yoghurt",
    
    "زيت": "oil",
    "زيت ذرة": "oil",
    "زيت ذره": "oil",
    "zayt": "oil",
    "zeit": "oil"
}
PROFILE_PATH = Path(__file__).parent / "grocery-profile.json"
SAMPLE_PROFILE_PATH = Path(__file__).parent / "grocery-profile.sample.json"

def _load_profile():
    path = PROFILE_PATH if PROFILE_PATH.exists() else SAMPLE_PROFILE_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_profile(data):
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def tool_lookup_grocery_item(arguments: dict):
    query = arguments.get("query", "").strip()
    profile = _load_profile()
    query_clean = query.lower()
    
    qty_match = re.search(r'\b(\d+)\b', query_clean)
    quantity = int(qty_match.group(1)) if qty_match else 1
    
    matched_key = None
    matched_item = None
    
    # Step 1: Semantic & Cross-Lingual Translation Analysis
    # Checks Arabic, English, and Franco-Arabic keywords in dictionary
    for synonym, target_category in ARABIC_SEMANTIC_SYNONYMS.items():
        if synonym in query_clean:
            if target_category in profile.get("items", {}):
                matched_key = target_category
                matched_item = profile["items"][target_category]
                break

    # Step 2: Exact or substring match across keys and generic keywords
    if not matched_item:
        for key, item in profile.get("items", {}).items():
            if key in query_clean:
                matched_key = key
                matched_item = item
                break
            for kw in item.get("generic_keywords", []):
                if kw.lower() in query_clean:
                    matched_key = key
                    matched_item = item
                    break
            if matched_item:
                break
            
    # Step 3: Fuzzy spelling matching across all tokens (difflib SequenceMatcher >= 70%)
    if not matched_item:
        words = re.findall(r'[\w\u0600-\u06FF]+', query_clean)
        candidates = []
        for key, item in profile.get("items", {}).items():
            candidates.append((key, key, item))
            for kw in item.get("generic_keywords", []):
                candidates.append((kw.lower(), key, item))
            # Also check brand and product name
            p = item.get("primary", {})
            if "product_name" in p:
                candidates.append((p["product_name"].lower(), key, item))
            if "brand" in p:
                candidates.append((p["brand"].lower(), key, item))
                
        best_ratio = 0.0
        best_match = None
        
        for word in words:
            if len(word) < 3:
                continue
            for cand_term, cand_key, cand_item in candidates:
                # Token-level similarity
                for cand_word in cand_term.split():
                    sim = difflib.SequenceMatcher(None, word, cand_word).ratio()
                    if sim > best_ratio and sim >= 0.70:
                        best_ratio = sim
                        best_match = (cand_key, cand_item)
                        
        if best_match:
            matched_key, matched_item = best_match
            
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
    pack_type = primary.get("pack_type", "pack")
    
    display_title = prod_name if brand.lower() in prod_name.lower() else f"{brand} {prod_name}"
    pack_label = pack_type if quantity == 1 else f"{pack_type}s"
    resolved_description = f"{quantity} {pack_label} of {display_title} {size}".strip()
    
    encoded_search = urllib.parse.quote_plus(primary["search_term"])
    store_search_url = f"https://www.amazon.eg/s?k={encoded_search}&i=nowstore&ref=nb_sb_noss"
    
    return {
        "status": "resolved",
        "category": matched_key,
        "quantity": quantity,
        "primary": primary,
        "resolved_string": resolved_description,
        "search_term": primary["search_term"],
        "store_search_url": store_search_url,
        "has_alternates": len(matched_item.get("alternates", [])) > 0
    }

def tool_check_substitutions(arguments: dict):
    category = arguments.get("category", "").lower().strip()
    profile = _load_profile()
    item_conf = profile.get("items", {}).get(category)
    if not item_conf:
        return {"status": "not_found", "category": category, "alternates": []}
        
    alternates = item_conf.get("alternates", [])
    history = profile.get("order_history", [])
    past_orders = []
    for order in history:
        for it in order.get("items", []):
            if it.get("item") == category:
                past_orders.append(it)
                
    return {
        "status": "success",
        "category": category,
        "alternates": alternates,
        "historical_deliveries": past_orders
    }

def tool_record_order_event(arguments: dict):
    items = arguments.get("items", [])
    date_str = arguments.get("date", "")
    profile = _load_profile()
    
    from datetime import date
    entry_date = date_str or date.today().isoformat()
    order_entry = {
        "date": entry_date,
        "items": items
    }
    profile.setdefault("order_history", []).append(order_entry)
    _save_profile(profile)
    return {"status": "success", "recorded_entry": order_entry}

def tool_stage_in_cart(arguments: dict):
    """
    Directly stages an item into the user's active Google Chrome session on Amazon Egypt Now.
    Enforces Rule 1: Must specify address ('home' or 'mom') or requires confirmation first.
    """
    query = arguments.get("query", "").strip()
    quantity = arguments.get("quantity", 1)
    address = arguments.get("address", "").strip().lower()
    
    profile = _load_profile()
    addresses = profile.get("addresses", {})
    
    # ENFORCE RULE 1: If address is not specified, block staging and demand address confirmation!
    if not address or address not in ["home", "mom", "22", "26"]:
        return {
            "status": "requires_address_confirmation",
            "message": "RULE 1 ENFORCED: You MUST ask the user which delivery address to select before staging items in the cart.",
            "options": {
                "home": "My Home (Building number 22)",
                "mom": "Mom's House (Building number 26)"
            },
            "prompt_user": "Please select the delivery address: 1) My Home (Building 22) or 2) Mom's House (Building 26)?"
        }
        
    # 1. Resolve query first
    lookup_res = tool_lookup_grocery_item({"query": query})
    if lookup_res.get("status") != "resolved":
        return {
            "status": "error",
            "message": f"Could not resolve '{query}' to a known product."
        }
        
    primary = lookup_res["primary"]
    brand = primary.get("brand", "")
    prod_name = primary.get("product_name", "")
    asin = primary.get("asin", "")
    qty = quantity or lookup_res.get("quantity", 1)
    
    selected_addr = "Mom's House (Building 26)" if ("mom" in address or "26" in address) else "My Home (Building 22)"
    
    # 2. Drive the active Chrome browser via AppleScript
    apple_script = f'''
    tell application "Google Chrome"
        tell front window
            execute active tab javascript "
                (function() {{
                    let brand = \\"{brand}\\".toLowerCase();
                    let prodName = \\"{prod_name}\\".toLowerCase();
                    let asin = \\"{asin}\\";
                    let targetQty = {qty};
                    
                    let all = Array.from(document.querySelectorAll(\\"*\\"));
                    let match = all.find(el => el.children.length === 0 && el.innerText && 
                        (el.innerText.toLowerCase().includes(brand) || el.innerText.toLowerCase().includes(prodName)));
                        
                    if (!match) {{
                        return JSON.stringify({{status: \\"not_found_on_screen\\", item: \\"{brand} {prod_name}\\"}});
                    }}
                    
                    let card = match;
                    while (card && card.parentElement && !card.innerText.includes(\\"EGP\\")) {{
                        card = card.parentElement;
                    }}
                    
                    let stepper = card.querySelector(\\"[aria-label='Quantity stepper']\\");
                    if (stepper) {{
                        let incBtn = card.querySelector(\\"button[aria-label='Increase quantity']\\");
                        if (incBtn) {{
                            incBtn.click();
                            return JSON.stringify({{status: \\"incremented\\", item: \\"{brand} {prod_name}\\"}});
                        }}
                    }}
                    
                    let addBtn = card.querySelector(\\"button, [role='button']\\");
                    if (addBtn) {{
                        addBtn.click();
                        return JSON.stringify({{status: \\"added\\", item: \\"{brand} {prod_name}\\"}});
                    }}
                    
                    return JSON.stringify({{status: \\"no_button\\", item: \\"{brand} {prod_name}\\"}});
                }})()
            "
        end tell
    end tell
    '''
    
    import subprocess
    proc = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    raw_out = proc.stdout.strip()
    
    try:
        parsed = json.loads(raw_out)
    except:
        parsed = {"raw": raw_out}
        
    return {
        "status": "success",
        "action": "staged_in_cart",
        "delivery_address": selected_addr,
        "resolved_product": f"{qty}x {brand} {prod_name}",
        "browser_execution": parsed
    }

def tool_list_configured_staples(arguments: dict):
    profile = _load_profile()
    staples = {}
    for cat, conf in profile.get("items", {}).items():
        staples[cat] = {
            "frequency": conf.get("default_frequency", "as needed"),
            "primary": conf.get("primary", {}),
            "alternates_count": len(conf.get("alternates", []))
        }
    return staples

TOOLS = [
    {
        "name": "lookup_grocery_item",
        "description": "Maps generic grocery items (e.g., '2 bottles of milk', 'sugar', 'جبنة رومي') to specific configured brands, sizes, and packaging for Amazon Egypt Now.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "User grocery request, e.g. '2 bottles of milk' or 'sugar'"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "stage_in_cart",
        "description": "Stages an item into the user's active Google Chrome session on Amazon Egypt Now. MANDATORY: You must provide the confirmed delivery address ('home' for Building 22 or 'mom' for Building 26). If the user has not confirmed the address yet, omit the parameter or pass empty to trigger the address selection prompt.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Grocery item name in English or Arabic, e.g. 'sugar', 'milk', 'جبنة رومي'"},
                "quantity": {"type": "integer", "description": "Quantity to add", "default": 1},
                "address": {"type": "string", "description": "Delivery address destination: 'home' (Building 22) or 'mom' (Building 26)", "enum": ["home", "mom", "22", "26"]}
            },
            "required": ["query", "address"]
        }
    },
    {
        "name": "check_substitutions",
        "description": "Checks order history and retrieves pre-ranked substitutes/alternates when primary item is out of stock.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Item category, e.g. 'milk', 'sugar', 'rice'"}
            },
            "required": ["category"]
        }
    },
    {
        "name": "record_order_event",
        "description": "Logs placed order details into the history log to inform future order recommendations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "description": "Array of ordered item objects"},
                "date": {"type": "string", "description": "Optional ISO date string"}
            },
            "required": ["items"]
        }
    },
    {
        "name": "list_configured_staples",
        "description": "Lists all preconfigured staples, their frequencies (weekly, bi-weekly, monthly), and primary brands.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

def handle_rpc(request: dict):
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "grocery-profile-ctx",
                    "version": "1.0.0"
                }
            }
        }
        
    elif method == "notifications/initialized":
        return None
        
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }
        
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "lookup_grocery_item":
                res = tool_lookup_grocery_item(arguments)
            elif tool_name == "stage_in_cart":
                res = tool_stage_in_cart(arguments)
            elif tool_name == "check_substitutions":
                res = tool_check_substitutions(arguments)
            elif tool_name == "record_order_event":
                res = tool_record_order_event(arguments)
            elif tool_name == "list_configured_staples":
                res = tool_list_configured_staples(arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {tool_name}"}
                }
                
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(res, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Error executing {tool_name}: {str(e)}"}]
                }
            }
            
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unhandled method {method}"}
    }

def main():
    """Main stdio JSON-RPC loop"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_rpc(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as ex:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(ex)}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
