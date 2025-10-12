from typing import Any

from payman.core.http import AsyncHttpClient

from .error_mapper import ErrorMapper


class ZarinpalHttpClient:
    """
    Asynchronous HTTP client for interacting with Zarinpal API.
    Automatically attaches the merchant ID and applies error mapping.
    """

    def __init__(
        self,
        merchant_id: str,
        base_url: str,
        http_client: AsyncHttpClient,
        error_mapper: ErrorMapper,
    ) -> None:
        """
        Args:
            merchant_id: Zarinpal merchant identifier.
            base_url: Base URL for ZarinPal API endpoints.
            http_client: Async HTTP client for making requests.
            error_mapper: Maps API responses to domain-specific exceptions.
        """

        self._merchant_id = merchant_id
        self._base_url = base_url.rstrip("/")
        self._http = http_client
        self._error_mapper = error_mapper

    async def post(
        self, endpoint: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Send a POST request with standardized error handling.

        Args:
            endpoint: API endpoint (e.g. '/pg/rest/WebGate/PaymentRequest.json').
            payload: Optional JSON body to include with the request.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            GatewayError: If the API response indicates an error.
        """

        url = f"{self._base_url}/{endpoint.lstrip('/')}"

        body = {"merchant_id": self._merchant_id}
        if payload:
            body.update(payload)

        response = await self._http.request("POST", url, json_data=body)

        # The mapper raises GatewayError internally if needed
        self._error_mapper.map(response)

        return response
