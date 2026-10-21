"""Organization resource for the Nostradamus IoTO SDK."""

from typing import TYPE_CHECKING, Optional, cast

import httpx

from ..models.organization import OrganizationResponse, OrganizationUpdateRequest
from ._base import BaseResource

if TYPE_CHECKING:
    pass


class OrganizationsResource(BaseResource):
    """Organization management operations.

    Provides methods to get and update organization information.
    """

    def get(self) -> OrganizationResponse:
        """Get organization information.

        Returns:
            OrganizationResponse: Organization details

        Raises:
            AuthenticationError: If not authenticated
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> org = client.organizations.get()
            >>> print(org.organization_name)
            'My Organization'
        """
        response = cast(
            httpx.Response,
            # The API scopes /organization to the caller's auth context —
            # no name segment. (A hardcoded name matched no route → 404.)
            self.client.request("GET", self.build_path("organization")),
        )
        return cast(
            OrganizationResponse,
            self.parse_response(response.json(), OrganizationResponse),
        )

    async def aget(self) -> OrganizationResponse:
        """Get organization information (async).

        Returns:
            OrganizationResponse: Organization details

        Raises:
            AuthenticationError: If not authenticated
            APIError: If request fails

        Example:
            >>> async with AsyncNostradamusClient(api_key="...") as client:
            ...     org = await client.organizations.aget()
            ...     print(org.organization_name)
        """
        response = await self.client.request("GET", self.build_path("organization"))
        return self.parse_response(response.json(), OrganizationResponse)

    def update(
        self,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> OrganizationResponse:
        """Update organization information.

        Args:
            description: New description for the organization
            tags: New tags for the organization

        Returns:
            OrganizationResponse: Updated organization details

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If input is invalid
            APIError: If request fails

        Example:
            >>> client = NostradamusClient(api_key="...")
            >>> org = client.organizations.update(
            ...     description="Updated description",
            ...     tags=["iot", "sensors"]
            ... )
        """
        request_data = OrganizationUpdateRequest(description=description, tags=tags)
        self.client.request(
            "PUT",
            self.build_path("organization"),
            json=request_data.model_dump(exclude_none=True),
        )
        # The API returns {"message": ...}, not the updated object —
        # refetch so callers get the OrganizationResponse this method promises.
        return cast(OrganizationResponse, self.get())

    async def aupdate(
        self,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> OrganizationResponse:
        """Update organization information (async).

        Args:
            description: New description for the organization
            tags: New tags for the organization

        Returns:
            OrganizationResponse: Updated organization details

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If input is invalid
            APIError: If request fails

        Example:
            >>> async with AsyncNostradamusClient(api_key="...") as client:
            ...     org = await client.organizations.aupdate(
            ...         description="Updated description"
            ...     )
        """
        request_data = OrganizationUpdateRequest(description=description, tags=tags)
        await self.client.request(
            "PUT",
            self.build_path("organization"),
            json=request_data.model_dump(exclude_none=True),
        )
        # The API returns {"message": ...}, not the updated object —
        # refetch so callers get the OrganizationResponse this method promises.
        return await self.aget()
