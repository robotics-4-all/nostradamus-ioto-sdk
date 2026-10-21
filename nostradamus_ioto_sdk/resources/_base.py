"""Base resource class for the Nostradamus IoTO SDK."""

from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    overload,
)
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from ..async_client import AsyncNostradamusClient
    from ..client import NostradamusClient

T = TypeVar("T", bound=BaseModel)


class BaseResource:
    """Base class for all resource clients.

    Provides common functionality for making API requests and
    parsing responses.

    Args:
        client: The parent client instance
    """

    def __init__(
        self, client: Union["NostradamusClient", "AsyncNostradamusClient"]
    ) -> None:
        self.client = client
        self.base_path = "/api/v1"

    def build_path(self, *parts: str) -> str:
        """Build URL path from parts.

        Args:
            *parts: Path components

        Returns:
            Complete path string

        Example:
            >>> self.build_path("projects", "123", "collections")
            '/api/v1/projects/123/collections'
        """
        clean_parts = [str(p).strip("/") for p in parts if p]
        return f"{self.base_path}/{'/'.join(clean_parts)}"

    @overload
    def parse_response(self, data: dict[str, Any], model_class: type[T]) -> T: ...

    @overload
    def parse_response(
        self, data: list[dict[str, Any]], model_class: type[T]
    ) -> list[T]: ...

    def parse_response(
        self, data: Union[dict[str, Any], list[dict[str, Any]]], model_class: type[T]
    ) -> Union[T, list[T]]:
        """Parse response data into Pydantic model(s).

        Args:
            data: Response data (dict or list of dicts)
            model_class: Pydantic model class to parse into

        Returns:
            Parsed model instance(s)
        """
        if isinstance(data, list):
            return [model_class(**item) for item in data]
        return model_class(**data)

    def parse_list_response(
        self, data: Union[dict[str, Any], list[dict[str, Any]]], model_class: type[T]
    ) -> list[T]:
        """Parse a list endpoint payload into model instances.

        The API paginates list responses as
        `{"items": [...], "total": N, ...}` — unwrap the envelope.
        A bare list (or, defensively, a single object) still parses.

        Args:
            data: Response data (paginated envelope, list, or single object)
            model_class: Pydantic model class to parse items into

        Returns:
            List of parsed model instances
        """
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            data = data["items"]
        if isinstance(data, list):
            return [model_class(**item) for item in data]
        return [model_class(**data)]

    def validate_uuid(self, value: Union[str, UUID]) -> str:
        """Validate and convert UUID to string.

        Args:
            value: UUID string or object

        Returns:
            UUID as string

        Raises:
            ValueError: If value is not a valid UUID
        """
        if isinstance(value, UUID):
            return str(value)
        try:
            UUID(value)
            return str(value)
        except (ValueError, AttributeError, TypeError) as err:
            raise ValueError(f"Invalid UUID: {value}") from err
