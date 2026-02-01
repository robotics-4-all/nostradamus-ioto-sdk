"""Project Keys resource for the Nostradamus IoTO SDK."""

from typing import TYPE_CHECKING, List, Union
from uuid import UUID

from ..models import BaseKeyModel, ProjectKeyCreateRequest, ProjectKeyResponse
from ..models.enums import KeyType
from ._base import BaseResource

if TYPE_CHECKING:
    pass


class ProjectKeysResource(BaseResource):
    """Project API key management operations.

    Provides methods to create, list, get, regenerate, and delete project API keys.
    """

    def create(
        self,
        project_id: Union[str, UUID],
        key_type: KeyType,
    ) -> ProjectKeyResponse:
        """Create a new API key for a project.

        Args:
            project_id: Project UUID
            key_type: Type of key (read/write/master)

        Returns:
            ProjectKeyResponse: Created API key details

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If input is invalid
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> key = client.project_keys.create(
            ...     project_id="550e8400-e29b-41d4-a716-446655440000",
            ...     key_type=KeyType.READ
            ... )
            >>> print(key.api_key)
        """
        project_id_str = self._validate_uuid(project_id)
        request_data = ProjectKeyCreateRequest(key_type=key_type)
        response = self._client._request(
            "POST",
            self._build_path("projects", project_id_str, "keys"),
            json=request_data.model_dump(),
        )

        # Parse the response - could be the full object or just an ID
        response_data = response.json()

        # Check if the response is already a full ProjectKeyResponse
        if "api_key" in response_data or "key" in response_data:
            # API returned full object
            return self._parse_response(response_data, ProjectKeyResponse)

        # Otherwise, extract the ID and fetch full details
        # Try different possible field names
        key_id = (
            response_data.get("key_id")
            or response_data.get("id")
            or response_data.get("keyId")
        )

        # If no direct ID field, try to extract from message
        if not key_id and "message" in response_data:
            import re

            message = response_data["message"]
            # Match UUID pattern in message: "...with ID <uuid>"
            uuid_pattern = (
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            )
            match = re.search(uuid_pattern, message, re.IGNORECASE)
            if match:
                key_id = match.group(0)

        if not key_id:
            # If still no ID, raise error with response details
            from ..exceptions import APIError

            raise APIError(f"Create response missing key ID. Response: {response_data}")

        # Fetch full key details
        return self.get(project_id, key_id)

    async def acreate(
        self,
        project_id: Union[str, UUID],
        key_type: KeyType,
    ) -> ProjectKeyResponse:
        """Create a new API key for a project (async)."""
        project_id_str = self._validate_uuid(project_id)
        request_data = ProjectKeyCreateRequest(key_type=key_type)
        response = await self._client._request(
            "POST",
            self._build_path("projects", project_id_str, "keys"),
            json=request_data.model_dump(),
        )

        # Parse the response - could be the full object or just an ID
        response_data = response.json()

        # Check if the response is already a full ProjectKeyResponse
        if "api_key" in response_data or "key" in response_data:
            # API returned full object
            return self._parse_response(response_data, ProjectKeyResponse)

        # Otherwise, extract the ID and fetch full details
        # Try different possible field names
        key_id = (
            response_data.get("key_id")
            or response_data.get("id")
            or response_data.get("keyId")
        )

        # If no direct ID field, try to extract from message
        if not key_id and "message" in response_data:
            import re

            message = response_data["message"]
            # Match UUID pattern in message: "...with ID <uuid>"
            uuid_pattern = (
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            )
            match = re.search(uuid_pattern, message, re.IGNORECASE)
            if match:
                key_id = match.group(0)

        if not key_id:
            # If still no ID, raise error with response details
            from ..exceptions import APIError

            raise APIError(f"Create response missing key ID. Response: {response_data}")

        # Fetch full key details
        return await self.aget(project_id, key_id)

    def list(self, project_id: Union[str, UUID]) -> List[ProjectKeyResponse]:
        """List all API keys for a project.

        Args:
            project_id: Project UUID

        Returns:
            List[ProjectKeyResponse]: List of API keys

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If project not found
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> keys = client.project_keys.list("550e8400-e29b-41d4-a716-446655440000")
            >>> for key in keys:
            ...     print(f"{key.key_type}: {key.api_key}")
        """
        project_id_str = self._validate_uuid(project_id)
        response = self._client._request(
            "GET", self._build_path("projects", project_id_str, "keys")
        )
        return self._parse_response(response.json(), ProjectKeyResponse)

    async def alist(self, project_id: Union[str, UUID]) -> List[ProjectKeyResponse]:
        """List all API keys for a project (async)."""
        project_id_str = self._validate_uuid(project_id)
        response = await self._client._request(
            "GET", self._build_path("projects", project_id_str, "keys")
        )
        return self._parse_response(response.json(), ProjectKeyResponse)

    def get(
        self,
        project_id: Union[str, UUID],
        api_key: str,
    ) -> ProjectKeyResponse:
        """Get API key details.

        Args:
            project_id: Project UUID
            api_key: The API key to retrieve

        Returns:
            ProjectKeyResponse: API key details

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If key not found
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> key = client.project_keys.get(
            ...     project_id="550e8400-e29b-41d4-a716-446655440000",
            ...     api_key="your-api-key-here"
            ... )
        """
        project_id_str = self._validate_uuid(project_id)
        response = self._client._request(
            "GET", self._build_path("projects", project_id_str, "keys", api_key)
        )
        return self._parse_response(response.json(), ProjectKeyResponse)

    async def aget(
        self,
        project_id: Union[str, UUID],
        api_key: str,
    ) -> ProjectKeyResponse:
        """Get API key details (async)."""
        project_id_str = self._validate_uuid(project_id)
        response = await self._client._request(
            "GET", self._build_path("projects", project_id_str, "keys", api_key)
        )
        return self._parse_response(response.json(), ProjectKeyResponse)

    def regenerate(
        self,
        project_id: Union[str, UUID],
        api_key: str,
    ) -> BaseKeyModel:
        """Regenerate an API key.

        Args:
            project_id: Project UUID
            api_key: The API key to regenerate

        Returns:
            BaseKeyModel: New API key value

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If key not found
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> new_key = client.project_keys.regenerate(
            ...     project_id="550e8400-e29b-41d4-a716-446655440000",
            ...     api_key="old-key"
            ... )
            >>> print(f"New key: {new_key.key_value}")
        """
        project_id_str = self._validate_uuid(project_id)
        response = self._client._request(
            "PUT",
            self._build_path("projects", project_id_str, "keys", api_key, "regenerate"),
        )
        return self._parse_response(response.json(), BaseKeyModel)

    async def aregenerate(
        self,
        project_id: Union[str, UUID],
        api_key: str,
    ) -> BaseKeyModel:
        """Regenerate an API key (async)."""
        project_id_str = self._validate_uuid(project_id)
        response = await self._client._request(
            "PUT",
            self._build_path("projects", project_id_str, "keys", api_key, "regenerate"),
        )
        return self._parse_response(response.json(), BaseKeyModel)

    def delete(
        self,
        project_id: Union[str, UUID],
        api_key: str,
    ) -> None:
        """Delete an API key.

        Args:
            project_id: Project UUID
            api_key: The API key to delete

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If key not found
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> client.project_keys.delete(
            ...     project_id="550e8400-e29b-41d4-a716-446655440000",
            ...     api_key="key-to-delete"
            ... )
        """
        project_id_str = self._validate_uuid(project_id)
        self._client._request(
            "DELETE", self._build_path("projects", project_id_str, "keys", api_key)
        )

    async def adelete(
        self,
        project_id: Union[str, UUID],
        api_key: str,
    ) -> None:
        """Delete an API key (async)."""
        project_id_str = self._validate_uuid(project_id)
        await self._client._request(
            "DELETE", self._build_path("projects", project_id_str, "keys", api_key)
        )
