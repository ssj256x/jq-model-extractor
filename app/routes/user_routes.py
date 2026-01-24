import json

from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.models.users import UserSummary, UserAddressSummary
from app.services.random_data import get_large_random_data_json

router = APIRouter(tags=["JQ"])


@router.get("/rjq")
def random_data_route():
    j = json.loads(get_large_random_data_json())
    return JSONResponse(content=j, status_code=200)


@router.get("/user_summary")
def get_user_summary():
    data = json.loads(get_large_random_data_json())
    u = UserSummary.from_json(data)
    return u


@router.get("/user_address_summary")
def get_user_address_summary():
    data = json.loads(get_large_random_data_json())
    u = UserAddressSummary.from_json(data)
    return u
