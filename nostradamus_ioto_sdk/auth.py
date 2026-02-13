"""Authentication handlers for the Nostradamus IoTO SDK."""

import threading
from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from .exceptions import AuthenticationError


class Token(BaseModel):
    """OAuth2 access token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None  # Seconds until expiration

    _created_at: Optional[datetime] = None

    def model_post_init(self, __context: object) -> None:
        """Initialize created_at timestamp."""
        self._created_at = datetime.now()

    @property
    def expires_at(self) -> Optional[datetime]:
        """Calculate expiration timestamp."""
        if self.expires_in and self._created_at:
            return self._created_at + timedelta(seconds=self.expires_in)
        return None

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Check if token is expired or will expire soon.

        Args:
            buffer_seconds: Seconds before expiration to consider token expired

        Returns:
            True if token is expired or will expire within buffer_seconds
        """
        if not self.expires_at:
            # If no expiration, assume token doesn't expire
            return False
        return datetime.now() >= (self.expires_at - timedelta(seconds=buffer_seconds))


class OAuth2Handler:
    """Handle OAuth2 password flow authentication.

    This handler manages OAuth2 tokens, including automatic refresh
    when tokens expire.

    Args:
        base_url: Base URL of the API
        username: Username for authentication
        password: Password for authentication
        token_url: Token endpoint path (default: /api/v1/token)

    Example:
        >>> handler = OAuth2Handler(
        ...     base_url="https://api.example.com",
        ...     username="user@example.com",
        ...     password="secret"
        ... )
        >>> headers = handler.get_headers()
        >>> # headers contains {"Authorization": "Bearer <token>"}
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        token_url: str = "/api/v1/token",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._token_url = token_url
        self._token: Optional[Token] = None
        self._lock = threading.Lock()

    def get_token(self) -> Token:
        """Get valid access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            AuthenticationError: If authentication fails
        """
        with self._lock:
            if self._token is None or self._token.is_expired():
                self._refresh_token()
            assert self._token is not None
            return self._token

    def _refresh_token(self) -> None:
        """Fetch a new access token from the API.

        Raises:
            AuthenticationError: If authentication fails
        """
        url = urljoin(self._base_url, self._token_url)
        data = {
            "grant_type": "password",
            "username": self._username,
            "password": self._password,
        }

        try:
            response = httpx.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            if err.response.status_code in (401, 403):
                raise AuthenticationError(
                    f"Authentication failed: {err.response.text}",
                    status_code=err.response.status_code,
                    response=err.response,
                ) from err
            raise AuthenticationError(
                f"Failed to obtain access token: {err}",
                status_code=err.response.status_code,
                response=err.response,
            ) from err
        except httpx.RequestError as err:
            raise AuthenticationError(
                f"Failed to connect to authentication server: {err}"
            ) from err

        try:
            token_data = response.json()
        except (ValueError, UnicodeDecodeError) as err:
            raise AuthenticationError(
                f"Failed to decode token response: {err}"
            ) from err

        try:
            self._token = Token(**token_data)
        except (TypeError, KeyError, PydanticValidationError) as err:
            raise AuthenticationError(f"Invalid token response format: {err}") from err

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary with Authorization header
        """
        token = self.get_token()
        return {
            "Authorization": f"{token.token_type.capitalize()} {token.access_token}"
        }

    def clear_token(self) -> None:
        """Clear the cached token, forcing refresh on next request."""
        with self._lock:
            self._token = None


class APIKeyHandler:
    """Handle API key authentication.

    Args:
        api_key: API key for authentication
        header_name: Name of the header to use (default: X-API-Key)

    Example:
        >>> handler = APIKeyHandler(api_key="my-secret-key")
        >>> headers = handler.get_headers()
        >>> # headers contains {"X-API-Key": "my-secret-key"}
    """

    def __init__(self, api_key: str, header_name: str = "X-API-Key") -> None:
        if not api_key:
            raise ValueError("API key cannot be empty")
        self._api_key = api_key
        self._header_name = header_name

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary with API key header
        """
        return {self._header_name: self._api_key}
