"""Unit tests for Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from nostradamus_ioto_sdk.models import (
    CollectionCreateRequest,
    CollectionResponse,
    CollectionUpdateRequest,
    DeleteDataRequest,
    KeyType,
    OrganizationResponse,
    OrganizationUpdateRequest,
    ProjectCreateRequest,
    ProjectKeyCreateRequest,
    ProjectKeyResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    StatOperation,
)


class TestEnums:
    """Test enum types."""

    def test_key_type_values(self):
        """Test KeyType enum has expected values."""
        assert KeyType.READ == "read"
        assert KeyType.WRITE == "write"
        assert KeyType.MASTER == "master"

    def test_stat_operation_values(self):
        """Test StatOperation enum has expected values."""
        assert StatOperation.AVG == "avg"
        assert StatOperation.MAX == "max"
        assert StatOperation.MIN == "min"
        assert StatOperation.SUM == "sum"
        assert StatOperation.COUNT == "count"
        assert StatOperation.DISTINCT == "distinct"


class TestOrganizationModels:
    """Test organization-related models."""

    def test_organization_response_from_dict(self):
        """Test creating OrganizationResponse from dict."""
        data = {
            "organization_id": "550e8400-e29b-41d4-a716-446655440000",
            "organization_name": "Test Organization",
            "description": "Test description",
            "creation_date": "2024-01-01T00:00:00Z",
        }
        org = OrganizationResponse(**data)
        assert str(org.organization_id) == "550e8400-e29b-41d4-a716-446655440000"
        assert org.organization_name == "Test Organization"

    def test_organization_update_request(self):
        """Test OrganizationUpdateRequest."""
        update = OrganizationUpdateRequest(description="New Description")
        assert update.description == "New Description"

    def test_organization_update_request_validation(self):
        """Test OrganizationUpdateRequest validates name."""
        # Empty name should work (optional field)
        update = OrganizationUpdateRequest()
        assert update.model_dump(exclude_none=True) == {}


class TestProjectModels:
    """Test project-related models."""

    def test_project_response_from_dict(self):
        """Test creating ProjectResponse from dict."""
        data = {
            "project_id": "650e8400-e29b-41d4-a716-446655440000",
            "project_name": "Test Project",
            "description": "A test project",
            "organization_id": "550e8400-e29b-41d4-a716-446655440000",
            "organization_name": "Test Org",
            "creation_date": "2024-01-01T00:00:00Z",
        }
        project = ProjectResponse(**data)
        assert str(project.project_id) == "650e8400-e29b-41d4-a716-446655440000"
        assert project.project_name == "Test Project"
        assert project.description == "A test project"
        assert str(project.organization_id) == "550e8400-e29b-41d4-a716-446655440000"

    def test_project_create_request(self):
        """Test ProjectCreateRequest."""
        create = ProjectCreateRequest(
            project_name="New Project", description="Project description"
        )
        assert create.project_name == "New Project"
        assert create.description == "Project description"

    def test_project_create_request_without_description(self):
        """Test ProjectCreateRequest without optional description."""
        create = ProjectCreateRequest(project_name="New Project")
        assert create.project_name == "New Project"
        assert create.description is None

    def test_project_update_request(self):
        """Test ProjectUpdateRequest."""
        update = ProjectUpdateRequest(description="Updated desc")
        assert update.description == "Updated desc"


class TestCollectionModels:
    """Test collection-related models."""

    def test_collection_response_from_dict(self):
        """Test creating CollectionResponse from dict."""
        data = {
            "collection_id": "750e8400-e29b-41d4-a716-446655440000",
            "collection_name": "Test Collection",
            "description": "A test collection",
            "project_id": "650e8400-e29b-41d4-a716-446655440000",
            "project_name": "Test Project",
            "organization_id": "550e8400-e29b-41d4-a716-446655440000",
            "organization_name": "Test Org",
            "creation_date": "2024-01-01T00:00:00Z",
            "collection_schema": {"type": "object"},
        }
        collection = CollectionResponse(**data)
        assert str(collection.collection_id) == "750e8400-e29b-41d4-a716-446655440000"
        assert collection.collection_name == "Test Collection"
        assert collection.description == "A test collection"
        assert str(collection.project_id) == "650e8400-e29b-41d4-a716-446655440000"

    def test_collection_create_request(self):
        """Test CollectionCreateRequest."""
        create = CollectionCreateRequest(
            name="New Collection",
            description="Collection description",
            collection_schema={"type": "object"},
        )
        assert create.name == "New Collection"
        assert create.description == "Collection description"

    def test_collection_update_request(self):
        """Test CollectionUpdateRequest."""
        update = CollectionUpdateRequest(description="Updated desc")
        assert update.description == "Updated desc"


class TestProjectKeyModels:
    """Test project key-related models."""

    def test_project_key_response_from_dict(self):
        """Test creating ProjectKeyResponse from dict."""
        data = {
            "api_key": "key-123",
            "key_type": "read",
            "project_id": "650e8400-e29b-41d4-a716-446655440000",
            "created_at": "2024-01-01T00:00:00Z",
        }
        key = ProjectKeyResponse(**data)
        assert key.api_key == "key-123"
        assert key.key_type == "read"
        assert str(key.project_id) == "650e8400-e29b-41d4-a716-446655440000"

    def test_project_key_create_request(self):
        """Test ProjectKeyCreateRequest."""
        create = ProjectKeyCreateRequest(key_type=KeyType.WRITE)
        assert create.key_type == KeyType.WRITE

    def test_project_key_create_with_string_type(self):
        """Test ProjectKeyCreateRequest accepts string for key_type."""
        create = ProjectKeyCreateRequest(key_type="master")
        assert create.key_type == KeyType.MASTER


class TestDataModels:
    """Test data-related models."""

    def test_delete_data_request(self):
        """Test DeleteDataRequest."""
        delete = DeleteDataRequest(
            key="sensor-1",
            timestamp_from=datetime(2024, 1, 1),
            timestamp_to=datetime(2024, 1, 31),
        )
        assert delete.key == "sensor-1"
        assert delete.timestamp_from == datetime(2024, 1, 1)
        assert delete.timestamp_to == datetime(2024, 1, 31)

    def test_delete_data_request_optional_fields(self):
        """Test DeleteDataRequest with minimal fields."""
        delete = DeleteDataRequest()
        assert delete.key is None
        assert delete.timestamp_from is None
        assert delete.timestamp_to is None


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_project_json_serialization(self):
        """Test ProjectCreateRequest JSON serialization."""
        create = ProjectCreateRequest(project_name="Test", description="Desc")
        json_dict = create.model_dump()
        assert json_dict["project_name"] == "Test"
        assert json_dict["description"] == "Desc"

    def test_project_json_deserialization(self):
        """Test ProjectResponse JSON deserialization."""
        json_str = '{"project_id": "650e8400-e29b-41d4-a716-446655440000", "project_name": "Test", "organization_id": "550e8400-e29b-41d4-a716-446655440000", "organization_name": "Org", "creation_date": "2024-01-01T00:00:00Z"}'
        # Pydantic v2 uses model_validate_json
        project = ProjectResponse.model_validate_json(json_str)
        assert str(project.project_id) == "650e8400-e29b-41d4-a716-446655440000"
        assert project.project_name == "Test"

    def test_model_dump_exclude_none(self):
        """Test model_dump with exclude_none."""
        update = ProjectUpdateRequest(description="Test")
        dumped = update.model_dump(exclude_none=True)
        assert "description" in dumped
        assert "tags" not in dumped


class TestModelValidation:
    """Test model validation."""

    def test_empty_name_validation(self):
        """Test that empty names raise validation error due to min_length constraint."""
        # ProjectCreateRequest has min_length=1 for project_name
        with pytest.raises(ValidationError):
            ProjectCreateRequest(project_name="")

    def test_none_required_field_validation(self):
        """Test that required fields cannot be None."""
        with pytest.raises(ValidationError):
            ProjectCreateRequest(project_name=None)  # type: ignore

    def test_invalid_key_type_validation(self):
        """Test invalid key_type raises validation error."""
        with pytest.raises(ValidationError):
            ProjectKeyCreateRequest(key_type="invalid")  # type: ignore
