"""User models for the Nostradamus IoTO SDK."""

from nostradamus_ioto_sdk.models._base import BaseModel


class UserRequest(BaseModel):
    """Request model for creating a new user."""

    username: str
    password: str


class Username(BaseModel):
    """Request model for identifying a user by username."""

    username: str
