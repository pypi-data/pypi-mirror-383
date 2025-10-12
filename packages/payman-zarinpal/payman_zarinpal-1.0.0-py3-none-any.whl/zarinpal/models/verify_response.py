from pydantic import BaseModel, Field
from .wage import WageResponse
from ..enums import Status


class VerifyResponse(BaseModel):
    code: Status = Field(..., description="Result code of payment verification")
    ref_id: int | None = Field(
        None, description="Transaction reference ID if payment was successful"
    )
    card_pan: str | None = Field(
        None, description="Masked card number used for payment"
    )
    card_hash: str | None = Field(None, description="SHA256 hash of the card number")
    fee_type: str | None = Field(
        None, description="Entity responsible for paying the fee (buyer or merchant)"
    )
    fee: int | None = Field(None, description="Fee amount charged for the transaction")
    message: str | None = Field(None, description="Additional message or error details")
    wages: list[WageResponse] | None = None

    @property
    def success(self) -> bool:
        return self.code == Status.SUCCESS

    @property
    def already_verified(self) -> bool:
        return self.code == Status.ALREADY_VERIFIED
