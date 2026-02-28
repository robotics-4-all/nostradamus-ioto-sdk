"""Project models for the Nostradamus IoTO SDK."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from ._base import BaseModel


class ProjectResponse(BaseModel):
    """Project information response.

    Attributes:
        organization_id: Parent organization UUID
        project_id: Unique project identifier
        organization_name: Name of the parent organization
        project_name: Name of the project
        description: Project description
        tags: List of tags associated with the project
        creation_date: When the project was created
    """

    organization_id: UUID = Field(..., description="Parent organization UUID")
    project_id: UUID = Field(..., description="Project UUID")
    organization_name: str = Field(..., description="Organization name")
    project_name: str = Field(..., description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    tags: list[str] = Field(default_factory=list, description="Project tags")
    creation_date: datetime = Field(..., description="Creation timestamp")


class ProjectCreateRequest(BaseModel):
    """Request to create a new project.

    Attributes:
        project_name: Name for the new project
        description: Description of the project
        tags: Tags to associate with the project
    """

    project_name: str = Field(..., description="Project name", min_length=1)
    description: Optional[str] = Field(default=None, description="Project description")
    tags: list[str] = Field(default_factory=list, description="Project tags")


class ProjectUpdateRequest(BaseModel):
    """Request to update project information.

    Attributes:
        description: New description for the project
        tags: New tags for the project
    """

    description: Optional[str] = Field(default=None, description="New description")
    tags: Optional[list[str]] = Field(default=None, description="New tags")
