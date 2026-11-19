"""Data operation models for the Nostradamus IoTO SDK."""

from datetime import datetime

from pydantic import Field

from ._base import BaseModel


class DeleteDataRequest(BaseModel):
    """Request to delete data from a collection.

    Attributes:
        key: Specific key to delete (optional)
        timestamp_from: Start of timestamp range (optional)
        timestamp_to: End of timestamp range (optional)

    Note:
        At least one parameter must be provided.
        Can delete by key, timestamp range, or both.
    """

    key: str | None = Field(default=None, description="Specific data key to delete")
    timestamp_from: datetime | None = Field(
        default=None, description="Start of timestamp range (ISO 8601)"
    )
    timestamp_to: datetime | None = Field(
        default=None, description="End of timestamp range (ISO 8601)"
    )
