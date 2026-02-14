"""Unit tests for resources._base module."""

from unittest.mock import Mock
from uuid import UUID

import pytest
from pydantic import BaseModel

from nostradamus_ioto_sdk.resources._base import BaseResource


class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""

    id: str
    name: str


class TestBaseResource:
    """Test suite for BaseResource class."""

    @pytest.fixture
    def mock_client(self):
        """Create mock client."""
        return Mock()

    @pytest.fixture
    def resource(self, mock_client):
        """Create BaseResource instance."""
        return BaseResource(mock_client)

    def test_init_sets_client_and_base_path(self, mock_client):
        """Test that initialization sets client and base path."""
        resource = BaseResource(mock_client)
        assert resource.client is mock_client
        assert resource.base_path == "/api/v1"

    def test_build_path_with_single_part(self, resource):
        """Test building path with single component."""
        path = resource._build_path("projects")
        assert path == "/api/v1/projects"

    def test_build_path_with_multiple_parts(self, resource):
        """Test building path with multiple components."""
        path = resource._build_path("projects", "123", "collections")
        assert path == "/api/v1/projects/123/collections"

    def test_build_path_with_trailing_slashes(self, resource):
        """Test that trailing slashes are stripped."""
        path = resource._build_path("projects/", "/123/", "/collections/")
        assert path == "/api/v1/projects/123/collections"

    def test_build_path_with_empty_parts(self, resource):
        """Test that empty parts are filtered out."""
        path = resource._build_path("projects", "", "123", None, "collections")
        assert path == "/api/v1/projects/123/collections"

    def test_build_path_with_uuid(self, resource):
        """Test building path with UUID object."""
        uuid_obj = UUID("12345678-1234-5678-1234-567812345678")
        path = resource._build_path("projects", uuid_obj)
        assert path == "/api/v1/projects/12345678-1234-5678-1234-567812345678"

    def test_parse_response_with_dict(self, resource):
        """Test parsing single dict response."""
        data = {"id": "123", "name": "Test"}
        result = resource._parse_response(data, SampleModel)

        assert isinstance(result, SampleModel)
        assert result.id == "123"
        assert result.name == "Test"

    def test_parse_response_with_list(self, resource):
        """Test parsing list of dicts response."""
        data = [
            {"id": "1", "name": "First"},
            {"id": "2", "name": "Second"},
        ]
        result = resource._parse_response(data, SampleModel)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, SampleModel) for item in result)
        assert result[0].id == "1"
        assert result[0].name == "First"
        assert result[1].id == "2"
        assert result[1].name == "Second"

    def test_parse_response_with_empty_list(self, resource):
        """Test parsing empty list response."""
        data = []
        result = resource._parse_response(data, SampleModel)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_validate_uuid_with_string(self, resource):
        """Test UUID validation with valid string."""
        uuid_str = "12345678-1234-5678-1234-567812345678"
        result = resource._validate_uuid(uuid_str)
        assert result == uuid_str

    def test_validate_uuid_with_uuid_object(self, resource):
        """Test UUID validation with UUID object."""
        uuid_obj = UUID("12345678-1234-5678-1234-567812345678")
        result = resource._validate_uuid(uuid_obj)
        assert result == "12345678-1234-5678-1234-567812345678"

    def test_validate_uuid_with_invalid_string_raises_error(self, resource):
        """Test that invalid UUID string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID: not-a-uuid"):
            resource._validate_uuid("not-a-uuid")

    def test_validate_uuid_with_none_raises_error(self, resource):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID: None"):
            resource._validate_uuid(None)

    def test_validate_uuid_with_int_raises_error(self, resource):
        """Test that integer raises ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID: 123"):
            resource._validate_uuid(123)
