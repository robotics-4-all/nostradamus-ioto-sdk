"""Collection models for the Nostradamus IoTO SDK."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from ._base import BaseModel


class CollectionResponse(BaseModel):
    """Collection information response.

    Attributes:
        collection_name: Name of the collection
        collection_id: Unique collection identifier
        project_id: Parent project UUID
        project_name: Name of the parent project
        organization_id: Parent organization UUID
        organization_name: Name of the parent organization
        description: Collection description
        tags: List of tags associated with the collection
        creation_date: When the collection was created
        collection_schema: Schema definition for the collection data
    """

    collection_name: str = Field(..., description="Collection name")
    collection_id: UUID = Field(..., description="Collection UUID")
    project_id: UUID = Field(..., description="Parent project UUID")
    project_name: str = Field(..., description="Project name")
    organization_id: UUID = Field(..., description="Parent organization UUID")
    organization_name: str = Field(..., description="Organization name")
    description: str = Field(..., description="Collection description")
    tags: List[str] = Field(default_factory=list, description="Collection tags")
    creation_date: datetime = Field(..., description="Creation timestamp")
    collection_schema: Dict[str, Any] = Field(
        ..., description="Schema definition for collection data"
    )


class CollectionCreateRequest(BaseModel):
    """Request to create a new collection.

    Attributes:
        name: Name for the new collection
        description: Description of the collection
        tags: Tags to associate with the collection
        collection_schema: Schema definition for the collection data
    """

    name: str = Field(..., description="Collection name", min_length=1)
    description: str = Field(..., description="Collection description")
    tags: List[str] = Field(default_factory=list, description="Collection tags")
    collection_schema: Dict[str, Any] = Field(
        ..., description="Schema definition for collection data"
    )


class CollectionUpdateRequest(BaseModel):
    """Request to update collection information.

    Attributes:
        description: New description for the collection
        tags: New tags for the collection
    """

    description: Optional[str] = Field(default=None, description="New description")
    tags: Optional[List[str]] = Field(default=None, description="New tags")
