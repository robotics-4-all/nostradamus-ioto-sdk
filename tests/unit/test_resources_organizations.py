"""Unit tests for resources.organizations module."""

from unittest.mock import AsyncMock, Mock

import pytest

from nostradamus_ioto_sdk.models import OrganizationResponse
from nostradamus_ioto_sdk.resources.organizations import OrganizationsResource


class TestOrganizationsResource:
    """Test suite for OrganizationsResource class."""

    @pytest.fixture
    def mock_client(self):
        """Create mock client with request method."""
        client = Mock()
        client.request = Mock()
        return client

    @pytest.fixture
    def resource(self, mock_client):
        """Create OrganizationsResource instance."""
        return OrganizationsResource(mock_client)

    def test_get_returns_organization_response(self, resource, mock_client):
        """Test that get() returns OrganizationResponse."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "organization_id": "12345678-1234-5678-1234-567812345678",
            "organization_name": "Test Org",
            "description": "Test description",
            "creation_date": "2024-01-01T00:00:00Z",
        }
        mock_client.request.return_value = mock_response

        # Call method
        result = resource.get()

        # Verify request was made correctly
        mock_client.request.assert_called_once_with(
            "GET", "/api/v1/organization/nostradamus"
        )

        # Verify response parsing
        assert isinstance(result, OrganizationResponse)
        assert str(result.organization_id) == "12345678-1234-5678-1234-567812345678"
        assert result.organization_name == "Test Org"
        assert result.description == "Test description"

    def test_update_with_description_only(self, resource, mock_client):
        """Test updating organization with description only."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "organization_id": "12345678-1234-5678-1234-567812345678",
            "organization_name": "Test Org",
            "description": "New description",
            "creation_date": "2024-01-01T00:00:00Z",
        }
        mock_client.request.return_value = mock_response

        # Call method
        result = resource.update(description="New description")

        # Verify request was made correctly
        mock_client.request.assert_called_once_with(
            "PUT",
            "/api/v1/organization/nostradamus",
            json={"description": "New description"},
        )

        # Verify response
        assert isinstance(result, OrganizationResponse)
        assert result.description == "New description"

    def test_update_with_tags_only(self, resource, mock_client):
        """Test updating organization with tags only."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "organization_id": "12345678-1234-5678-1234-567812345678",
            "organization_name": "Test Org",
            "description": "Test description",
            "creation_date": "2024-01-01T00:00:00Z",
            "tags": ["iot", "sensors"],
        }
        mock_client.request.return_value = mock_response

        # Call method
        result = resource.update(tags=["iot", "sensors"])

        # Verify request was made correctly
        mock_client.request.assert_called_once_with(
            "PUT",
            "/api/v1/organization/nostradamus",
            json={"tags": ["iot", "sensors"]},
        )

        # Verify response
        assert isinstance(result, OrganizationResponse)
        assert result.tags == ["iot", "sensors"]

    def test_update_with_both_description_and_tags(self, resource, mock_client):
        """Test updating organization with both description and tags."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "organization_id": "12345678-1234-5678-1234-567812345678",
            "organization_name": "Test Org",
            "description": "New description",
            "creation_date": "2024-01-01T00:00:00Z",
            "tags": ["iot", "sensors"],
        }
        mock_client.request.return_value = mock_response

        # Call method
        result = resource.update(description="New description", tags=["iot", "sensors"])

        # Verify request was made correctly
        mock_client.request.assert_called_once_with(
            "PUT",
            "/api/v1/organization/nostradamus",
            json={"description": "New description", "tags": ["iot", "sensors"]},
        )

        # Verify response
        assert isinstance(result, OrganizationResponse)
        assert result.description == "New description"
        assert result.tags == ["iot", "sensors"]

    def test_update_with_no_parameters(self, resource, mock_client):
        """Test updating organization with no parameters sends empty JSON."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "organization_id": "12345678-1234-5678-1234-567812345678",
            "organization_name": "Test Org",
            "description": "Test description",
            "creation_date": "2024-01-01T00:00:00Z",
        }
        mock_client.request.return_value = mock_response

        # Call method
        result = resource.update()

        # Verify request was made with empty JSON (exclude_none=True)
        mock_client.request.assert_called_once_with(
            "PUT", "/api/v1/organization/nostradamus", json={}
        )

        # Verify response
        assert isinstance(result, OrganizationResponse)


class TestOrganizationsResourceAsync:
    """Test async methods of OrganizationsResource."""

    @pytest.fixture
    def mock_async_client(self):
        """Create mock async client."""
        client = Mock()
        client.request = AsyncMock()
        return client

    @pytest.fixture
    def resource(self, mock_async_client):
        """Create OrganizationsResource with async client."""
        return OrganizationsResource(mock_async_client)

    @pytest.mark.asyncio
    async def test_aget_returns_organization_response(
        self, resource, mock_async_client
    ):
        """Test aget returns OrganizationResponse."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "organization_id": "12345678-1234-5678-1234-567812345678",
            "organization_name": "Test Org",
            "description": "Test description",
            "creation_date": "2024-01-01T00:00:00Z",
        }
        mock_async_client.request.return_value = mock_response

        result = await resource.aget()

        mock_async_client.request.assert_called_once_with(
            "GET", "/api/v1/organization/nostradamus"
        )
        assert isinstance(result, OrganizationResponse)
        assert result.organization_name == "Test Org"

    @pytest.mark.asyncio
    async def test_aupdate_returns_organization_response(
        self, resource, mock_async_client
    ):
        """Test aupdate returns OrganizationResponse."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "organization_id": "12345678-1234-5678-1234-567812345678",
            "organization_name": "Test Org",
            "description": "Updated description",
            "creation_date": "2024-01-01T00:00:00Z",
            "tags": ["iot"],
        }
        mock_async_client.request.return_value = mock_response

        result = await resource.aupdate(description="Updated description", tags=["iot"])

        mock_async_client.request.assert_called_once_with(
            "PUT",
            "/api/v1/organization/nostradamus",
            json={"description": "Updated description", "tags": ["iot"]},
        )
        assert isinstance(result, OrganizationResponse)
        assert result.description == "Updated description"
