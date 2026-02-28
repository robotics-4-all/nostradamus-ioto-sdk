"""Logging utilities for the Nostradamus IoTO SDK."""

import logging
import re
from typing import Any, Optional

# Patterns for sensitive data masking
SENSITIVE_PATTERNS = [
    (
        re.compile(r"(api[-_]?key['\"]?\s*[:=]\s*['\"]?)([^'\"]+)", re.I),
        r"\1***REDACTED***",
    ),
    (
        re.compile(r"(authorization['\"]?\s*[:=]\s*['\"]?)([^'\"]+)", re.I),
        r"\1***REDACTED***",
    ),
    (
        re.compile(r"(x-api-key['\"]?\s*[:=]\s*['\"]?)([^'\"]+)", re.I),
        r"\1***REDACTED***",
    ),
    (
        re.compile(r"(password['\"]?\s*[:=]\s*['\"]?)([^'\"]+)", re.I),
        r"\1***REDACTED***",
    ),
    (re.compile(r"(token['\"]?\s*[:=]\s*['\"]?)([^'\"]+)", re.I), r"\1***REDACTED***"),
    (re.compile(r"(bearer\s+)([^\s]+)", re.I), r"\1***REDACTED***"),
]


def mask_sensitive_data(text: str) -> str:
    """Mask sensitive information in text.

    Args:
        text: Text that may contain sensitive data

    Returns:
        Text with sensitive data masked
    """
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def mask_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Mask sensitive information in dictionary.

    Args:
        data: Dictionary that may contain sensitive data

    Returns:
        Dictionary with sensitive data masked
    """
    masked: dict[str, Any] = {}
    sensitive_keys = {
        "api_key",
        "api-key",
        "apikey",
        "authorization",
        "x-api-key",
        "password",
        "token",
        "access_token",
        "refresh_token",
    }

    for key, value in data.items():
        if key.lower() in sensitive_keys:
            masked[key] = "***REDACTED***"
        elif isinstance(value, dict):
            masked[key] = mask_dict(value)
        elif isinstance(value, str):
            masked[key] = mask_sensitive_data(value)
        else:
            masked[key] = value

    return masked


class SDKLogger:
    """Structured logger for the SDK with sensitive data masking.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> logger = SDKLogger("nostradamus.client", "INFO")
        >>> logger.log_request("GET", "https://api.example.com/projects", {...})
    """

    def __init__(self, name: str, level: str = "INFO") -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper()))

        # Add handler if none exists
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def log_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict[str, str]] = None,
        body: Optional[Any] = None,
    ) -> None:
        """Log HTTP request with masked sensitive data.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
        """
        masked_headers = mask_dict(headers) if headers else {}

        log_msg = f"Request: {method} {url}"
        if headers:
            log_msg += f"\nHeaders: {masked_headers}"
        if body:
            if isinstance(body, dict):
                log_msg += f"\nBody: {mask_dict(body)}"
            elif isinstance(body, str):
                log_msg += f"\nBody: {mask_sensitive_data(body)}"

        self._logger.debug(log_msg)

    def log_response(
        self,
        status_code: int,
        body: Optional[Any] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Log HTTP response.

        Args:
            status_code: HTTP status code
            body: Response body
            duration: Request duration in seconds
        """
        log_msg = f"Response: {status_code}"
        if duration:
            log_msg += f" ({duration:.3f}s)"
        if body:
            # Limit body size in logs
            body_str = str(body)
            if len(body_str) > 500:
                body_str = body_str[:500] + "... (truncated)"
            log_msg += f"\nBody: {body_str}"

        self._logger.debug(log_msg)

    def log_error(
        self, error: Exception, context: Optional[dict[str, Any]] = None
    ) -> None:
        """Log error with context.

        Args:
            error: Exception that occurred
            context: Additional context information
        """
        log_msg = f"Error: {type(error).__name__}: {error}"
        if context:
            masked_context = mask_dict(context)
            log_msg += f"\nContext: {masked_context}"

        self._logger.error(log_msg, exc_info=True)

    def debug(self, message: str) -> None:
        """Log debug message."""
        self._logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self._logger.error(message)


def get_logger(name: str, level: str = "INFO") -> SDKLogger:
    """Get SDK logger instance.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        SDKLogger instance
    """
    return SDKLogger(name, level)
