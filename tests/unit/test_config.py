"""Unit tests for configuration."""

import pytest
import os

from nostradamus_ioto_sdk.config import ClientConfig, RetryConfig


class TestClientConfig:
    """Test ClientConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ClientConfig()
        assert config.base_url == "https://nostradamus-ioto.issel.ee.auth.gr"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.backoff_factor == 0.5
        assert config.enable_cache is False
        assert config.cache_ttl == 60
        assert config.log_level == "INFO"
        assert config.verify_ssl is True

    def test_custom_config(self):
        """Test creating config with custom values."""
        config = ClientConfig(
            base_url="https://custom.api.com",
            timeout=60.0,
            max_retries=5,
            backoff_factor=1.0,
            enable_cache=True,
            cache_ttl=120,
            log_level="DEBUG",
            verify_ssl=False,
        )
        assert config.base_url == "https://custom.api.com"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.backoff_factor == 1.0
        assert config.enable_cache is True
        assert config.cache_ttl == 120
        assert config.log_level == "DEBUG"
        assert config.verify_ssl is False

    def test_from_env_default(self, monkeypatch):
        """Test from_env with no environment variables."""
        # Clear any existing env vars
        for key in list(os.environ.keys()):
            if key.startswith("NOSTRADAMUS_"):
                monkeypatch.delenv(key, raising=False)

        config = ClientConfig.from_env()
        assert config.base_url == "https://nostradamus-ioto.issel.ee.auth.gr"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_from_env_custom_base_url(self, monkeypatch):
        """Test from_env with custom base URL."""
        monkeypatch.setenv("NOSTRADAMUS_BASE_URL", "https://custom.example.com")
        config = ClientConfig.from_env()
        assert config.base_url == "https://custom.example.com"

    def test_from_env_custom_timeout(self, monkeypatch):
        """Test from_env with custom timeout."""
        monkeypatch.setenv("NOSTRADAMUS_TIMEOUT", "60.5")
        config = ClientConfig.from_env()
        assert config.timeout == 60.5

    def test_from_env_custom_max_retries(self, monkeypatch):
        """Test from_env with custom max_retries."""
        monkeypatch.setenv("NOSTRADAMUS_MAX_RETRIES", "10")
        config = ClientConfig.from_env()
        assert config.max_retries == 10

    def test_from_env_custom_backoff_factor(self, monkeypatch):
        """Test from_env with custom backoff_factor."""
        monkeypatch.setenv("NOSTRADAMUS_BACKOFF_FACTOR", "2.0")
        config = ClientConfig.from_env()
        assert config.backoff_factor == 2.0

    def test_from_env_enable_cache_true(self, monkeypatch):
        """Test from_env with cache enabled."""
        monkeypatch.setenv("NOSTRADAMUS_ENABLE_CACHE", "true")
        config = ClientConfig.from_env()
        assert config.enable_cache is True

    def test_from_env_enable_cache_false(self, monkeypatch):
        """Test from_env with cache disabled."""
        monkeypatch.setenv("NOSTRADAMUS_ENABLE_CACHE", "false")
        config = ClientConfig.from_env()
        assert config.enable_cache is False

    def test_from_env_enable_cache_case_insensitive(self, monkeypatch):
        """Test from_env cache flag is case insensitive."""
        monkeypatch.setenv("NOSTRADAMUS_ENABLE_CACHE", "TRUE")
        config = ClientConfig.from_env()
        assert config.enable_cache is True

    def test_from_env_custom_cache_ttl(self, monkeypatch):
        """Test from_env with custom cache TTL."""
        monkeypatch.setenv("NOSTRADAMUS_CACHE_TTL", "300")
        config = ClientConfig.from_env()
        assert config.cache_ttl == 300

    def test_from_env_custom_log_level(self, monkeypatch):
        """Test from_env with custom log level."""
        monkeypatch.setenv("NOSTRADAMUS_LOG_LEVEL", "debug")
        config = ClientConfig.from_env()
        assert config.log_level == "DEBUG"

    def test_from_env_verify_ssl_true(self, monkeypatch):
        """Test from_env with SSL verification enabled."""
        monkeypatch.setenv("NOSTRADAMUS_VERIFY_SSL", "true")
        config = ClientConfig.from_env()
        assert config.verify_ssl is True

    def test_from_env_verify_ssl_false(self, monkeypatch):
        """Test from_env with SSL verification disabled."""
        monkeypatch.setenv("NOSTRADAMUS_VERIFY_SSL", "false")
        config = ClientConfig.from_env()
        assert config.verify_ssl is False

    def test_from_env_custom_prefix(self, monkeypatch):
        """Test from_env with custom prefix."""
        monkeypatch.setenv("CUSTOM_BASE_URL", "https://prefix.example.com")
        config = ClientConfig.from_env(prefix="CUSTOM_")
        assert config.base_url == "https://prefix.example.com"

    def test_from_env_all_variables(self, monkeypatch):
        """Test from_env with all environment variables set."""
        monkeypatch.setenv("NOSTRADAMUS_BASE_URL", "https://full.example.com")
        monkeypatch.setenv("NOSTRADAMUS_TIMEOUT", "45.0")
        monkeypatch.setenv("NOSTRADAMUS_MAX_RETRIES", "7")
        monkeypatch.setenv("NOSTRADAMUS_BACKOFF_FACTOR", "1.5")
        monkeypatch.setenv("NOSTRADAMUS_ENABLE_CACHE", "true")
        monkeypatch.setenv("NOSTRADAMUS_CACHE_TTL", "180")
        monkeypatch.setenv("NOSTRADAMUS_LOG_LEVEL", "warning")
        monkeypatch.setenv("NOSTRADAMUS_VERIFY_SSL", "false")

        config = ClientConfig.from_env()
        assert config.base_url == "https://full.example.com"
        assert config.timeout == 45.0
        assert config.max_retries == 7
        assert config.backoff_factor == 1.5
        assert config.enable_cache is True
        assert config.cache_ttl == 180
        assert config.log_level == "WARNING"
        assert config.verify_ssl is False


class TestRetryConfig:
    """Test RetryConfig class."""

    def test_default_retry_config(self):
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.backoff_factor == 0.5
        assert config.retry_on_status == (408, 429, 500, 502, 503, 504)
        assert config.max_backoff == 60.0

    def test_custom_retry_config(self):
        """Test custom retry configuration."""
        config = RetryConfig(
            max_retries=5,
            backoff_factor=1.0,
            retry_on_status=(500, 502),
            max_backoff=120.0,
        )
        assert config.max_retries == 5
        assert config.backoff_factor == 1.0
        assert config.retry_on_status == (500, 502)
        assert config.max_backoff == 120.0

    def test_get_backoff_delay_first_attempt(self):
        """Test backoff delay for first attempt."""
        config = RetryConfig(backoff_factor=0.5)
        delay = config.get_backoff_delay(0)
        assert delay == 0.5  # 0.5 * 2^0 = 0.5

    def test_get_backoff_delay_second_attempt(self):
        """Test backoff delay for second attempt."""
        config = RetryConfig(backoff_factor=0.5)
        delay = config.get_backoff_delay(1)
        assert delay == 1.0  # 0.5 * 2^1 = 1.0

    def test_get_backoff_delay_third_attempt(self):
        """Test backoff delay for third attempt."""
        config = RetryConfig(backoff_factor=0.5)
        delay = config.get_backoff_delay(2)
        assert delay == 2.0  # 0.5 * 2^2 = 2.0

    def test_get_backoff_delay_max_backoff(self):
        """Test backoff delay respects max_backoff."""
        config = RetryConfig(backoff_factor=1.0, max_backoff=5.0)
        # 1.0 * 2^10 = 1024, but should be capped at 5.0
        delay = config.get_backoff_delay(10)
        assert delay == 5.0

    def test_get_backoff_delay_different_factors(self):
        """Test backoff delay with different factors."""
        config = RetryConfig(backoff_factor=2.0)
        assert config.get_backoff_delay(0) == 2.0  # 2.0 * 2^0
        assert config.get_backoff_delay(1) == 4.0  # 2.0 * 2^1
        assert config.get_backoff_delay(2) == 8.0  # 2.0 * 2^2

    def test_get_backoff_delay_zero_attempt(self):
        """Test backoff delay for zero attempt."""
        config = RetryConfig(backoff_factor=1.0)
        delay = config.get_backoff_delay(0)
        assert delay == 1.0
