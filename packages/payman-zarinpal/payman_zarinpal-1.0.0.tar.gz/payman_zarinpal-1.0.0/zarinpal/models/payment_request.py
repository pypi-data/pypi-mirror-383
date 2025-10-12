from typing import Union
from pydantic import (
    BaseModel,
    Field,
    AnyHttpUrl,
    EmailStr,
    constr,
    conint,
    field_validator,
)
from .wage import Wage


class PaymentMetadata(BaseModel):
    mobile: constr(pattern=r"^09\d{9}$") | None = None
    email: EmailStr | str | None = None
    order_id: str | None = None


class PaymentRequest(BaseModel):
    amount: conint(ge=1000)
    currency: str = Field(default="IRR", pattern=r"^(IRR|IRT)$")
    description: str
    callback_url: AnyHttpUrl
    metadata: Union[PaymentMetadata, dict[str, Union[str, int]], None] = None
    referrer_id: str | None = None
    wages: list[Wage] = Field(default_factory=list)

    @field_validator("wages")
    def check_wages_length(cls, v):
        if not (1 <= len(v) <= 5):
            raise ValueError("wages must contain between 1 and 5 items")
        return v
