"""Unit tests for custom exceptions."""

from unittest.mock import Mock

import httpx

from nostradamus_ioto_sdk.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    ConfigurationError,
    NostradamusError,
    RateLimitError,
    RequestTimeoutError,
    ResourceNotFoundError,
    ValidationError,
)


class TestNostradamusError:
    """Test base exception class."""

    def test_base_exception_creation(self):
        """Test creating base exception."""
        error = NostradamusError("Test error")
        assert error.message == "Test error"
        assert str(error) == "Test error"

    def test_base_exception_inheritance(self):
        """Test that base exception inherits from Exception."""
        error = NostradamusError("Test")
        assert isinstance(error, Exception)


class TestConfigurationError:
    """Test configuration error."""

    def test_configuration_error_creation(self):
        """Test creating configuration error."""
        error = ConfigurationError("Invalid config")
        assert error.message == "Invalid config"
        assert str(error) == "Invalid config"

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inherits from NostradamusError."""
        error = ConfigurationError("Test")
        assert isinstance(error, NostradamusError)
        assert isinstance(error, Exception)


class TestAuthenticationError:
    """Test authentication error."""

    def test_authentication_error_basic(self):
        """Test basic authentication error."""
        error = AuthenticationError("Auth failed")
        assert error.message == "Auth failed"
        assert error.status_code is None
        assert error.response is None

    def test_authentication_error_with_status_code(self):
        """Test authentication error with status code."""
        error = AuthenticationError("Auth failed", status_code=401)
        assert error.status_code == 401
        assert str(error) == "Auth failed"

    def test_authentication_error_with_response(self):
        """Test authentication error with response object."""
        mock_response = Mock(spec=httpx.Response)
        error = AuthenticationError("Auth failed", response=mock_response)
        assert error.response == mock_response


class TestAPIError:
    """Test API error."""

    def test_api_error_basic(self):
        """Test basic API error."""
        error = APIError("API failed")
        assert error.message == "API failed"
        assert str(error) == "API failed"

    def test_api_error_with_status_code(self):
        """Test API error with status code."""
        error = APIError("API failed", status_code=500)
        assert error.status_code == 500
        assert str(error) == "[500] API failed"

    def test_api_error_with_response(self):
        """Test API error with response."""
        mock_response = Mock(spec=httpx.Response)
        error = APIError("API failed", response=mock_response)
        assert error.response == mock_response

    def test_api_error_with_request(self):
        """Test API error with request."""
        mock_request = Mock(spec=httpx.Request)
        error = APIError("API failed", request=mock_request)
        assert error.request == mock_request

    def test_api_error_str_without_status(self):
        """Test string representation without status code."""
        error = APIError("Test message")
        assert str(error) == "Test message"

    def test_api_error_str_with_status(self):
        """Test string representation with status code."""
        error = APIError("Test message", status_code=400)
        assert str(error) == "[400] Test message"


class TestValidationError:
    """Test validation error."""

    def test_validation_error_basic(self):
        """Test basic validation error."""
        error = ValidationError("Validation failed")
        assert error.message == "Validation failed"
        assert error.status_code == 422
        assert error.errors == []

    def test_validation_error_with_dict_errors(self):
        """Test validation error with dict errors."""
        errors = [
            {"loc": ["body", "name"], "msg": "field required"},
            {"loc": ["body", "email"], "msg": "invalid email"},
        ]
        error = ValidationError("Validation failed", errors=errors)
        assert error.errors == errors
        error_str = str(error)
        assert "[422] Validation failed" in error_str
        assert "body -> name: field required" in error_str
        assert "body -> email: invalid email" in error_str

    def test_validation_error_with_string_errors(self):
        """Test validation error with string errors."""
        errors = ["Error 1", "Error 2"]
        error = ValidationError("Validation failed", errors=errors)
        error_str = str(error)
        assert "Error 1" in error_str
        assert "Error 2" in error_str

    def test_validation_error_with_empty_loc(self):
        """Test validation error with empty location."""
        errors = [{"loc": [], "msg": "general error"}]
        error = ValidationError("Validation failed", errors=errors)
        error_str = str(error)
        assert ": general error" in error_str

    def test_validation_error_str_without_errors(self):
        """Test string representation without errors."""
        error = ValidationError("Validation failed")
        assert str(error) == "[422] Validation failed"

    def test_validation_error_with_response(self):
        """Test validation error with response."""
        mock_response = Mock(spec=httpx.Response)
        error = ValidationError("Validation failed", response=mock_response)
        assert error.response == mock_response


class TestResourceNotFoundError:
    """Test resource not found error."""

    def test_resource_not_found_default(self):
        """Test default resource not found error."""
        error = ResourceNotFoundError()
        assert error.message == "Resource not found"
        assert error.status_code == 404
        assert str(error) == "[404] Resource not found"

    def test_resource_not_found_custom_message(self):
        """Test custom message."""
        error = ResourceNotFoundError("Project not found")
        assert error.message == "Project not found"
        assert str(error) == "[404] Project not found"

    def test_resource_not_found_with_response(self):
        """Test with response."""
        mock_response = Mock(spec=httpx.Response)
        error = ResourceNotFoundError(response=mock_response)
        assert error.response == mock_response


class TestRateLimitError:
    """Test rate limit error."""

    def test_rate_limit_error_default(self):
        """Test default rate limit error."""
        error = RateLimitError()
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.retry_after is None

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry_after."""
        error = RateLimitError(retry_after=60)
        assert error.retry_after == 60
        assert str(error) == "[429] Rate limit exceeded (retry after 60s)"

    def test_rate_limit_error_without_retry_after(self):
        """Test string representation without retry_after."""
        error = RateLimitError()
        assert str(error) == "[429] Rate limit exceeded"

    def test_rate_limit_error_custom_message(self):
        """Test custom message."""
        error = RateLimitError("Too many requests", retry_after=30)
        assert str(error) == "[429] Too many requests (retry after 30s)"


class TestRequestTimeoutError:
    """Test timeout error."""

    def test_timeout_error_default(self):
        """Test default timeout error."""
        error = RequestTimeoutError()
        assert error.message == "Request timed out"
        assert error.timeout is None

    def test_timeout_error_with_timeout_value(self):
        """Test timeout error with timeout value."""
        error = RequestTimeoutError(timeout=30.0)
        assert error.timeout == 30.0
        assert error.message == "Request timed out"

    def test_timeout_error_custom_message(self):
        """Test custom message."""
        error = RequestTimeoutError("Connection timed out after 60s", timeout=60.0)
        assert error.message == "Connection timed out after 60s"
        assert error.timeout == 60.0


class TestAPIConnectionError:
    """Test connection error."""

    def test_connection_error_creation(self):
        """Test creating connection error."""
        error = APIConnectionError("Failed to connect")
        assert error.message == "Failed to connect"
        assert isinstance(error, APIError)

    def test_connection_error_inheritance(self):
        """Test APIConnectionError inherits from APIError."""
        error = APIConnectionError("Test")
        assert isinstance(error, APIError)
        assert isinstance(error, NostradamusError)
