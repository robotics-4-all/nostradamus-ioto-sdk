import builtins
from typing import TYPE_CHECKING, Union
from uuid import UUID

from ..models.user import Username, UserRequest
from ._base import BaseResource

if TYPE_CHECKING:
    pass


class UsersResource(BaseResource):
    """User management operations."""

    def create(
        self,
        organization_id: Union[str, UUID],
        username: str,
        password: str,
    ) -> None:
        """Create a new user in an organization.

        Args:
            organization_id: Organization UUID
            username: Username for the new user
            password: Password for the new user

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If input is invalid
            APIError: If request fails
        """
        org_id_str = self.validate_uuid(organization_id)
        request_data = UserRequest(username=username, password=password)
        self.client.request(
            "POST",
            self.build_path("organizations", org_id_str, "users"),
            json=request_data.model_dump(),
        )

    async def acreate(
        self,
        organization_id: Union[str, UUID],
        username: str,
        password: str,
    ) -> None:
        """Create a new user in an organization (async)."""
        org_id_str = self.validate_uuid(organization_id)
        request_data = UserRequest(username=username, password=password)
        await self.client.request(
            "POST",
            self.build_path("organizations", org_id_str, "users"),
            json=request_data.model_dump(),
        )

    def list(
        self,
        organization_id: Union[str, UUID],
    ) -> builtins.list[str]:
        """List all users in an organization.

        Args:
            organization_id: Organization UUID

        Returns:
            List of usernames

        Raises:
            AuthenticationError: If not authenticated
            APIError: If request fails
        """
        org_id_str = self.validate_uuid(organization_id)
        response = self.client.request(
            "GET", self.build_path("organizations", org_id_str, "users")
        )
        return response.json()

    async def alist(
        self,
        organization_id: Union[str, UUID],
    ) -> builtins.list[str]:
        """List all users in an organization (async)."""
        org_id_str = self.validate_uuid(organization_id)
        response = await self.client.request(
            "GET", self.build_path("organizations", org_id_str, "users")
        )
        return response.json()

    def update_password(
        self,
        username: str,
        new_password: str,
    ) -> None:
        """Update a user's password.

        Args:
            username: Username to update
            new_password: New password

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If input is invalid
            APIError: If request fails
        """
        request_data = UserRequest(username=username, password=new_password)
        self.client.request(
            "PUT",
            self.build_path("update_password"),
            json=request_data.model_dump(),
        )

    async def aupdate_password(
        self,
        username: str,
        new_password: str,
    ) -> None:
        """Update a user's password (async)."""
        request_data = UserRequest(username=username, password=new_password)
        await self.client.request(
            "PUT",
            self.build_path("update_password"),
            json=request_data.model_dump(),
        )

    def delete(
        self,
        username: str,
    ) -> None:
        """Delete a user.

        Args:
            username: Username to delete

        Raises:
            AuthenticationError: If not authenticated
            APIError: If request fails
        """
        request_data = Username(username=username)
        self.client.request(
            "DELETE",
            self.build_path("users"),
            json=request_data.model_dump(),
        )

    async def adelete(
        self,
        username: str,
    ) -> None:
        """Delete a user (async)."""
        request_data = Username(username=username)
        await self.client.request(
            "DELETE",
            self.build_path("users"),
            json=request_data.model_dump(),
        )
