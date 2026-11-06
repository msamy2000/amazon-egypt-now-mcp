#!/usr/bin/env python3
"""
Amazon Egypt Now Cart Automation Service
Connects to Amazon Egypt (amazon.eg) using Playwright with persistent session storage
to ensure addresses, login sessions, and Now/Yalla store context remain preserved.
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

USER_DATA_DIR = Path(__file__).parent / ".browser_session"
STORE_URL = "https://www.amazon.eg/-/en/tez/browse?qcbrand=sAuWWBROaG&ref_=nav_cs_yalla"

async def stage_item_in_cart(search_term: str, target_quantity: int = 1, headless: bool = False):
    """
    Launches browser, searches for product on Amazon Egypt Now, and stages to cart.
    """
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        # Launch persistent browser context to retain cookies/session
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            print(f"[Shopper] Navigating to Amazon Now Egypt...")
            await page.goto(STORE_URL, wait_until="domcontentloaded", timeout=45000)
            
            # Direct search for the specific item within Now store
            search_url = f"https://www.amazon.eg/s?k={search_term.replace(' ', '+')}&i=nowstore"
            print(f"[Shopper] Searching item: {search_term}...")
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(3000)
            
            # Check for results or out-of-stock indicators
            first_product = await page.query_selector("div[data-component-type='s-search-result']")
            if not first_product:
                print(f"[Shopper] No direct search results found for '{search_term}'.")
                return {"status": "out_of_stock_or_not_found", "search_term": search_term}
                
            title_el = await first_product.query_selector("h2 a span")
            title_text = await title_el.inner_text() if title_el else "Unknown item"
            print(f"[Shopper] Found top match: {title_text}")
            
            # Locate Add to Cart button (Now store usually has quick 'Add to Cart' or 'Add' button)
            add_button = await first_product.query_selector("button[name='submit.addToCart'], input[id*='add-to-cart'], button:has-text('Add to Cart'), button:has-text('Add')")
            
            if add_button:
                await add_button.click()
                print(f"[Shopper] Clicked 'Add to Cart' for: {title_text}")
                await page.wait_for_timeout(2000)
                return {
                    "status": "staged_in_cart",
                    "product": title_text,
                    "quantity": target_quantity,
                    "search_term": search_term
                }
            else:
                # Open product page to add
                link = await first_product.query_selector("h2 a")
                if link:
                    await link.click()
                    await page.wait_for_load_state("domcontentloaded")
                    p_add = await page.query_selector("input#add-to-cart-button, button#add-to-cart-button")
                    if p_add:
                        await p_add.click()
                        await page.wait_for_timeout(2000)
                        return {
                            "status": "staged_in_cart",
                            "product": title_text,
                            "quantity": target_quantity,
                            "search_term": search_term
                        }

            return {
                "status": "requires_manual_selection",
                "product": title_text,
                "url": page.url
            }
            
        except Exception as e:
            print(f"[Shopper] Error: {e}", file=sys.stderr)
            return {"status": "error", "message": str(e)}
        finally:
            await context.close()

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Juhayna Full Cream Milk 1L"
    qty = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    res = asyncio.run(stage_item_in_cart(query, qty, headless=True))
    print(json.dumps(res, indent=2))
