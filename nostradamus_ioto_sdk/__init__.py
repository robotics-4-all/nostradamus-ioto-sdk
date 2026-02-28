"""Nostradamus IoTO Python SDK.

Professional Python SDK for the Nostradamus IoT Observatory API.
"""

from .async_client import AsyncNostradamusClient
from .client import NostradamusClient
from .config import ClientConfig
from .exceptions import (
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
from .models import (
    BaseKeyModel,
    CollectionCreateRequest,
    CollectionResponse,
    CollectionUpdateRequest,
    DeleteDataRequest,
    HTTPValidationError,
    KeyType,
    OrganizationResponse,
    OrganizationUpdateRequest,
    ProjectCreateRequest,
    ProjectKeyCreateRequest,
    ProjectKeyResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    StatOperation,
)

__version__ = "0.1.0"

__all__ = [
    # Main clients
    "NostradamusClient",
    "AsyncNostradamusClient",
    # Configuration
    "ClientConfig",
    # Exceptions
    "NostradamusError",
    "ConfigurationError",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "ResourceNotFoundError",
    "RateLimitError",
    "RequestTimeoutError",
    "APIConnectionError",
    # Enums
    "KeyType",
    "StatOperation",
    # Models
    "OrganizationResponse",
    "OrganizationUpdateRequest",
    "ProjectResponse",
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
    "CollectionResponse",
    "CollectionCreateRequest",
    "CollectionUpdateRequest",
    "ProjectKeyResponse",
    "ProjectKeyCreateRequest",
    "BaseKeyModel",
    "DeleteDataRequest",
    "HTTPValidationError",
]
