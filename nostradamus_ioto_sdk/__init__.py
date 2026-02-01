"""Nostradamus IoTO Python SDK.

Professional Python SDK for the Nostradamus IoT Observatory API.
"""

from .client import NostradamusClient
from .async_client import AsyncNostradamusClient
from .config import ClientConfig
from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    NostradamusError,
    RateLimitError,
    ResourceNotFoundError,
    TimeoutError,
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
    "TimeoutError",
    "ConnectionError",
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
