"""Unit tests for authentication handlers."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import httpx

from nostradamus_ioto_sdk.auth import Token, APIKeyHandler, OAuth2Handler
from nostradamus_ioto_sdk.exceptions import AuthenticationError


class TestToken:
    """Test Token model."""

    def test_token_creation(self):
        """Test Token creation."""
        token = Token(
            access_token="test-token",
            token_type="bearer",
            expires_in=3600,
        )
        assert token.access_token == "test-token"
        assert token.token_type == "bearer"
        assert token.expires_in == 3600

    def test_token_is_expired_when_fresh(self):
        """Test token is not expired when fresh."""
        token = Token(
            access_token="test-token",
            token_type="bearer",
            expires_in=3600,
        )
        assert not token.is_expired()

    def test_token_expiration_property(self):
        """Test token expiration property calculation."""
        token = Token(
            access_token="test-token",
            token_type="bearer",
            expires_in=3600,
        )
        # Token should have an expires_at property
        assert token.expires_at is not None
        # Should be approximately 1 hour from now
        time_diff = (token.expires_at - datetime.now()).total_seconds()
        assert 3590 < time_diff < 3610  # Allow 10 second variance

    def test_token_without_expiration(self):
        """Test token without expiration never expires."""
        token = Token(
            access_token="test-token",
            token_type="bearer",
        )
        assert not token.is_expired()
        assert token.expires_at is None


class TestAPIKeyHandler:
    """Test API key authentication handler."""

    def test_api_key_handler_creation(self):
        """Test APIKeyHandler creation."""
        handler = APIKeyHandler("test-api-key")
        assert handler._api_key == "test-api-key"

    def test_api_key_handler_get_headers(self):
        """Test APIKeyHandler returns correct headers."""
        handler = APIKeyHandler("test-api-key")
        headers = handler.get_headers()
        assert headers == {"X-API-Key": "test-api-key"}

    def test_api_key_handler_empty_key(self):
        """Test APIKeyHandler with empty key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            APIKeyHandler("")


class TestOAuth2Handler:
    """Test OAuth2 authentication handler."""

    def test_oauth2_handler_creation(self):
        """Test OAuth2Handler creation."""
        handler = OAuth2Handler(
            base_url="https://api.example.com",
            username="testuser",
            password="testpass",
        )
        assert handler._base_url == "https://api.example.com"
        assert handler._username == "testuser"
        assert handler._password == "testpass"

    @patch("httpx.post")
    def test_oauth2_handler_get_headers_success(self, mock_post):
        """Test OAuth2 handler get_headers triggers authentication."""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-token",
            "token_type": "bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        handler = OAuth2Handler(
            base_url="https://api.example.com",
            username="testuser",
            password="testpass",
        )

        # Getting headers should trigger authentication
        headers = handler.get_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer new-token"

        # Verify API was called
        mock_post.assert_called_once()

    @patch("httpx.post")
    def test_oauth2_handler_authentication_failure(self, mock_post):
        """Test OAuth2 authentication failure."""
        # Mock failed authentication response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid credentials"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401", request=Mock(), response=mock_response
        )
        mock_post.return_value = mock_response

        handler = OAuth2Handler(
            base_url="https://api.example.com",
            username="testuser",
            password="wrongpass",
        )

        with pytest.raises(AuthenticationError) as exc_info:
            handler.get_headers()

        assert "Authentication failed" in str(exc_info.value)

    @patch("httpx.post")
    def test_oauth2_handler_get_headers_authenticates_if_needed(self, mock_post):
        """Test get_headers authenticates if no token."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-token",
            "token_type": "bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        handler = OAuth2Handler(
            base_url="https://api.example.com",
            username="testuser",
            password="testpass",
        )

        headers = handler.get_headers()

        # Should have authenticated and returned headers
        assert headers == {"Authorization": "Bearer new-token"}
        mock_post.assert_called_once()

    @patch("httpx.post")
    def test_oauth2_handler_thread_safety(self, mock_post):
        """Test OAuth2Handler is thread-safe."""
        import threading

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "thread-token",
            "token_type": "bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        handler = OAuth2Handler(
            base_url="https://api.example.com",
            username="testuser",
            password="testpass",
        )

        results = []

        def get_headers_thread():
            headers = handler.get_headers()
            results.append(headers)

        # Create multiple threads
        threads = [threading.Thread(target=get_headers_thread) for _ in range(10)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # All results should have the same token
        assert len(results) == 10
        assert all(r == results[0] for r in results)

    @patch("httpx.post")
    def test_oauth2_handler_connection_error(self, mock_post):
        """Test OAuth2 handler handles connection errors."""
        mock_post.side_effect = httpx.ConnectError("Connection failed")

        handler = OAuth2Handler(
            base_url="https://api.example.com",
            username="testuser",
            password="testpass",
        )

        with pytest.raises(AuthenticationError) as exc_info:
            handler.get_headers()

        assert "Connection failed" in str(
            exc_info.value
        ) or "Authentication failed" in str(exc_info.value)

    @patch("httpx.post")
    def test_oauth2_handler_timeout_error(self, mock_post):
        """Test OAuth2 handler handles timeout errors."""
        mock_post.side_effect = httpx.TimeoutException("Request timed out")

        handler = OAuth2Handler(
            base_url="https://api.example.com",
            username="testuser",
            password="testpass",
        )

        with pytest.raises(AuthenticationError) as exc_info:
            handler.get_headers()

        assert "timed out" in str(
            exc_info.value
        ).lower() or "Authentication failed" in str(exc_info.value)

    def test_oauth2_handler_strips_trailing_slash_from_url(self):
        """Test OAuth2Handler strips trailing slash from base URL."""
        handler = OAuth2Handler(
            base_url="https://api.example.com/",
            username="testuser",
            password="testpass",
        )
        assert handler._base_url == "https://api.example.com"
