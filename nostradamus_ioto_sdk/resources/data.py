"""Data resource for the Nostradamus IoTO SDK."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, Union
from uuid import UUID

from ..exceptions import ValidationError
from ..models.enums import StatOperation
from ._base import BaseResource

if TYPE_CHECKING:
    pass


class DataResource(BaseResource):
    """Data operations for collections."""

    def send(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        data: Union[dict[str, Any], list[dict[str, Any]]],
    ) -> None:
        """Send data to collection."""
        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)
        self.client.request(
            "POST",
            self.build_path(
                "projects",
                project_id_str,
                "collections",
                collection_id_str,
                "send_data",
            ),
            json=data,
        )

    async def asend(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        data: Union[dict[str, Any], list[dict[str, Any]]],
    ) -> None:
        """Send data to collection (async)."""
        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)
        await self.client.request(
            "POST",
            self.build_path(
                "projects",
                project_id_str,
                "collections",
                collection_id_str,
                "send_data",
            ),
            json=data,
        )

    def get(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        attributes: Optional[list[str]] = None,
        filters: Optional[list[dict[str, Any]]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        nested: bool = False,
    ) -> list[dict[str, Any]]:
        """Query data from collection."""
        import json

        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)

        params: dict[str, Any] = {}
        if attributes:
            params["attributes"] = attributes
        if filters:
            # Filters must be JSON-encoded as string
            params["filters"] = json.dumps(filters)
        if order_by:
            params["order_by"] = order_by
        if limit:
            params["limit"] = limit
        if nested:
            params["nested"] = nested

        response = self.client.request(
            "GET",
            self.build_path(
                "projects", project_id_str, "collections", collection_id_str, "get_data"
            ),
            params=params,
        )
        return response.json()

    async def aget(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        attributes: Optional[list[str]] = None,
        filters: Optional[list[dict[str, Any]]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        nested: bool = False,
    ) -> list[dict[str, Any]]:
        """Query data from collection (async)."""
        import json

        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)

        params: dict[str, Any] = {}
        if attributes:
            params["attributes"] = attributes
        if filters:
            # Filters must be JSON-encoded as string
            params["filters"] = json.dumps(filters)
        if order_by:
            params["order_by"] = order_by
        if limit:
            params["limit"] = limit
        if nested:
            params["nested"] = nested

        response = await self.client.request(
            "GET",
            self.build_path(
                "projects", project_id_str, "collections", collection_id_str, "get_data"
            ),
            params=params,
        )
        return response.json()

    def statistics(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        operation: Union[str, StatOperation],
        attribute: str,
        group_by: Optional[str] = None,
        interval: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        """Get statistics/aggregations."""
        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)

        params: dict[str, Any] = {
            "operation": operation if isinstance(operation, str) else operation.value,
            "attribute": attribute,
        }
        if group_by:
            params["group_by"] = group_by
        if interval:
            params["interval"] = interval
        if limit:
            params["limit"] = limit

        response = self.client.request(
            "GET",
            self.build_path(
                "projects",
                project_id_str,
                "collections",
                collection_id_str,
                "statistics",
            ),
            params=params,
        )
        return response.json()

    async def astatistics(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        operation: Union[str, StatOperation],
        attribute: str,
        group_by: Optional[str] = None,
        interval: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        """Get statistics/aggregations (async)."""
        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)

        params: dict[str, Any] = {
            "operation": operation if isinstance(operation, str) else operation.value,
            "attribute": attribute,
        }
        if group_by:
            params["group_by"] = group_by
        if interval:
            params["interval"] = interval
        if limit:
            params["limit"] = limit

        response = await self.client.request(
            "GET",
            self.build_path(
                "projects",
                project_id_str,
                "collections",
                collection_id_str,
                "statistics",
            ),
            params=params,
        )
        return response.json()

    def delete(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        key: Optional[str] = None,
        timestamp_from: Optional[Union[str, datetime]] = None,
        timestamp_to: Optional[Union[str, datetime]] = None,
    ) -> dict[str, Any]:
        """Delete data from collection based on criteria.

        Args:
            project_id: Project UUID
            collection_id: Collection UUID
            key: Specific data key to delete (optional)
            timestamp_from: Start of timestamp range in ISO 8601 format (optional)
            timestamp_to: End of timestamp range in ISO 8601 format (optional)

        Returns:
            Response containing deletion confirmation message

        Note:
            At least one parameter (key, timestamp_from, or timestamp_to) must be provided.
            Can delete by key, timestamp range, or both.
        """
        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)

        delete_request: dict[str, Any] = {}
        if key:
            delete_request["key"] = key
        if timestamp_from:
            delete_request["timestamp_from"] = (
                timestamp_from.isoformat()
                if isinstance(timestamp_from, datetime)
                else timestamp_from
            )
        if timestamp_to:
            delete_request["timestamp_to"] = (
                timestamp_to.isoformat()
                if isinstance(timestamp_to, datetime)
                else timestamp_to
            )

        if not delete_request:
            raise ValidationError(
                "At least one parameter (key, timestamp_from, or timestamp_to) must be provided"
            )

        response = self.client.request(
            "DELETE",
            self.build_path(
                "projects",
                project_id_str,
                "collections",
                collection_id_str,
                "delete_data",
            ),
            json=delete_request,
        )
        return response.json()

    async def adelete(
        self,
        project_id: Union[str, UUID],
        collection_id: Union[str, UUID],
        key: Optional[str] = None,
        timestamp_from: Optional[Union[str, datetime]] = None,
        timestamp_to: Optional[Union[str, datetime]] = None,
    ) -> dict[str, Any]:
        """Delete data from collection based on criteria (async).

        Args:
            project_id: Project UUID
            collection_id: Collection UUID
            key: Specific data key to delete (optional)
            timestamp_from: Start of timestamp range in ISO 8601 format (optional)
            timestamp_to: End of timestamp range in ISO 8601 format (optional)

        Returns:
            Response containing deletion confirmation message

        Note:
            At least one parameter (key, timestamp_from, or timestamp_to) must be provided.
            Can delete by key, timestamp range, or both.
        """
        project_id_str = self.validate_uuid(project_id)
        collection_id_str = self.validate_uuid(collection_id)

        delete_request: dict[str, Any] = {}
        if key:
            delete_request["key"] = key
        if timestamp_from:
            delete_request["timestamp_from"] = (
                timestamp_from.isoformat()
                if isinstance(timestamp_from, datetime)
                else timestamp_from
            )
        if timestamp_to:
            delete_request["timestamp_to"] = (
                timestamp_to.isoformat()
                if isinstance(timestamp_to, datetime)
                else timestamp_to
            )

        if not delete_request:
            raise ValidationError(
                "At least one parameter (key, timestamp_from, or timestamp_to) must be provided"
            )

        response = await self.client.request(
            "DELETE",
            self.build_path(
                "projects",
                project_id_str,
                "collections",
                collection_id_str,
                "delete_data",
            ),
            json=delete_request,
        )
        return response.json()
