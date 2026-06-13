"""Unit tests for HTTP utilities."""

import time

import pytest

from nostradamus_ioto_sdk._http import RateLimiter, should_retry
from nostradamus_ioto_sdk.config import RetryConfig



class TestRateLimiter:
    """Test rate limiter functionality."""

    def test_rate_limiter_creation(self):
        """Test creating a rate limiter."""
        limiter = RateLimiter(requests_per_second=10)
        assert limiter.rate == 10

    def test_rate_limiter_acquire(self):
        """Test acquiring rate limit permits."""
        limiter = RateLimiter(requests_per_second=100)

        # Should acquire immediately
        result = limiter.acquire(timeout=1.0)
        assert result is True

    def test_rate_limiter_blocks_when_exhausted(self):
        """Test rate limiter blocks when tokens exhausted."""
        limiter = RateLimiter(requests_per_second=2)

        # Acquire all tokens
        limiter.acquire()
        limiter.acquire()

        # Next acquire should timeout
        start = time.time()
        result = limiter.acquire(timeout=0.1)
        duration = time.time() - start

        assert result is False
        assert duration >= 0.1

    def test_rate_limiter_refills_over_time(self):
        """Test rate limiter refills tokens over time."""
        limiter = RateLimiter(requests_per_second=10)

        # Acquire some tokens
        limiter.acquire()
        limiter.acquire()

        # Wait for refill
        time.sleep(0.3)

        # Should be able to acquire more
        result = limiter.acquire(timeout=0.1)
        assert result is True

    def test_rate_limiter_handle_rate_limit(self):
        """Test handling rate limit response."""
        limiter = RateLimiter(requests_per_second=10)
        original_rate = limiter.rate

        limiter.handle_rate_limit()

        assert limiter.rate == original_rate * 0.5
        assert limiter.tokens == 0.0

    def test_rate_limiter_handle_rate_limit_with_retry_after(self):
        """Test handling rate limit with retry-after header."""
        limiter = RateLimiter(requests_per_second=10)

        start = time.time()
        limiter.handle_rate_limit(retry_after=1)
        duration = time.time() - start

        # Should have waited for retry_after seconds
        assert duration >= 0.9  # Allow small margin

    @pytest.mark.asyncio
    async def test_rate_limiter_async_acquire(self):
        """Test async acquire."""
        limiter = RateLimiter(requests_per_second=100)

        result = await limiter.aacquire(timeout=1.0)
        assert result is True

    @pytest.mark.asyncio
    async def test_rate_limiter_async_blocks_when_exhausted(self):
        """Test async rate limiter blocks when exhausted."""
        limiter = RateLimiter(requests_per_second=2)

        # Acquire all tokens
        await limiter.aacquire()
        await limiter.aacquire()

        # Next acquire should timeout
        start = time.time()
        result = await limiter.aacquire(timeout=0.1)
        duration = time.time() - start

        assert result is False
        assert duration >= 0.1

    def test_rate_limiter_minimum_rate(self):
        """Test rate limiter has minimum rate of 1."""
        limiter = RateLimiter(requests_per_second=2)

        # Handle rate limit multiple times
        limiter.handle_rate_limit()  # 2 -> 1
        limiter.handle_rate_limit()  # 1 -> 0.5 but capped at 1

        assert limiter.rate >= 1.0


class TestShouldRetry:
    """Test should_retry function."""

    def test_should_retry_with_retryable_status(self):
        """Test should_retry returns True for retryable statuses."""
        retry_config = RetryConfig(retry_on_status=[500, 502, 503, 504])

        assert should_retry(500, retry_config) is True
        assert should_retry(502, retry_config) is True
        assert should_retry(503, retry_config) is True
        assert should_retry(504, retry_config) is True

    def test_should_retry_with_non_retryable_status(self):
        """Test should_retry returns False for non-retryable statuses."""
        retry_config = RetryConfig(retry_on_status=[500, 502, 503, 504])

        assert should_retry(400, retry_config) is False
        assert should_retry(401, retry_config) is False
        assert should_retry(404, retry_config) is False
        assert should_retry(200, retry_config) is False

    def test_should_retry_with_custom_retry_statuses(self):
        """Test should_retry with custom retry statuses."""
        retry_config = RetryConfig(retry_on_status=[408, 429])

        assert should_retry(408, retry_config) is True
        assert should_retry(429, retry_config) is True
        assert should_retry(500, retry_config) is False
