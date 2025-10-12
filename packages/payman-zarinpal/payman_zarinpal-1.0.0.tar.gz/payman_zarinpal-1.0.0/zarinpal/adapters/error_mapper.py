from zarinpal.exception.zarinpal_errors import ZARINPAL_ERRORS, ZarinPalGatewayException


class ErrorMapper:
    def __init__(
        self, errors_map: dict[int, type[Exception]], base_exc: type[Exception]
    ):
        self.errors_map = errors_map
        self.base_exc = base_exc

    def map(self, response: dict) -> None:
        """Raise the appropriate exception based on ZarinPal API response."""
        if not response:
            raise self.base_exc("Empty response from ZarinPal API.")

        errors = response.get("errors")
        if not errors:
            return  # success case

        code = errors.get("code")
        exc_cls = self.errors_map.get(code, self.base_exc)
        raise exc_cls(errors.get("message", f"Unknown error (code={code})"))


zarinpal_error_mapper = ErrorMapper(ZARINPAL_ERRORS, ZarinPalGatewayException)
