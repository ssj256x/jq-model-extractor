import json
import pprint
from typing import Annotated, Optional

from result import Ok, Err, Result
import jq

from core.model import JqModel
from core.resolver import Jq, JqMode, Computed
from core.transform import Transform


def unwrap(result: Result):
    match result:
        case Ok(value):
            print("Success: ", value.model_dump_json(indent=2))
        case Err(error):
            print("Error: ")
            pprint.pprint(error)


def transform_geo(data):
    for d in data:
        lat = d["geo"]["lat"]
        lon = d["geo"]["lon"]
        d["geo"] = f"Lat:{lat} # Lon: {lon}"
    return data


def create_one_line_address(data):
    return jq.compile('''
        (
            .location.street + ", " +
            .location.city + ", " +
            .location.state + ", " +
            .location.country + " - " +
            .location.postalCode
        )
    ''').input_value(data).all()[0]


def full_name(data: dict) -> str:
    parts = [
        jq.compile('.profile.name.first').input_value(data).all()[0],
        jq.compile('.profile.name.middle').input_value(data).all()[0],
        jq.compile('.profile.name.last').input_value(data).all()[0]
    ]

    return " ".join(p for p in parts if p)


class Audit(JqModel):
    auditedBy: Annotated[
        str,
        Jq(".audit.lastUpdated.by", required=True)
    ]

    auditedDate: Annotated[
        str,
        Jq(".audit.lastUpdated.at")
    ]


class Address(JqModel):
    address_line: Annotated[
        str,
        Jq('.profile.addresses[]', mode=JqMode.ONE, required=True),
        Transform(create_one_line_address)
    ]


class UserDetailsConcise(JqModel):
    user_id: Annotated[
        str,
        Jq(".id"),
        Transform(str.upper)
    ]

    full_name: Annotated[
        str,
        Computed(full_name),
        Transform(str.upper),
    ]

    email: Annotated[
        str,
        Jq(".profile.contact.email")
    ]

    phone_verified: Annotated[
        bool,
        Jq(".profile.contact.phone.verified")
    ]

    primary_city: Annotated[
        Optional[str],
        Jq(".profile.addresses[] | select(.primary == true) | .location.city")
    ]

    premium_price: Annotated[
        Optional[float],
        Jq(".subscriptions[] | select(.plan == \"PREMIUM\") | .billing.price")
    ]

    audit: Audit

    address: Address


with open('user.json') as f:
    users = json.loads(f.read())
    u = UserDetailsConcise.from_json(json.loads(users))
    unwrap(u)
