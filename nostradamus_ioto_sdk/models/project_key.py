"""Project key models for the Nostradamus IoTO SDK."""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from ._base import BaseModel
from .enums import KeyType


class ProjectKeyResponse(BaseModel):
    """Project API key information response.

    Attributes:
        api_key: The API key value
        project_id: Parent project UUID
        key_type: Type of the key (read/write/master)
        created_at: When the key was created
    """

    api_key: str = Field(..., description="API key value")
    project_id: UUID = Field(..., description="Parent project UUID")
    key_type: str = Field(..., description="Key type (read/write/master)")
    created_at: datetime = Field(..., description="Creation timestamp")


class ProjectKeyCreateRequest(BaseModel):
    """Request to create a new project API key.

    Attributes:
        key_type: Type of key to create (read/write/master)
    """

    key_type: KeyType = Field(
        ...,
        description=(
            "Type of key to create: read (read-only),"
            " write (write data), or master (full access)"
        ),
    )


class BaseKeyModel(BaseModel):
    """Base model for key value response.

    Attributes:
        key_value: The key value string
    """

    key_value: str = Field(..., description="Key value")
