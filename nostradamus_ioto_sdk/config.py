"""Configuration management for the Nostradamus IoTO SDK."""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClientConfig:
    """Configuration for the Nostradamus IoTO client.

    Attributes:
        base_url: Base URL of the API
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff factor for retries
        enable_cache: Enable response caching for GET requests
        cache_ttl: Cache time-to-live in seconds
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        verify_ssl: Verify SSL certificates

    Example:
        >>> config = ClientConfig(
        ...     base_url="https://api.example.com",
        ...     max_retries=5,
        ...     enable_cache=True
        ... )
    """

    base_url: str = "https://nostradamus-ioto.issel.ee.auth.gr"
    timeout: float = 30.0
    max_retries: int = 3
    backoff_factor: float = 0.5
    enable_cache: bool = False
    cache_ttl: int = 60
    log_level: str = "INFO"
    verify_ssl: bool = True

    @classmethod
    def from_env(cls, prefix: str = "NOSTRADAMUS_") -> "ClientConfig":
        """Create configuration from environment variables.

        Environment variables:
            NOSTRADAMUS_BASE_URL: API base URL
            NOSTRADAMUS_TIMEOUT: Request timeout
            NOSTRADAMUS_MAX_RETRIES: Maximum retries
            NOSTRADAMUS_BACKOFF_FACTOR: Retry backoff factor
            NOSTRADAMUS_ENABLE_CACHE: Enable caching (true/false)
            NOSTRADAMUS_CACHE_TTL: Cache TTL in seconds
            NOSTRADAMUS_LOG_LEVEL: Logging level
            NOSTRADAMUS_VERIFY_SSL: Verify SSL (true/false)

        Args:
            prefix: Prefix for environment variable names

        Returns:
            ClientConfig instance with values from environment

        Example:
            >>> os.environ["NOSTRADAMUS_BASE_URL"] = "https://custom.api.com"
            >>> config = ClientConfig.from_env()
            >>> config.base_url
            'https://custom.api.com'
        """
        return cls(
            base_url=os.getenv(f"{prefix}BASE_URL", cls.base_url),
            timeout=float(os.getenv(f"{prefix}TIMEOUT", str(cls.timeout))),
            max_retries=int(os.getenv(f"{prefix}MAX_RETRIES", str(cls.max_retries))),
            backoff_factor=float(
                os.getenv(f"{prefix}BACKOFF_FACTOR", str(cls.backoff_factor))
            ),
            enable_cache=os.getenv(f"{prefix}ENABLE_CACHE", "false").lower() == "true",
            cache_ttl=int(os.getenv(f"{prefix}CACHE_TTL", str(cls.cache_ttl))),
            log_level=os.getenv(f"{prefix}LOG_LEVEL", cls.log_level).upper(),
            verify_ssl=os.getenv(f"{prefix}VERIFY_SSL", "true").lower() == "true",
        )


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff factor (delay = backoff_factor * (2 ** attempt))
        retry_on_status: HTTP status codes that trigger retry
        max_backoff: Maximum backoff delay in seconds
    """

    max_retries: int = 3
    backoff_factor: float = 0.5
    retry_on_status: tuple = field(
        default_factory=lambda: (408, 429, 500, 502, 503, 504)
    )
    max_backoff: float = 60.0

    def get_backoff_delay(self, attempt: int) -> float:
        """Calculate backoff delay for given attempt.

        Args:
            attempt: Retry attempt number (0-based)

        Returns:
            Delay in seconds
        """
        delay = self.backoff_factor * (2**attempt)
        return min(delay, self.max_backoff)
