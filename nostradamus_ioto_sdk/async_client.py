"""Asynchronous client for Nostradamus IoTO SDK."""

import asyncio
from typing import Any, Optional

import httpx

from ._http import RateLimiter
from ._logging import get_logger
from .auth import APIKeyHandler, OAuth2Handler
from .config import RetryConfig
from .exceptions import APIError, ConfigurationError
from .resources.collections import CollectionsResource
from .resources.data import DataResource
from .resources.organizations import OrganizationsResource
from .resources.project_keys import ProjectKeysResource
from .resources.projects import ProjectsResource


async def make_async_request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    retry_config: RetryConfig,
    logger: Any,
    **kwargs: Any,
) -> httpx.Response:
    """Make async HTTP request with retry logic.

    Args:
        client: Async HTTP client
        method: HTTP method
        url: Request URL
        retry_config: Retry configuration
        logger: Logger instance
        **kwargs: Additional request arguments

    Returns:
        HTTP response

    Raises:
        Various exceptions based on response
    """
    from ._base_client import handle_response
    from ._http import should_retry
    from .exceptions import (
        AuthenticationError,
        ConnectionError,
        RateLimitError,
        TimeoutError,
        ValidationError,
    )

    last_exception: Optional[Exception] = None

    for attempt in range(retry_config.max_retries + 1):
        try:
            logger.log_request(method, url, kwargs.get("headers"), kwargs.get("json"))
            import time

            start_time = time.time()

            response = await client.request(method, url, **kwargs)

            duration = time.time() - start_time
            logger.log_response(response.status_code, None, duration)

            # Handle response (raises on error)
            return handle_response(response)

        except httpx.TimeoutException as err:
            last_exception = TimeoutError(f"Request timed out: {err}")
            if attempt < retry_config.max_retries:
                delay = retry_config.get_backoff_delay(attempt)
                logger.debug(f"Request timed out, retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                raise last_exception from err

        except httpx.RequestError as err:
            last_exception = ConnectionError(f"Connection error: {err}")
            if attempt < retry_config.max_retries:
                delay = retry_config.get_backoff_delay(attempt)
                logger.debug(f"Connection error, retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                raise last_exception from err

        except (RateLimitError, AuthenticationError, ValidationError):
            # Don't retry these
            raise

        except APIError as err:
            if err.status_code and should_retry(err.status_code, retry_config):
                if attempt < retry_config.max_retries:
                    delay = retry_config.get_backoff_delay(attempt)
                    logger.debug(
                        f"Retryable error {err.status_code}, retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    last_exception = err
                else:
                    raise
            else:
                raise

    # Should not reach here, but just in case
    if last_exception:
        raise last_exception
    raise APIError("Max retries exceeded")


class AsyncNostradamusClient:
    """Asynchronous client for Nostradamus IoTO API.

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
        >>> async with AsyncNostradamusClient(api_key="your-api-key") as client:
        ...     projects = await client.projects.alist()

        >>> # With OAuth2
        >>> client = AsyncNostradamusClient(username="user", password="pass")
        >>> org = await client.organizations.aget()
        >>> await client.close()

        >>> # Manual lifecycle
        >>> client = AsyncNostradamusClient(api_key="key")
        >>> try:
        ...     data = await client.data.aget(project_id, collection_id)
        >>> finally:
        ...     await client.close()
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

        # Setup rate limiter (disabled by default)
        self._rate_limiter: Optional[RateLimiter] = None
        if rate_limit_rps > 0:
            self._rate_limiter = RateLimiter(requests_per_second=int(rate_limit_rps))

        # Setup authentication
        if api_key:
            self._auth_handler = APIKeyHandler(api_key)
        else:
            self._auth_handler = OAuth2Handler(
                base_url=self._base_url,
                username=username,  # type: ignore
                password=password,  # type: ignore
            )

        # Create async HTTP client (no base_url - we'll build full URLs)
        self._http_client = httpx.AsyncClient(timeout=timeout, **kwargs)

        # Initialize resource clients (they use the same resource classes)
        self.organizations = OrganizationsResource(self)
        self.projects = ProjectsResource(self)
        self.project_keys = ProjectKeysResource(self)
        self.collections = CollectionsResource(self)
        self.data = DataResource(self)

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make async HTTP request with authentication and retry logic.

        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional request arguments

        Returns:
            HTTP response
        """
        # Acquire rate limit permit if enabled
        if self._rate_limiter:
            await self._rate_limiter.aacquire()

        # Add authentication headers
        headers = kwargs.pop("headers", {})
        auth_headers = self._auth_handler.get_headers()
        headers.update(auth_headers)
        kwargs["headers"] = headers

        # Build full URL
        url = f"{self._base_url}{path}"

        # Make request with retry
        return await make_async_request_with_retry(
            client=self._http_client,
            method=method,
            url=url,
            retry_config=self._retry_config,
            logger=self._logger,
            **kwargs,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http_client.aclose()

    async def __aenter__(self) -> "AsyncNostradamusClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        await self.close()
