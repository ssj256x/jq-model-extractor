import json

from result import Ok, Err, Result
from typing import Annotated
from jresolve import (
    JqModel,
    Jq,
    Transform,
    Computed,
    JqMode
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
        int,
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
            print("Error: \n", error)
