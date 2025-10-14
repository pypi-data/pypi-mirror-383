I would like to prepare a plan related to @server.py MCP tool called `get_best_deals`. The idea is to call stackable validation api with all redeemables returned by qualification API.
Then enhance `redeemables` list with two details from validation response.


### Expected enhancements:

```
redeemables: [
    {
        "id": "promo_TX8chQgOhqVegfyklDS7H48u",
        "is_applicable": true,  /* Why validation response corresponding `redeemable.status == "APPLICABLE" */,
        "resolved_order": redeemable.order, /** Taken from Validation response for APPLICABLE redeemables */
        ...otherFields
    },
    ...
]
```

### Example partial response from Qualification API:

```
{
  "redeemables": {
    "object": "list",
    "data_ref": "data",
    "data": [
      {
        "id": "promo_TX8chQgOhqVegfyklDS7H48u",
        "object": "promotion_tier",
      },
      {
        "id": "promo_04cO7c71vUq2zXGMV3LljtPw",
        "object": "promotion_tier",
      },
      {
        "code": "voucher_code",
        "object": "voucher",
      }
    ]
  }
}
```


### Example request/response to Validation API:

Validation API endpoint: /v1/validations
<validation_api>
<request_body>
{
  "customer": {
     "source_id": "liam-sterling"
  },
    "order": {
          "amount": 13200,
          "items": [
            {
              "source_id": "FF1050-1",
              "related_object": "product",
              "quantity": 4,
              "product": {
                "name": "FlavorFlux - Protein Power Chocolate",
                "metadata": {}
              }
            }
          ]
    },
  "redeemables": [
    { "object": "promotion_tier", "id": "promo_TX8chQgOhqVegfyklDS7H48u" },
    { "object": "promotion_tier", "id": "promo_04cO7c71vUq2zXGMV3LljtPw" },
    { "object": "voucher", "id": "voucher_code" },
    { "object": "promotion_stack", "id": "stack_KxSD0GahLUg9ULB6TseGfUHJ" }
  ]
}
</request_body>
<response_body>
{

  "id": "valid_11553a7a320d1f9ba9",
  "valid": false,
  "redeemables": [
    {
      "status": "APPLICABLE",
      "id": "promo_TX8chQgOhqVegfyklDS7H48u",
      "object": "promotion_tier",
      "order": {
        "amount": 13200,
        "total_amount": 13200,
        "items": [
          {
            "object": "order_item",
            "id": "ordli_11553a7a4a4d1f9bab",
            "source_id": "FF1050-1",
            "related_object": "product",
            "quantity": 4,
            "initial_quantity": 4,
            "product": {
              "name": "FlavorFlux - Protein Power Chocolate",
              "metadata": {}
            }
          }
        ],
        "customer_id": null,
        "referrer_id": null,
        "object": "order"
      },
      "applicable_to": {
        "data": [
          {
            "object": "products_collection",
            "id": "pc_yyecTc9CwLWImTKpMac1EyVP",
            "strict": false,
            "effect": "APPLY_TO_EVERY",
            "order_item_indices": [
              0
            ],
            "order_item_units": [
              {
                "index": 0,
                "units": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "skip_initially": 0,
            "repeat": 1,
            "target": "ITEM"
          },
          {
            "object": "product",
            "id": "FF1050-1",
            "source_id": "FF1050-1",
            "strict": true,
            "effect": "APPLY_TO_EVERY",
            "order_item_indices": [
              0
            ],
            "order_item_units": [
              {
                "index": 0,
                "units": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "skip_initially": 0,
            "repeat": 1,
            "target": "ITEM"
          }
        ],
        "total": 2,
        "data_ref": "data",
        "object": "list"
      },
      "inapplicable_to": {
        "data": [],
        "total": 0,
        "data_ref": "data",
        "object": "list"
      },
      "result": {
        "discount": {
          "type": "PERCENT",
          "effect": "APPLY_TO_ITEMS",
          "percent_off": 15,
          "is_dynamic": false
        }
      },
      "metadata": {}
    },
    {
      "status": "INAPPLICABLE",
      "id": "promo_04cO7c71vUq2zXGMV3LljtPw",
      "object": "promotion_tier",
      "result": {
        "error": {
          "code": 400,
          "key": "order_rules_violated",
          "message": "order does not match validation rules",
          "details": "Promotion Tier cannot be redeemed because of violated validation rules: val_RKJsewO4Fplk",
          "request_id": "v-11553a7a2acdc5719e"
        },
        "details": {
          "message": "order does not match validation rules",
          "key": "order_rules_violated"
        }
      },
      "metadata": {}
    }
  ],
  "inapplicable_redeemables": [
    {
      "status": "INAPPLICABLE",
      "id": "promo_04cO7c71vUq2zXGMV3LljtPw",
      "object": "promotion_tier",
      "result": {
        "error": {
          "code": 400,
          "key": "order_rules_violated",
          "message": "order does not match validation rules",
          "details": "Promotion Tier cannot be redeemed because of violated validation rules: val_RKJsewO4Fplk",
          "request_id": "v-11553a7a2acdc5719e"
        },
        "details": {
          "message": "order does not match validation rules",
          "key": "order_rules_violated"
        }
      },
      "metadata": {}
    }
  ],
  "tracking_id": "track_QssXUsQ55E31qQxgklbWZw==",
  "stacking_rules": {
    "redeemables_limit": 30,
    "applicable_redeemables_limit": 5,
    "applicable_exclusive_redeemables_limit": 1,
    "applicable_redeemables_category_limits": {},
    "exclusive_categories": [],
    "joint_categories": [],
    "redeemables_application_mode": "ALL",
    "redeemables_sorting_rule": "REQUESTED_ORDER",
    "redeemables_no_effect_rule": "REDEEM_ANYWAY",
    "no_effect_skip_categories": [],
    "no_effect_redeem_anyway_categories": [],
    "redeemables_products_application_mode": "STACK",
    "redeemables_rollback_order_mode": "WITH_ORDER",
    "grouped_redeemables_sorting_rule": "JOINT_ALWAYS_LAST"
  }
}
</response_body>
</validation_api>

