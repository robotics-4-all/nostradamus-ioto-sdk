"""Projects resource for the Nostradamus IoTO SDK."""

from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID

from ..models import ProjectCreateRequest, ProjectResponse, ProjectUpdateRequest
from ._base import BaseResource

if TYPE_CHECKING:
    pass


class ProjectsResource(BaseResource):
    """Project management operations.

    Provides full CRUD operations for projects.
    """

    def list(self) -> List[ProjectResponse]:
        """List all projects.

        Returns:
            List[ProjectResponse]: List of all projects

        Raises:
            AuthenticationError: If not authenticated
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> projects = client.projects.list()
            >>> for project in projects:
            ...     print(project.project_name)
        """
        response = self._client._request("GET", self._build_path("projects"))
        return self._parse_response(response.json(), ProjectResponse)

    async def alist(self) -> List[ProjectResponse]:
        """List all projects (async).

        Returns:
            List[ProjectResponse]: List of all projects
        """
        response = await self._client._request("GET", self._build_path("projects"))
        return self._parse_response(response.json(), ProjectResponse)

    def get(self, project_id: Union[str, UUID]) -> ProjectResponse:
        """Get project by ID.

        Args:
            project_id: Project UUID

        Returns:
            ProjectResponse: Project details

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If project not found
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> project = client.projects.get("550e8400-e29b-41d4-a716-446655440000")
            >>> print(project.project_name)
        """
        project_id_str = self._validate_uuid(project_id)
        response = self._client._request(
            "GET", self._build_path("projects", project_id_str)
        )
        return self._parse_response(response.json(), ProjectResponse)

    async def aget(self, project_id: Union[str, UUID]) -> ProjectResponse:
        """Get project by ID (async).

        Args:
            project_id: Project UUID

        Returns:
            ProjectResponse: Project details
        """
        project_id_str = self._validate_uuid(project_id)
        response = await self._client._request(
            "GET", self._build_path("projects", project_id_str)
        )
        return self._parse_response(response.json(), ProjectResponse)

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> ProjectResponse:
        """Create a new project.

        Args:
            name: Project name
            description: Project description
            tags: List of tags

        Returns:
            ProjectResponse: Created project details

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If input is invalid
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> project = client.projects.create(
            ...     name="My IoT Project",
            ...     description="Collecting sensor data",
            ...     tags=["sensors", "temperature"]
            ... )
            >>> print(project.project_id)
        """
        request_data = ProjectCreateRequest(
            project_name=name, description=description, tags=tags or []
        )
        response = self._client._request(
            "POST",
            self._build_path("projects"),
            json=request_data.model_dump(exclude_none=True),
        )

        # Parse the response - could be the full object or just an ID
        response_data = response.json()

        # Check if the response is already a full ProjectResponse
        if "project_name" in response_data:
            # API returned full object
            return self._parse_response(response_data, ProjectResponse)

        # Otherwise, extract the ID and fetch full details
        # Try different possible field names
        project_id = (
            response_data.get("project_id")
            or response_data.get("id")
            or response_data.get("projectId")
        )

        # If no direct ID field, try to extract from message
        if not project_id and "message" in response_data:
            import re

            message = response_data["message"]
            # Match UUID pattern in message: "...with ID <uuid>"
            uuid_pattern = (
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            )
            match = re.search(uuid_pattern, message, re.IGNORECASE)
            if match:
                project_id = match.group(0)

        if not project_id:
            # If still no ID, raise error with response details
            from ..exceptions import APIError

            raise APIError(
                f"Create response missing project ID. Response: {response_data}"
            )

        # Fetch full project details
        return self.get(project_id)

    async def acreate(
        self,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> ProjectResponse:
        """Create a new project (async).

        Args:
            name: Project name
            description: Project description
            tags: List of tags

        Returns:
            ProjectResponse: Created project details
        """
        request_data = ProjectCreateRequest(
            project_name=name, description=description, tags=tags or []
        )
        response = await self._client._request(
            "POST",
            self._build_path("projects"),
            json=request_data.model_dump(exclude_none=True),
        )

        # Parse the response - could be the full object or just an ID
        response_data = response.json()

        # Check if the response is already a full ProjectResponse
        if "project_name" in response_data:
            # API returned full object
            return self._parse_response(response_data, ProjectResponse)

        # Otherwise, extract the ID and fetch full details
        # Try different possible field names
        project_id = (
            response_data.get("project_id")
            or response_data.get("id")
            or response_data.get("projectId")
        )

        # If no direct ID field, try to extract from message
        if not project_id and "message" in response_data:
            import re

            message = response_data["message"]
            # Match UUID pattern in message: "...with ID <uuid>"
            uuid_pattern = (
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            )
            match = re.search(uuid_pattern, message, re.IGNORECASE)
            if match:
                project_id = match.group(0)

        if not project_id:
            # If still no ID, raise error with response details
            from ..exceptions import APIError

            raise APIError(
                f"Create response missing project ID. Response: {response_data}"
            )

        # Fetch full project details
        return await self.aget(project_id)

    def update(
        self,
        project_id: Union[str, UUID],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> ProjectResponse:
        """Update project.

        Args:
            project_id: Project UUID
            description: New description
            tags: New tags

        Returns:
            ProjectResponse: Updated project details

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If project not found
            ValidationError: If input is invalid
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> project = client.projects.update(
            ...     project_id="550e8400-e29b-41d4-a716-446655440000",
            ...     description="Updated description"
            ... )
        """
        project_id_str = self._validate_uuid(project_id)
        request_data = ProjectUpdateRequest(description=description, tags=tags)
        response = self._client._request(
            "PUT",
            self._build_path("projects", project_id_str),
            json=request_data.model_dump(exclude_none=True),
        )
        return self._parse_response(response.json(), ProjectResponse)

    async def aupdate(
        self,
        project_id: Union[str, UUID],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> ProjectResponse:
        """Update project (async).

        Args:
            project_id: Project UUID
            description: New description
            tags: New tags

        Returns:
            ProjectResponse: Updated project details
        """
        project_id_str = self._validate_uuid(project_id)
        request_data = ProjectUpdateRequest(description=description, tags=tags)
        response = await self._client._request(
            "PUT",
            self._build_path("projects", project_id_str),
            json=request_data.model_dump(exclude_none=True),
        )
        return self._parse_response(response.json(), ProjectResponse)

    def delete(self, project_id: Union[str, UUID]) -> None:
        """Delete project.

        Args:
            project_id: Project UUID

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If project not found
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> client.projects.delete("550e8400-e29b-41d4-a716-446655440000")
        """
        project_id_str = self._validate_uuid(project_id)
        self._client._request("DELETE", self._build_path("projects", project_id_str))

    async def adelete(self, project_id: Union[str, UUID]) -> None:
        """Delete project (async).

        Args:
            project_id: Project UUID
        """
        project_id_str = self._validate_uuid(project_id)
        await self._client._request(
            "DELETE", self._build_path("projects", project_id_str)
        )
