"""HTTP utilities for retry, rate limiting, and caching."""

import asyncio
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from .config import RetryConfig


class ResponseCache:
    """TTL-based cache for GET requests.

    Thread-safe and async-safe cache implementation.

    Args:
        ttl: Time-to-live in seconds for cached responses
        max_size: Maximum number of cached items

    Example:
        >>> cache = ResponseCache(ttl=60, max_size=100)
        >>> cache.set("key1", {"data": "value"})
        >>> result = cache.get("key1")
    """

    def __init__(self, ttl: int = 60, max_size: int = 100) -> None:
        self._ttl = ttl
        self._max_size = max_size
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._lock = threading.Lock()
        self._access_order: deque = deque(maxlen=max_size)

    def _generate_key(
        self, method: str, url: str, params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate cache key from request parameters.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters

        Returns:
            Cache key string
        """
        params_str = ""
        if params:
            sorted_params = sorted(params.items())
            params_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        return f"{method}:{url}:{params_str}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key in self._cache:
                value, expires_at = self._cache[key]
                if datetime.now() < expires_at:
                    # Move to end (most recently used)
                    self._access_order.remove(key)
                    self._access_order.append(key)
                    return value
                else:
                    # Expired, remove it
                    del self._cache[key]
                    if key in self._access_order:
                        self._access_order.remove(key)
            return None

    def set(self, key: str, value: Any) -> None:
        """Store value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            # Evict least recently used if at max size
            if (
                len(self._cache) >= self._max_size
                and key not in self._cache
                and self._access_order
            ):
                lru_key = self._access_order.popleft()
                if lru_key in self._cache:
                    del self._cache[lru_key]

            expires_at = datetime.now() + timedelta(seconds=self._ttl)
            self._cache[key] = (value, expires_at)

            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()

    def invalidate(self, pattern: Optional[str] = None) -> None:
        """Invalidate cache entries matching pattern.

        Args:
            pattern: Pattern to match (None = clear all)
        """
        if pattern is None:
            self.clear()
            return

        with self._lock:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)


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
