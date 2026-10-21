"""HTTP utilities for retry, rate limiting, and caching."""

import asyncio
import threading
import time
from typing import Optional

from .config import RetryConfig


class RateLimiter:
    """Adaptive rate limiter with sliding window.

    Implements token bucket algorithm for rate limiting.
    Adapts based on 429 responses from the API.

    Args:
        requests_per_second: Initial rate limit

    Example:
        >>> limiter = RateLimiter(requests_per_second=10)
        >>> limiter.acquire()  # Blocks if rate limit exceeded
    """

    def __init__(self, requests_per_second: int = 10) -> None:
        self._rate = float(requests_per_second)
        self._tokens = float(requests_per_second)
        self._last_update = time.monotonic()
        self._lock = threading.Lock()
        self._async_lock: Optional[asyncio.Lock] = None

    @property
    def rate(self) -> float:
        """Current rate limit (requests per second)."""
        return self._rate

    @property
    def tokens(self) -> float:
        """Current number of available tokens."""
        return self._tokens

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire permission to make a request (blocking).

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if acquired, False if timeout
        """
        start_time = time.monotonic()

        while True:
            with self._lock:
                self._refill()

                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True

            if timeout and (time.monotonic() - start_time) >= timeout:
                return False

            # Sleep for a short time before retrying
            time.sleep(0.01)

    def _get_async_lock(self) -> asyncio.Lock:
        """Get or create the async lock (lazy initialization)."""
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    async def aacquire(self, timeout: Optional[float] = None) -> bool:
        """Async acquire permission to make a request.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if acquired, False if timeout
        """
        start_time = time.monotonic()

        while True:
            async with self._get_async_lock():
                self._refill()

                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True

            if timeout and (time.monotonic() - start_time) >= timeout:
                return False

            # Sleep for a short time before retrying
            await asyncio.sleep(0.01)

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_update
        self._tokens = min(self._rate, self._tokens + elapsed * self._rate)
        self._last_update = now

    def handle_rate_limit(self, retry_after: Optional[int] = None) -> None:
        """Adapt rate limit based on 429 response.

        Args:
            retry_after: Seconds to wait from Retry-After header
        """
        with self._lock:
            # Reduce rate by 50% when hit with rate limit
            self._rate = max(1.0, self._rate * 0.5)
            self._tokens = 0.0  # Reset tokens

            if retry_after:
                # Wait for the specified time
                time.sleep(retry_after)
            else:
                # Default backoff
                time.sleep(1.0)


def should_retry(status_code: int, retry_config: RetryConfig) -> bool:
    """Determine if request should be retried based on status code.

    Args:
        status_code: HTTP status code
        retry_config: Retry configuration

    Returns:
        True if should retry, False otherwise
    """
    return status_code in retry_config.retry_on_status
