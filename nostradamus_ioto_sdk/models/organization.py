"""Organization models for the Nostradamus IoTO SDK."""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from ._base import BaseModel


class OrganizationResponse(BaseModel):
    """Organization information response.

    Attributes:
        organization_id: Unique organization identifier
        organization_name: Name of the organization
        description: Organization description
        creation_date: When the organization was created
        tags: List of tags associated with the organization
    """

    organization_id: UUID = Field(..., description="Organization UUID")
    organization_name: str = Field(..., description="Organization name")
    description: str = Field(..., description="Organization description")
    creation_date: datetime = Field(..., description="Creation timestamp")
    tags: list[str] | None = Field(default=None, description="Organization tags")


class OrganizationUpdateRequest(BaseModel):
    """Request to update organization information.

    Attributes:
        description: New description for the organization
        tags: New tags for the organization
    """

    description: str | None = Field(default=None, description="New description")
    tags: list[str] | None = Field(default=None, description="New tags")
