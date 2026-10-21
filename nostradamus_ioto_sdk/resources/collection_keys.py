"""Collection Keys resource for the Nostradamus IoTO SDK."""

from typing import TYPE_CHECKING, Union
from uuid import UUID

from ..models.common import KeyStatisticsResponse
from ._base import BaseResource

if TYPE_CHECKING:
    pass


class CollectionKeysResource(BaseResource):
    """Collection key statistics operations."""

    def get_statistics(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        key: str,
    ) -> KeyStatisticsResponse:
        """Get statistics for a specific key in a collection.

        Args:
            project_id: Project UUID
            collection_id: Collection UUID
            key: The data key to get statistics for

        Returns:
            KeyStatisticsResponse: Key statistics details

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If project, collection, or key not found
            APIError: If request fails
        """
        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)
        response = self.client.request(
            "GET",
            self.build_path(
                "projects",
                project_id_str,
                "collections",
                collection_id_str,
                "keys",
                key,
                "stats",
            ),
        )
        return self.parse_response(response.json(), KeyStatisticsResponse)

    async def aget_statistics(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        key: str,
    ) -> KeyStatisticsResponse:
        """Get statistics for a specific key in a collection (async)."""
        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)
        response = await self.client.request(
            "GET",
            self.build_path(
                "projects",
                project_id_str,
                "collections",
                collection_id_str,
                "keys",
                key,
                "stats",
            ),
        )
        return self.parse_response(response.json(), KeyStatisticsResponse)
