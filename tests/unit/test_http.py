"""Unit tests for HTTP utilities."""

import pytest
import time
import asyncio
from datetime import datetime, timedelta

from nostradamus_ioto_sdk._http import ResponseCache, RateLimiter, should_retry
from nostradamus_ioto_sdk.config import RetryConfig


class TestResponseCache:
    """Test response cache functionality."""

    def test_cache_creation(self):
        """Test creating a cache."""
        cache = ResponseCache(ttl=60, max_size=100)
        assert cache._ttl == 60
        assert cache._max_size == 100

    def test_cache_set_and_get(self):
        """Test setting and getting cached values."""
        cache = ResponseCache(ttl=60)
        cache.set("key1", {"data": "value1"})
        result = cache.get("key1")
        assert result == {"data": "value1"}

    def test_cache_get_nonexistent_key(self):
        """Test getting non-existent key returns None."""
        cache = ResponseCache(ttl=60)
        result = cache.get("nonexistent")
        assert result is None

    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = ResponseCache(ttl=1)  # 1 second TTL
        cache.set("key1", "value1")

        # Should be cached
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("key1") is None

    def test_cache_lru_eviction(self):
        """Test LRU eviction when max size reached."""
        cache = ResponseCache(ttl=60, max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # All should be cached
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

        # Add a fourth item, should evict key1 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_cache_lru_access_updates_order(self):
        """Test accessing items updates LRU order."""
        cache = ResponseCache(ttl=60, max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it recently used
        cache.get("key1")

        # Add key4, should evict key2 (now least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # Still cached
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = ResponseCache(ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_invalidate_pattern(self):
        """Test invalidating cache entries by pattern."""
        cache = ResponseCache(ttl=60)
        cache.set("user:1:profile", "profile1")
        cache.set("user:2:profile", "profile2")
        cache.set("post:1:data", "post1")

        # Invalidate all user entries
        cache.invalidate("user:")

        assert cache.get("user:1:profile") is None
        assert cache.get("user:2:profile") is None
        assert cache.get("post:1:data") == "post1"  # Should still exist

    def test_cache_invalidate_all(self):
        """Test invalidating all cache entries."""
        cache = ResponseCache(ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.invalidate(None)

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_generate_key(self):
        """Test cache key generation."""
        cache = ResponseCache(ttl=60)

        key1 = cache._generate_key("GET", "/api/users", {"page": 1, "size": 10})
        key2 = cache._generate_key("GET", "/api/users", {"size": 10, "page": 1})

        # Keys should be the same (params sorted)
        assert key1 == key2

        key3 = cache._generate_key("GET", "/api/users", {"page": 2, "size": 10})
        assert key1 != key3

    def test_cache_thread_safety(self):
        """Test cache is thread-safe."""
        import threading

        cache = ResponseCache(ttl=60)
        results = []

        def set_and_get(key, value):
            cache.set(key, value)
            time.sleep(0.01)  # Small delay
            result = cache.get(key)
            results.append(result)

        threads = [
            threading.Thread(target=set_and_get, args=(f"key{i}", f"value{i}"))
            for i in range(10)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All values should have been retrieved successfully
        assert len(results) == 10
        assert all(r is not None for r in results)


class TestRateLimiter:
    """Test rate limiter functionality."""

    def test_rate_limiter_creation(self):
        """Test creating a rate limiter."""
        limiter = RateLimiter(requests_per_second=10)
        assert limiter._rate == 10

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
        original_rate = limiter._rate

        # Handle rate limit (should reduce rate by 50%)
        limiter.handle_rate_limit()

        assert limiter._rate == original_rate * 0.5
        assert limiter._tokens == 0.0

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

        assert limiter._rate >= 1.0


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
