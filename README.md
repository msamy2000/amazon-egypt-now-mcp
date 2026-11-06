# Amazon Egypt Now Grocery Shopper & MCP Context Server

An intelligent grocery purchasing assistant and Model Context Protocol (MCP) server tailored for **Amazon Egypt Now** (`amazon.eg` Yalla/Tez store).

## What it Does
- **Implicit Mapping**: Automatically converts generic items (e.g. *"buy 2 bottles of milk"*, *"get rice and sugar"*) into preconfigured brands, packages, and sizes.
- **Substitutions & Order History**: Automatically resolves stock conflicts or alternates from past logs, and prompts for confirmation if primary is unavailable.
- **Amazon Now Staging**: Directly stages resolved items into the user's active shopping cart on Amazon Egypt Now.
- **Promotion & Budget Awareness**: Alerts the user when cart value is approaching the free delivery threshold (150 EGP).

## Files
- `server.py`: Standard JSON-RPC 2.0 MCP server over stdio (zero external dependencies).
- `grocery-profile.sample.json`: Sample configuration of staples, brands, sizes, and rules.
- `stage_main_browser.py`: Cart stager connecting directly into an active Chrome session.
- `grocery_profile_resolver.py`: Standalone CLI utility for resolving grocery requests.
- `test_resolver.py`: Unit test suite.
- `test_mcp.py`: MCP protocol test suite.

## Core Operating Rules
1. **Address Selection**: Always ask which address to deliver to before finalizing.
2. **Promotions & Free Delivery**: Highlight active promotions and minimum spend thresholds (e.g. Free Shipping threshold at 150 EGP).
3. **Out-of-Stock Fallback**: Show ranked alternatives if a preferred product is missing.
4. **Clarification**: When in doubt, ask before acting.
5. **Cheapest Brand Preference**: Compare list and discounted promotional prices, presenting the cheapest option.
6. **Human-Only Checkout**: Stage items in cart, but never click "Proceed to Checkout" or "Place Order".

## Running the MCP Server
```bash
python3 server.py
```
Or in any MCP client config (e.g., Claude Desktop, Cursor):
```json
{
  "mcpServers": {
    "grocery-profile-ctx": {
      "command": "python3",
      "args": ["/path/to/server.py"]
    }
  }
}
```
