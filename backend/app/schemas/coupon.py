from app.schemas.common import CamelModel


class CouponApplyRequest(CamelModel):
    code: str


class CouponApplyResponse(CamelModel):
    code: str
    discount: float
    new_total: float
