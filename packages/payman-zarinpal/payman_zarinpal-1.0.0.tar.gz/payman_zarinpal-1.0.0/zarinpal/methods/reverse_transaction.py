from payman.utils import to_model_instance

from ..models import ReverseRequest, ReverseResponse


class ReverseTransaction:
    async def reverse(
        self: "ZarinPal", params: ReverseRequest | dict | None = None, **kwargs
    ) -> ReverseResponse:
        """
        Reverses a pending or unsettled transaction in ZarinPal.

        This method is used when a payment session has not yet been settled,
        and you want to cancel or refund it before it's finalized by ZarinPal.

        Args:
            params (ReverseRequest | dict | None): Details of the transaction to be reversed.
                You can provide:
                - A `ReverseRequest` Pydantic model
                - A plain dictionary with equivalent fields
                - Or keyword arguments (`**kwargs`) matching the model fields

        Returns:
            ReverseResponse: Contains information about the reversal status and messages.
        """

        parsed = to_model_instance(params, ReverseRequest, **kwargs).model_dump(
            mode="json"
        )
        response = await self.client.post("/reverse.json", parsed)
        return ReverseResponse(**response.get("data"))
