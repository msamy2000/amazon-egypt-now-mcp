# Amazon Egypt Now Grocery Shopper MCP (`grocery-profile-ctx`)

A Model Context Protocol (MCP) server that transforms any AI agent (Claude Desktop, Cursor, Antigravity, Open-WebUI, etc.) into a personalized grocery purchasing assistant for **Amazon Egypt Now**.

---

## 🌟 Key Features

1. **Natural Language Grocery Resolution**:
   - Converts generic terms like *"buy 2 bottles of milk"*, *"get rice and sugar"* into exact brands, packaging types, and pack sizes (e.g., *2 packs of Lamar Full Fat Milk 1L*).
2. **Personalized Preference Memory**:
   - Maintains a customizable profile (`grocery-profile.json`) learned from past orders or tailored to the user's favorite brands.
3. **Cheaper Brand & Promotion Awareness (Rule 5)**:
   - Compares list prices and Amazon promotional discounts, highlighting when a quality alternate is cheaper (e.g., Al Sa'a 20% off vs. Al Doha).
4. **Offer & Free Shipping Alerts (Rule 2)**:
   - Proactively checks current cart subtotal against the **150 EGP** free shipping threshold.
5. **Multi-Address Safety (Rule 1)**:
   - Supports designated address profiles (e.g. *Mom's House: Building 26*, *My Home: Building 22*) and prompts before staging.
6. **Strict Human Checkout Barrier (Rule 6)**:
   - Safely stages products in the user's active cart, leaving the final payment button strictly to human authorization.
7. **Zero External Dependencies**:
   - Pure Python standard library JSON-RPC 2.0 implementation over `stdio`. Runs instantly on any macOS/Linux/Windows machine without needing `pip install`.

---

## 🛠️ MCP Tools Exposed

| Tool Name | Description |
| :--- | :--- |
| `lookup_grocery_item` | Resolves generic phrases to specific brand/size/pack and Amazon Now search URLs. |
| `check_substitutions` | Returns pre-ranked alternatives and price comparisons when an item is out of stock. |
| `stage_in_cart` | Prepares the exact product addition script / URL for Amazon Now. |
| `list_known_catalog` | Lists all learned staples and current preferred configurations. |
| `record_order_event` | Logs completed orders to calibrate future delivery frequencies. |

---

## 🚀 How to Share & Install

### Option A: Using with Claude Desktop
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "grocery-shopper": {
      "command": "python3",
      "args": [
        "/path/to/Amazon Shopper/server.py"
      ]
    }
  }
}
```

### Option B: Using with Cursor / Antigravity / Any MCP Client
In your project's `.cursor/mcp.json` or MCP settings:

```json
{
  "mcpServers": {
    "grocery-shopper": {
      "command": "python3",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

---

## 📦 File Structure

- `server.py`: The MCP server (JSON-RPC 2.0 over standard I/O).
- `grocery-profile.json`: User preferences, staples, and addresses.
- `KNOWN_PRODUCTS.md`: Human-readable reference catalog.
- `stage_main_browser.py`: Cart automation script for active Chrome sessions.
- `test_mcp.py`: Automated protocol test suite.

---

## 📄 License
MIT
