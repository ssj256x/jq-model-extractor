from pydantic import BaseModel


class Geo(BaseModel):
    lat: float
    lon: float


class Address(BaseModel):
    address_line: str
    geo: Geo | str
