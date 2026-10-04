from app.schemas.common import CamelModel


class Address(CamelModel):
    id: int
    first_name: str
    last_name: str
    line1: str
    city: str
    state: str
    pin: str
    country: str
    phone: str
    email: str | None = None
    is_default: bool = False


class AddressCreate(CamelModel):
    first_name: str
    last_name: str
    line1: str
    city: str
    state: str
    pin: str
    country: str
    phone: str
    email: str | None = None
    is_default: bool = False
