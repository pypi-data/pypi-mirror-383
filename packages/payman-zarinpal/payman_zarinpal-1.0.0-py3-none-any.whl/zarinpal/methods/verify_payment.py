from payman.utils import to_model_instance

from ..models import VerifyRequest, VerifyResponse


class VerifyPayment:
    async def verify_payment(
        self: "ZarinPal", params: VerifyRequest | dict | None = None, **kwargs
    ) -> VerifyResponse:
        """
        Verify the transaction status after the payment is complete.

        Args:
           params (VerifyRequest | dict, optional): Verification input containing the `authority`.
                Can be passed as a Pydantic model,
                dictionary, or directly via keyword arguments.

        Returns:
            VerifyResponse: Verification result including ref_id.
        """

        parsed = to_model_instance(params, VerifyRequest, **kwargs).model_dump(
            mode="json"
        )
        response = await self.client.post("/verify.json", parsed)
        return VerifyResponse(**response.get("data"))
