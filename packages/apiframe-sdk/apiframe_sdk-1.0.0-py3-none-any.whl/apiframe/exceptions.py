"""
Apiframe SDK Exception Classes
"""

from typing import Any, Optional


class ApiframeError(Exception):
    """Base exception for all Apiframe errors"""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status: Optional[int] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.details = details

    def __str__(self) -> str:
        return self.message


class ValidationError(ApiframeError):
    """Validation error"""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message, "VALIDATION_ERROR", 400, details)


class AuthenticationError(ApiframeError):
    """Authentication error"""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, "AUTHENTICATION_ERROR", 401)


class RateLimitError(ApiframeError):
    """Rate limit exceeded error"""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, "RATE_LIMIT_ERROR", 429)


class TimeoutError(ApiframeError):
    """Request timeout error"""

    def __init__(self, message: str = "Request timeout") -> None:
        super().__init__(message, "TIMEOUT_ERROR", 408)

