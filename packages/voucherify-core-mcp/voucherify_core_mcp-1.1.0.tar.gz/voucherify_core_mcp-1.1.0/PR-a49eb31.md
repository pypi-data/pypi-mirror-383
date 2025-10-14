## Title
Get Best Deals: add applicability flag and discounted cart preview

## Description
This update enhances `get_best_deals` so you can quickly decide which promotion to surface and clearly show expected savings to your customers.

- **New `is_applicable`**: Instantly tells you if a promotion fully qualifies for the current cart.
- **New `resolved_order`**: For applicable promotions, returns a cart snapshot with calculated discounts for UI previews and savings summaries.
- **Compatibility**: Additive change; no breaking changes.

### Example
```json
{
  "id": "promo_123",
  "object": "promotion_tier",
  "is_applicable": true,
  "redeemable_details": { "public_banner": "Buy 2 get 20% off" },
  "validation_rules": [/* ... */],
  "resolved_order": {
    "total_amount": 2450,
    "items": [/* discounted items */]
  }
}
```

- **Why it matters**: Faster UI decisions, clearer savings messaging, and fewer extra lookups.
- Docs will be updated to reflect the new fields in `get_best_deals`.


