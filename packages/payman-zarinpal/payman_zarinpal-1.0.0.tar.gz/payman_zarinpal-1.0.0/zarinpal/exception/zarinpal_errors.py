from payman.core.exceptions.base import GatewayError


class ZarinPalGatewayException(GatewayError):
    """Base class for all ZarinPal errors."""

    def __init__(self, message: str = "An unknown error occurred with ZarinPal."):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


class ValidationException(ZarinPalGatewayException):
    """Raised for general data validation issues."""

    pass


class MerchantIDException(ZarinPalGatewayException):
    """Raised when the merchant ID is missing or invalid."""

    pass


class TerminalException(ZarinPalGatewayException):
    """Raised when there is an issue with the terminal or merchant permissions."""

    pass


class PaymentException(ZarinPalGatewayException):
    """Raised for payment-related errors like insufficient funds or transaction rejection."""

    pass


class SessionException(ZarinPalGatewayException):
    """Raised when a payment session is invalid, incomplete, or expired."""

    pass


class AuthorityException(ZarinPalGatewayException):
    """Raised when an invalid authority code is used or not found."""

    pass


class ReverseException(ZarinPalGatewayException):
    """Raised for errors occurring during transaction reversal."""

    pass


class AlreadyVerifiedException(ZarinPalGatewayException):
    """Raised when trying to verify a transaction that is already verified."""

    pass


class PaymentNotCompletedException(SessionException):
    """Raised when user never completed the payment (canceled, closed page, etc)."""

    pass


ZARINPAL_ERRORS = {
    -9: ValidationException,
    -10: MerchantIDException,
    -11: TerminalException,
    -12: PaymentException,
    -15: TerminalException,
    -16: TerminalException,
    -17: TerminalException,
    -18: PaymentException,
    -19: PaymentException,
    -30: PaymentException,
    -31: PaymentException,
    -32: PaymentException,
    -33: PaymentException,
    -34: PaymentException,
    -35: PaymentException,
    -36: PaymentException,
    -37: PaymentException,
    -38: PaymentException,
    -39: PaymentException,
    -40: PaymentException,
    -41: PaymentException,
    -50: PaymentNotCompletedException,
    -51: SessionException,
    -52: ZarinPalGatewayException,
    -53: SessionException,
    -54: AuthorityException,
    -55: SessionException,
    -60: ReverseException,
    -61: ReverseException,
    -62: ReverseException,
    -63: ReverseException,
}
