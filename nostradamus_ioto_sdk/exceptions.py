"""Custom exceptions for the Nostradamus IoTO SDK."""

from typing import Any, Dict, List, Optional

import httpx


class NostradamusError(Exception):
    """Base exception for all Nostradamus SDK errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ConfigurationError(NostradamusError):
    """Raised when the SDK is misconfigured."""


class AuthenticationError(NostradamusError):
    """Raised when authentication fails (401, 403)."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class APIError(NostradamusError):
    """Raised when an API request fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[httpx.Response] = None,
        request: Optional[httpx.Request] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.request = request

    def __str__(self) -> str:
        base_msg = self.message
        if self.status_code:
            base_msg = f"[{self.status_code}] {base_msg}"
        return base_msg


class ValidationError(APIError):
    """Raised when request validation fails (422)."""

    def __init__(
        self,
        message: str,
        errors: Optional[List[Dict[str, Any]]] = None,
        response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message, status_code=422, response=response)
        self.errors = errors or []

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.errors:
            error_details = []
            for error in self.errors:
                # Handle both dict and string errors
                if isinstance(error, dict):
                    loc = " -> ".join(str(x) for x in error.get("loc", []))
                    msg = error.get("msg", "Unknown error")
                    error_details.append(f"{loc}: {msg}")
                else:
                    error_details.append(str(error))
            return f"{base_msg}\n" + "\n".join(error_details)
        return base_msg


class ResourceNotFoundError(APIError):
    """Raised when a requested resource is not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message, status_code=404, response=response)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message, status_code=429, response=response)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.retry_after:
            return f"{base_msg} (retry after {self.retry_after}s)"
        return base_msg


class RequestTimeoutError(APIError):
    """Raised when a request times out."""

    def __init__(
        self, message: str = "Request timed out", timeout: Optional[float] = None
    ) -> None:
        super().__init__(message)
        self.timeout = timeout


class APIConnectionError(APIError):
    """Raised when connection to API fails."""
