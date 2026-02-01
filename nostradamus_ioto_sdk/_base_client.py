"""Base client functionality for Nostradamus IoTO SDK."""

import time
from typing import Any, Optional

import httpx

from ._http import should_retry
from .config import RetryConfig
from .exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    RateLimitError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)


def handle_response(response: httpx.Response) -> httpx.Response:
    """Handle HTTP response and raise appropriate exceptions.

    Args:
        response: HTTP response object

    Returns:
        Response if successful

    Raises:
        AuthenticationError: For 401/403 errors
        ResourceNotFoundError: For 404 errors
        ValidationError: For 422 errors
        RateLimitError: For 429 errors
        APIError: For other error responses
    """
    if response.status_code < 400:
        return response

    # Handle specific status codes
    if response.status_code in (401, 403):
        raise AuthenticationError(
            f"Authentication failed: {response.text}",
            status_code=response.status_code,
            response=response,
        )

    if response.status_code == 404:
        raise ResourceNotFoundError(
            f"Resource not found: {response.text}", response=response
        )

    if response.status_code == 422:
        try:
            error_data = response.json()
            errors = error_data.get("detail", [])
        except Exception:
            errors = []
        raise ValidationError(
            f"Validation error: {response.text}", errors=errors, response=response
        )

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        retry_after_int = int(retry_after) if retry_after else None
        raise RateLimitError(
            "Rate limit exceeded", retry_after=retry_after_int, response=response
        )

    # Generic API error
    raise APIError(
        f"API error: {response.text}",
        status_code=response.status_code,
        response=response,
    )


def make_request_with_retry(
    client: httpx.Client,
    method: str,
    url: str,
    retry_config: RetryConfig,
    logger: Any,
    **kwargs: Any,
) -> httpx.Response:
    """Make HTTP request with retry logic.

    Args:
        client: HTTP client
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
    last_exception: Optional[Exception] = None

    for attempt in range(retry_config.max_retries + 1):
        try:
            logger.log_request(method, url, kwargs.get("headers"), kwargs.get("json"))
            start_time = time.time()

            response = client.request(method, url, **kwargs)

            duration = time.time() - start_time
            logger.log_response(response.status_code, None, duration)

            # Handle response (raises on error)
            return handle_response(response)

        except httpx.TimeoutException as err:
            last_exception = TimeoutError(f"Request timed out: {err}")
            if attempt < retry_config.max_retries:
                delay = retry_config.get_backoff_delay(attempt)
                logger.debug(f"Request timed out, retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise last_exception from err

        except httpx.RequestError as err:
            last_exception = ConnectionError(f"Connection error: {err}")
            if attempt < retry_config.max_retries:
                delay = retry_config.get_backoff_delay(attempt)
                logger.debug(f"Connection error, retrying in {delay}s...")
                time.sleep(delay)
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
                    time.sleep(delay)
                    last_exception = err
                else:
                    raise
            else:
                raise

    # Should not reach here, but just in case
    if last_exception:
        raise last_exception
    raise APIError("Max retries exceeded")
