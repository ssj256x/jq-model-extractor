from typing import Optional

from app.models import JqModel, Jq, JqMode, Computed
from app.models.address import Address
from app.services.random_data import get_large_random_data_json
from app.utils.computed_functions import full_name


class UserSummary(JqModel):
    user_id: str = Jq(".id")
    email: str = Jq(".profile.contact.email")
    phone_verified: bool = Jq(".profile.contact.phone.verified")
    primary_city: Optional[str] = Jq(".profile.addresses[] | select(.primary == true) | .location.city")
    premium_price: Optional[float] = Jq(".subscriptions[] | select(.plan == \"PREMIUM\") | .billing.price")


class UserAddressSummary(JqModel):
    user_id: str = Jq(".id")
    name: str = Computed(fn=full_name, description="User's name as single string")
    address: list[Address] = Jq("""
        .profile.addresses[] 
        | {
            address_line: (
                .location.street + ", " +
                .location.city + ", " +
                .location.state + ", " +
                .location.country + " - " +
                .location.postalCode
            ),
            geo: {
                lat: .geo.lat,
                lon: .geo.lng
            }
        }
        """, mode=JqMode.MANY)

print(UserSummary.from_json(get_large_random_data_json()))