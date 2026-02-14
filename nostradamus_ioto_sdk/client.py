"""Synchronous client for Nostradamus IoTO SDK."""

from typing import Any, Optional

import httpx

from ._base_client import make_request_with_retry
from ._http import RateLimiter
from ._logging import get_logger
from .auth import APIKeyHandler, OAuth2Handler
from .config import RetryConfig
from .exceptions import ConfigurationError
from .resources.collections import CollectionsResource
from .resources.data import DataResource
from .resources.organizations import OrganizationsResource
from .resources.project_keys import ProjectKeysResource
from .resources.projects import ProjectsResource


class NostradamusClient:
    """Synchronous client for Nostradamus IoTO API.

    Args:
        api_key: API key for authentication (mutually exclusive with username/password)
        username: Username for OAuth2 authentication
        password: Password for OAuth2 authentication
        base_url: API base URL
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        log_level: Logging level
        **kwargs: Additional configuration options

    Examples:
        >>> # With API key
        >>> client = NostradamusClient(api_key="your-api-key")
        >>> projects = client.projects.list()

        >>> # With OAuth2
        >>> client = NostradamusClient(username="user", password="pass")
        >>> org = client.organizations.get()

        >>> # As context manager
        >>> with NostradamusClient(api_key="key") as client:
        ...     data = client.data.get(project_id, collection_id)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = "https://nostradamus-ioto.issel.ee.auth.gr",
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit_rps: float = 0.0,
        log_level: str = "INFO",
        **kwargs: Any,
    ) -> None:
        # Validate authentication parameters
        if api_key and (username or password):
            raise ConfigurationError(
                "Provide either api_key OR username/password, not both"
            )
        if not api_key and not (username and password):
            raise ConfigurationError("Must provide either api_key or username/password")

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retry_config = RetryConfig(max_retries=max_retries)
        self._logger = get_logger(__name__, log_level)

        # Setup authentication
        if api_key:
            self._auth_handler = APIKeyHandler(api_key)
        else:
            self._auth_handler = OAuth2Handler(
                base_url=self._base_url,
                username=username,  # type: ignore
                password=password,  # type: ignore
            )

        # Setup rate limiter (disabled by default)
        self._rate_limiter: Optional[RateLimiter] = None
        if rate_limit_rps > 0:
            self._rate_limiter = RateLimiter(requests_per_second=int(rate_limit_rps))

        # Create HTTP client (no base_url - we'll build full URLs)
        self._http_client = httpx.Client(timeout=timeout, **kwargs)

        # Initialize resource clients
        self.organizations = OrganizationsResource(self)
        self.projects = ProjectsResource(self)
        self.project_keys = ProjectKeysResource(self)
        self.collections = CollectionsResource(self)
        self.data = DataResource(self)

    @property
    def base_url(self) -> str:
        """The base URL for API requests."""
        return self._base_url

    @property
    def auth_handler(self) -> Any:
        """The authentication handler (OAuth2Handler or APIKeyHandler)."""
        return self._auth_handler

    @property
    def rate_limiter(self) -> Optional[RateLimiter]:
        """The rate limiter instance, or None if disabled."""
        return self._rate_limiter

    @property
    def http_client(self) -> httpx.Client:
        """The underlying HTTP client."""
        return self._http_client

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make HTTP request with authentication and retry logic.

        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional request arguments

        Returns:
            HTTP response
        """
        if self._rate_limiter:
            self._rate_limiter.acquire()

        headers = kwargs.pop("headers", {})
        auth_headers = self._auth_handler.get_headers()
        headers.update(auth_headers)
        kwargs["headers"] = headers

        url = f"{self._base_url}{path}"

        return make_request_with_retry(
            client=self._http_client,
            method=method,
            url=url,
            retry_config=self._retry_config,
            logger=self._logger,
            **kwargs,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._http_client.close()

    def __enter__(self) -> "NostradamusClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.close()
