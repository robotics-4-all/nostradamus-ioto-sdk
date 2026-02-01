"""Validators for the Nostradamus IoTO SDK."""

from datetime import datetime
from typing import Union
from uuid import UUID

from dateutil import parser as dateutil_parser


def validate_uuid(value: Union[str, UUID]) -> UUID:
    """Validate and convert to UUID.

    Args:
        value: String or UUID to validate

    Returns:
        Valid UUID object

    Raises:
        ValueError: If value is not a valid UUID

    Example:
        >>> validate_uuid("550e8400-e29b-41d4-a716-446655440000")
        UUID('550e8400-e29b-41d4-a716-446655440000')
    """
    if isinstance(value, UUID):
        return value

    try:
        return UUID(value)
    except (ValueError, AttributeError, TypeError) as err:
        raise ValueError(f"Invalid UUID: {value}") from err


def validate_iso8601(value: Union[str, datetime]) -> datetime:
    """Validate and parse ISO 8601 timestamp.

    Args:
        value: ISO 8601 string or datetime object

    Returns:
        Valid datetime object

    Raises:
        ValueError: If value is not a valid ISO 8601 timestamp

    Example:
        >>> validate_iso8601("2024-02-01T12:00:00Z")
        datetime.datetime(2024, 2, 1, 12, 0, tzinfo=tzutc())
    """
    if isinstance(value, datetime):
        return value

    try:
        return dateutil_parser.isoparse(value)
    except (ValueError, TypeError) as err:
        raise ValueError(f"Invalid ISO 8601 timestamp: {value}") from err


def validate_project_id(project_id: Union[str, UUID]) -> str:
    """Validate project ID and convert to string.

    Args:
        project_id: Project UUID (string or UUID object)

    Returns:
        Project ID as string

    Raises:
        ValueError: If project_id is not valid
    """
    uuid_obj = validate_uuid(project_id)
    return str(uuid_obj)


def validate_collection_id(collection_id: Union[str, UUID]) -> str:
    """Validate collection ID and convert to string.

    Args:
        collection_id: Collection UUID (string or UUID object)

    Returns:
        Collection ID as string

    Raises:
        ValueError: If collection_id is not valid
    """
    uuid_obj = validate_uuid(collection_id)
    return str(uuid_obj)
