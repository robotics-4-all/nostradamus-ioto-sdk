"""Error response models for the Nostradamus IoTO SDK."""

from pydantic import Field

from ._base import BaseModel


class ValidationError(BaseModel):
    """Validation error detail.

    Attributes:
        loc: Location of the error (field path)
        msg: Error message
        type: Error type identifier
    """

    loc: list[str | int] = Field(..., description="Error location (field path)")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type identifier")


class HTTPValidationError(BaseModel):
    """HTTP 422 validation error response.

    Attributes:
        detail: List of validation errors
    """

    detail: list[ValidationError] | None = Field(
        default=None, description="List of validation errors"
    )
