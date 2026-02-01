"""Base resource class for the Nostradamus IoTO SDK."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from ..client import NostradamusClient
    from ..async_client import AsyncNostradamusClient

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
        self._client = client
        self._base_path = "/api/v1"

    def _build_path(self, *parts: str) -> str:
        """Build URL path from parts.

        Args:
            *parts: Path components

        Returns:
            Complete path string

        Example:
            >>> self._build_path("projects", "123", "collections")
            '/api/v1/projects/123/collections'
        """
        clean_parts = [str(p).strip("/") for p in parts if p]
        return f"{self._base_path}/{'/'.join(clean_parts)}"

    def _parse_response(
        self, data: Union[Dict[str, Any], List[Dict[str, Any]]], model_class: Type[T]
    ) -> Union[T, List[T]]:
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

    def _validate_uuid(self, value: Union[str, UUID]) -> str:
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
