class NaykiError(Exception):
    """Base error class for Nayki app exceptions."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(NaykiError):
    """Exception raised when a resource is not found."""
    pass


class UnauthorizedError(NaykiError):
    """Exception raised when a user is not authenticated or authorized."""
    pass


class ValidationError(NaykiError):
    """Exception raised when input data fails domain validation."""
    pass


class ConfigurationError(NaykiError):
    """Exception raised when system configurations are invalid."""
    pass
