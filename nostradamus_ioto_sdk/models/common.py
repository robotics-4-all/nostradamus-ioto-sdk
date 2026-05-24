"""Common response models for the Nostradamus IoTO SDK."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from nostradamus_ioto_sdk.models._base import BaseModel


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    offset: int
    limit: int


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


class DataListResponse(BaseModel):
    """Response model for data list queries."""

    data: list[dict[str, Any]]
    total_count: int


class DeleteDataResponse(BaseModel):
    """Response model for data deletion."""

    message: str
    criteria: dict[str, Any]


class KeyStatisticsResponse(BaseModel):
    """Response model for collection key statistics."""

    key: str
    collection_name: str
    total_records: int
    first_timestamp: datetime
    last_timestamp: datetime
    daily_breakdown: dict[str, int]


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str


class ReadyResponse(BaseModel):
    """Response model for readiness check."""

    status: str
    checks: dict[str, Any]
