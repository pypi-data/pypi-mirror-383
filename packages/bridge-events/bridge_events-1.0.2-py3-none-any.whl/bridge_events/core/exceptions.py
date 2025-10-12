class BaseError(Exception):
    """Base exception for application-specific errors.

    This is the parent class for all custom exceptions in the application.
    It provides a common interface for accessing error messages.
    """

    def __init__(self, message: str) -> None:
        """Initialize the error with a descriptive message."""
        super().__init__(message)
        self._message = message

    @property
    def message(self) -> str:
        """Get the error message."""
        return self._message


class BridgeError(BaseError):
    """Exception for Bridge webhook processing issues.

    Used to indicate problems with webhook handling, signature verification,
    or event processing.
    """
