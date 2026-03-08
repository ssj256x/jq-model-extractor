# jresolve

**jresolve** is a lightweight Python library for resolving and transforming JSON data using JQ-style expressions and declarative models.

It allows you to define structured models that extract and compute fields from raw JSON inputs, making it easier to build clean data pipelines and APIs.

---

## Features

- Declarative JSON resolution using models
- JQ-style query expressions
- Computed and derived fields
- Transform pipelines
- Clear error handling
- Lightweight and dependency-friendly

---

## Examples
Suppose we have the below JSON
```json
{
  "id": "order_789",
  "created_at": "2024-02-10T14:21:00Z",
  "customer": {
    "first_name": "Alice",
    "last_name": "Smith",
    "contact": {
      "email": "ALICE@EXAMPLE.COM"
    }
  },
  "items": [
    { "name": "Keyboard", "category": "premium", "price": 120 },
    { "name": "Mouse", "category": "standard", "price": 40 },
    { "name": "Monitor", "category": "premium", "price": 300 }
  ]
}
```
and we want to transform it to
```json
{
  "order_id": "order_789",
  "customer_email": "alice@example.com",
  "item_count": 3,
  "premium_total": 420,
  "order_label": "ORDER-order_789"
}
```
we can describe the model as

```python
import json
from result import Ok, Err, Result # from the "result" lib
from typing import Annotated
from jresolve import (
    JqModel,
    Jq,
    JqMode,
    Transform,
    Computed
)
from jresolve.exceptions import ResolutionError


class OrderSummary(JqModel):
    order_id: Annotated[
        str,
        Jq(".id")
    ]

    customer_email: Annotated[
        str,
        Jq(".customer.contact.email"),
        Transform(str.lower)
    ]

    item_count: Annotated[
        int,
        Jq(".items"),
        Transform(len)
    ]

    premium_total: Annotated[
        float,
        Jq(
            ".items[] | select(.category == \"premium\") | .price", 
            mode=JqMode.MANY
        ),
        Transform(sum)
    ]

    order_label: Annotated[
        str,
        Computed(lambda d: f"ORDER-{d['id']}")
    ]


# Execute the resolution
with open('orders.json') as f:
    data = json.loads(f.read())
    result: Result[dict, ResolutionError] = OrderSummary.from_json(data)
    
    match result:
        case Ok(value):
            print("Success: ", value.model_dump_json(indent=2))
        case Err(error):
            print("Error: ", error)
```