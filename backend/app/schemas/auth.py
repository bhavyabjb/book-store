from pydantic import EmailStr, Field

from app.schemas.common import CamelModel


class RegisterRequest(CamelModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: str | None = None


class LoginRequest(CamelModel):
    email: EmailStr
    password: str


class UserProfile(CamelModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    gift_points_balance: int = 0


class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
