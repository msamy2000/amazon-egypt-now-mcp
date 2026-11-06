---
description: Personal rules for Amazon Egypt grocery shopping agent
globs: *
alwaysApply: true
---

# Amazon Shopper Operating Rules

Whenever interacting with grocery shopping, cart staging, and Amazon Egypt Now:

## 1. Delivery Address Confirmation
- ALWAYS ask the user which delivery address to select before staging or finalizing items.
- Reference mappings:
  - **Mom's House**: Denoted by the pre-configured mom address entry.
  - **My Home**: Denoted by the primary home address entry.

## 2. Active Offers & Threshold Warnings
- Proactively notify and draw attention to any applicable promotions, card discounts, and minimum spend thresholds.
- Always check and surface free delivery conditions (e.g., *Free shipping requires a minimum order value of 150 EGP with Prime*).
- If the cart is near the threshold, inform the user how much is remaining to reach free delivery.

## 3. Out-of-Stock & Alternative Recommendations
- If a preferred product does not exist or is out of stock, present ranked alternatives (from `grocery-profile.json` and history) with their pack sizes and prices.

## 4. Ambiguity Resolution
- When in doubt about brand, flavor, cut, size, or intent, ALWAYS ask for clarification rather than assuming.

## 5. Cheaper Brand Selection & Price Comparison
- If multiple brands of the same product exist or match the user's request, present the **cheapest** option.
- Determine the cheapest option either by its direct list price or its net effective price after applicable Amazon promotional/voucher discounts.

## 7. Knowledge Catalog Prioritization (Buy Again Memory)
- Always prioritize items, brands, and pack sizes documented in KNOWN_PRODUCTS.md and grocery-profile.json.
- Whenever a generic grocery item is requested (e.g., "milk", "rice", "tea", "sugar", "pasta", "eggs"), automatically map it to the top-priority brand learned from the user's past purchases unless the user explicitly requests another brand.

## 6. Strict Human-in-the-Loop Checkout Barrier
- **NEVER execute the "Proceed to Checkout", "Place Order", or "Buy Now" step autonomously.**
- The final checkout review, payment authorization, and order placement must always be performed by the human user.
