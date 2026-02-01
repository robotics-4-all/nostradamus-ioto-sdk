"""Unit tests for NostradamusClient."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx

from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.config import ClientConfig
from nostradamus_ioto_sdk.exceptions import ConfigurationError
from nostradamus_ioto_sdk.auth import APIKeyHandler, OAuth2Handler


class TestNostradamusClientInitialization:
    """Test client initialization."""

    def test_client_init_with_api_key(self):
        """Test client initialization with API key."""
        client = NostradamusClient(api_key="test-key")
        assert isinstance(client._auth_handler, APIKeyHandler)
        assert client._auth_handler._api_key == "test-key"

    def test_client_init_without_credentials(self):
        """Test client initialization without credentials raises error."""
        with pytest.raises(ConfigurationError):
            NostradamusClient()

    def test_client_init_with_partial_oauth2(self):
        """Test client initialization with only username fails."""
        with pytest.raises(ConfigurationError):
            NostradamusClient(username="testuser")

    def test_client_init_with_only_password(self):
        """Test client initialization with only password fails."""
        with pytest.raises(ConfigurationError):
            NostradamusClient(password="testpass")

    def test_client_init_with_both_api_key_and_username(self):
        """Test client initialization with both API key and username/password fails."""
        with pytest.raises(
            ConfigurationError,
            match="Provide either api_key OR username/password, not both",
        ):
            NostradamusClient(
                api_key="test-key", username="testuser", password="testpass"
            )

    @patch("nostradamus_ioto_sdk.client.OAuth2Handler")
    def test_client_init_with_username_and_password(self, mock_oauth2):
        """Test client initialization with username and password."""
        # Mock OAuth2Handler
        mock_handler = Mock()
        mock_oauth2.return_value = mock_handler

        client = NostradamusClient(username="testuser", password="testpass")

        # Verify OAuth2Handler was created
        mock_oauth2.assert_called_once_with(
            base_url="https://nostradamus-ioto.issel.ee.auth.gr",
            username="testuser",
            password="testpass",
        )
        assert client._auth_handler is mock_handler

    def test_client_has_resources(self):
        """Test client has all resource managers."""
        client = NostradamusClient(api_key="test-key")
        assert hasattr(client, "organizations")
        assert hasattr(client, "projects")
        assert hasattr(client, "collections")
        assert hasattr(client, "project_keys")
        assert hasattr(client, "data")


class TestNostradamusClientContextManager:
    """Test client context manager."""

    def test_client_context_manager_enter(self):
        """Test client can be used as context manager."""
        with NostradamusClient(api_key="test-key") as client:
            assert isinstance(client, NostradamusClient)

    def test_client_context_manager_exit(self):
        """Test client closes properly on context exit."""
        client = NostradamusClient(api_key="test-key")
        with patch.object(client, "close") as mock_close:
            with client:
                pass
            mock_close.assert_called_once()

    def test_client_close(self):
        """Test client close method."""
        client = NostradamusClient(api_key="test-key")
        # Should not raise any errors
        client.close()


class TestNostradamusClientMethods:
    """Test client methods."""

    @patch("nostradamus_ioto_sdk.client.make_request_with_retry")
    def test_client_request_uses_auth_headers(self, mock_request):
        """Test that client requests include auth headers."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response

        client = NostradamusClient(api_key="test-key-123")

        # Make a request
        response = client._request("GET", "/test")

        # Verify request was made
        assert mock_request.called
        call_kwargs = mock_request.call_args[1]

        # Verify auth headers are included
        assert "headers" in call_kwargs
        assert "X-API-Key" in call_kwargs["headers"]
        assert call_kwargs["headers"]["X-API-Key"] == "test-key-123"

    @patch("nostradamus_ioto_sdk.client.make_request_with_retry")
    def test_client_request_with_json_body(self, mock_request):
        """Test client request with JSON body."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = NostradamusClient(api_key="test-key")
        test_data = {"key": "value"}
        client._request("POST", "/test", json=test_data)

        # Verify JSON was passed
        call_kwargs = mock_request.call_args[1]
        assert "json" in call_kwargs
        assert call_kwargs["json"] == test_data

    @patch("nostradamus_ioto_sdk.client.make_request_with_retry")
    def test_client_request_with_params(self, mock_request):
        """Test client request with query parameters."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = NostradamusClient(api_key="test-key")
        params = {"limit": 10, "offset": 0}
        client._request("GET", "/test", params=params)

        # Verify params were passed
        call_kwargs = mock_request.call_args[1]
        assert "params" in call_kwargs
        assert call_kwargs["params"] == params
