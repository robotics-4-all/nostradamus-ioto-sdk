"""Collections resource for the Nostradamus IoTO SDK."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID

from ..models import (
    CollectionCreateRequest,
    CollectionResponse,
    CollectionUpdateRequest,
)
from ._base import BaseResource

if TYPE_CHECKING:
    pass


class CollectionsResource(BaseResource):
    """Collection management operations."""

    def list(self, project_id: Union[str, UUID]) -> List[CollectionResponse]:
        """List all collections in a project."""
        project_id_str = self._validate_uuid(project_id)
        response = self._client._request(
            "GET", self._build_path("projects", project_id_str, "collections")
        )
        return self._parse_response(response.json(), CollectionResponse)

    async def alist(self, project_id: Union[str, UUID]) -> List[CollectionResponse]:
        """List all collections in a project (async)."""
        project_id_str = self._validate_uuid(project_id)
        response = await self._client._request(
            "GET", self._build_path("projects", project_id_str, "collections")
        )
        return self._parse_response(response.json(), CollectionResponse)

    def get(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
    ) -> CollectionResponse:
        """Get collection by ID."""
        project_id_str = self._validate_uuid(project_id)
        collection_id_str = self._validate_uuid(collection_id)
        response = self._client._request(
            "GET",
            self._build_path(
                "projects", project_id_str, "collections", collection_id_str
            ),
        )
        return self._parse_response(response.json(), CollectionResponse)

    async def aget(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
    ) -> CollectionResponse:
        """Get collection by ID (async)."""
        project_id_str = self._validate_uuid(project_id)
        collection_id_str = self._validate_uuid(collection_id)
        response = await self._client._request(
            "GET",
            self._build_path(
                "projects", project_id_str, "collections", collection_id_str
            ),
        )
        return self._parse_response(response.json(), CollectionResponse)

    def create(
        self,
        project_id: Union[str, UUID],
        name: str,
        description: str,
        collection_schema: Dict[str, Any],
        tags: Optional[List[str]] = None,
    ) -> CollectionResponse:
        """Create a new collection."""
        project_id_str = self._validate_uuid(project_id)
        request_data = CollectionCreateRequest(
            name=name,
            description=description,
            tags=tags or [],
            collection_schema=collection_schema,
        )
        response = self._client._request(
            "POST",
            self._build_path("projects", project_id_str, "collections"),
            json=request_data.model_dump(),
        )

        # Parse the response - could be the full object or just an ID
        response_data = response.json()

        # Check if the response is already a full CollectionResponse
        if "collection_name" in response_data:
            # API returned full object
            return self._parse_response(response_data, CollectionResponse)

        # Otherwise, extract the ID and fetch full details
        # Try different possible field names
        collection_id = (
            response_data.get("collection_id")
            or response_data.get("id")
            or response_data.get("collectionId")
        )

        # If no direct ID field, try to extract from message
        if not collection_id and "message" in response_data:
            import re

            message = response_data["message"]
            # Match UUID pattern in message: "...with ID <uuid>"
            uuid_pattern = (
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            )
            match = re.search(uuid_pattern, message, re.IGNORECASE)
            if match:
                collection_id = match.group(0)

        if not collection_id:
            # If still no ID, raise error with response details
            from ..exceptions import APIError

            raise APIError(
                f"Create response missing collection ID. Response: {response_data}"
            )

        # Fetch full collection details
        return self.get(project_id, collection_id)

    async def acreate(
        self,
        project_id: Union[str, UUID],
        name: str,
        description: str,
        collection_schema: Dict[str, Any],
        tags: Optional[List[str]] = None,
    ) -> CollectionResponse:
        """Create a new collection (async)."""
        project_id_str = self._validate_uuid(project_id)
        request_data = CollectionCreateRequest(
            name=name,
            description=description,
            tags=tags or [],
            collection_schema=collection_schema,
        )
        response = await self._client._request(
            "POST",
            self._build_path("projects", project_id_str, "collections"),
            json=request_data.model_dump(),
        )

        # Parse the response - could be the full object or just an ID
        response_data = response.json()

        # Check if the response is already a full CollectionResponse
        if "collection_name" in response_data:
            # API returned full object
            return self._parse_response(response_data, CollectionResponse)

        # Otherwise, extract the ID and fetch full details
        # Try different possible field names
        collection_id = (
            response_data.get("collection_id")
            or response_data.get("id")
            or response_data.get("collectionId")
        )

        # If no direct ID field, try to extract from message
        if not collection_id and "message" in response_data:
            import re

            message = response_data["message"]
            # Match UUID pattern in message: "...with ID <uuid>"
            uuid_pattern = (
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            )
            match = re.search(uuid_pattern, message, re.IGNORECASE)
            if match:
                collection_id = match.group(0)

        if not collection_id:
            # If still no ID, raise error with response details
            from ..exceptions import APIError

            raise APIError(
                f"Create response missing collection ID. Response: {response_data}"
            )

        # Fetch full collection details
        return await self.aget(project_id, collection_id)

    def update(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> CollectionResponse:
        """Update collection."""
        project_id_str = self._validate_uuid(project_id)
        collection_id_str = self._validate_uuid(collection_id)
        request_data = CollectionUpdateRequest(description=description, tags=tags)
        response = self._client._request(
            "PUT",
            self._build_path(
                "projects", project_id_str, "collections", collection_id_str
            ),
            json=request_data.model_dump(exclude_none=True),
        )
        return self._parse_response(response.json(), CollectionResponse)

    async def aupdate(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> CollectionResponse:
        """Update collection (async)."""
        project_id_str = self._validate_uuid(project_id)
        collection_id_str = self._validate_uuid(collection_id)
        request_data = CollectionUpdateRequest(description=description, tags=tags)
        response = await self._client._request(
            "PUT",
            self._build_path(
                "projects", project_id_str, "collections", collection_id_str
            ),
            json=request_data.model_dump(exclude_none=True),
        )
        return self._parse_response(response.json(), CollectionResponse)

    def delete(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
    ) -> None:
        """Delete collection."""
        project_id_str = self._validate_uuid(project_id)
        collection_id_str = self._validate_uuid(collection_id)
        self._client._request(
            "DELETE",
            self._build_path(
                "projects", project_id_str, "collections", collection_id_str
            ),
        )

    async def adelete(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
    ) -> None:
        """Delete collection (async)."""
        project_id_str = self._validate_uuid(project_id)
        collection_id_str = self._validate_uuid(collection_id)
        await self._client._request(
            "DELETE",
            self._build_path(
                "projects", project_id_str, "collections", collection_id_str
            ),
        )
