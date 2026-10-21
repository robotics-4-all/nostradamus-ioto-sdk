"""Unit tests for server-shape handling (envelopes, nested ids, refetch updates)."""

from unittest.mock import Mock

import pytest

from nostradamus_ioto_sdk.exceptions import ResourceNotFoundError
from nostradamus_ioto_sdk.models.collection import CollectionResponse
from nostradamus_ioto_sdk.models.project import ProjectResponse
from nostradamus_ioto_sdk.models.project_key import ProjectKeyResponse
from nostradamus_ioto_sdk.resources.collections import CollectionsResource
from nostradamus_ioto_sdk.resources.project_keys import ProjectKeysResource
from nostradamus_ioto_sdk.resources.projects import ProjectsResource
from nostradamus_ioto_sdk.resources.users import UsersResource

ORG_ID = "12345678-1234-5678-1234-567812345678"
PROJ_ID = "550e8400-e29b-41d4-a716-446655440000"
COLL_ID = "660e8400-e29b-41d4-a716-446655440001"
RAW_KEY = "a" * 64
NEW_KEY = "b" * 64


def _project_payload(**over):
    payload = {
        "organization_id": ORG_ID,
        "project_id": PROJ_ID,
        "organization_name": "org",
        "project_name": "proj",
        "description": "d",
        "tags": [],
        "creation_date": "2024-01-01T00:00:00Z",
    }
    payload.update(over)
    return payload


def _collection_payload(**over):
    payload = {
        "collection_name": "coll",
        "collection_id": COLL_ID,
        "project_id": PROJ_ID,
        "project_name": "proj",
        "organization_id": ORG_ID,
        "organization_name": "org",
        "description": "d",
        "tags": [],
        "creation_date": "2024-01-01T00:00:00Z",
        "collection_schema": {"key": "K1"},
    }
    payload.update(over)
    return payload


def _key_payload(api_key=RAW_KEY, **over):
    payload = {
        "api_key": api_key,
        "project_id": PROJ_ID,
        "key_type": "write",
        "created_at": "2024-01-01T00:00:00Z",
    }
    payload.update(over)
    return payload


def _mock_request(payloads):
    """Build a Mock client whose request() returns payloads in order."""
    client = Mock()
    responses = []
    for payload in payloads:
        response = Mock()
        response.json.return_value = payload
        responses.append(response)
    client.request.side_effect = responses
    return client


class TestParseListEnvelope:
    def test_projects_list_unwraps_envelope(self):
        client = _mock_request([{"items": [_project_payload()], "total": 1}])
        result = ProjectsResource(client).list()
        assert isinstance(result, list)
        assert isinstance(result[0], ProjectResponse)
        assert str(result[0].project_id) == PROJ_ID

    def test_projects_list_accepts_bare_list(self):
        client = _mock_request([[_project_payload()]])
        result = ProjectsResource(client).list()
        assert len(result) == 1
        assert isinstance(result[0], ProjectResponse)

    def test_collections_list_unwraps_envelope(self):
        client = _mock_request([{"items": [_collection_payload()], "total": 1}])
        result = CollectionsResource(client).list(PROJ_ID)
        assert len(result) == 1
        assert isinstance(result[0], CollectionResponse)

    def test_users_list_unwraps_envelope_to_usernames(self):
        client = _mock_request(
            [
                {
                    "items": [{"id": "1", "username": "alice", "role": "member"}],
                    "total": 1,
                }
            ]
        )
        assert UsersResource(client).list(ORG_ID) == ["alice"]

    def test_project_keys_list_accepts_bare_list(self):
        client = _mock_request([[_key_payload()]])
        result = ProjectKeysResource(client).list(PROJ_ID)
        assert len(result) == 1
        assert isinstance(result[0], ProjectKeyResponse)


class TestNestedCreateId:
    def test_projects_create_unwraps_nested_id(self):
        client = _mock_request(
            [{"message": "created", "id": {"project_id": PROJ_ID}}, _project_payload()]
        )
        result = ProjectsResource(client).create(name="p")
        assert isinstance(result, ProjectResponse)
        assert str(result.project_id) == PROJ_ID
        # Second call is the follow-up GET on the unwrapped id
        assert client.request.call_args_list[1].args[1].endswith(f"/projects/{PROJ_ID}")


class TestUpdateRefetch:
    def test_projects_update_returns_refetched_object(self):
        client = _mock_request(
            [
                {"message": "Project successfully updated"},
                _project_payload(description="new"),
            ]
        )
        result = ProjectsResource(client).update(PROJ_ID, description="new")
        assert isinstance(result, ProjectResponse)
        assert result.description == "new"
        assert client.request.call_count == 2

    def test_collections_update_returns_refetched_object(self):
        client = _mock_request(
            [
                {"message": "Collection updated successfully"},
                _collection_payload(description="new"),
            ]
        )
        result = CollectionsResource(client).update(PROJ_ID, COLL_ID, description="new")
        assert isinstance(result, CollectionResponse)
        assert result.description == "new"
        assert client.request.call_count == 2


class TestProjectKeyRoutes:
    def test_regenerate_uses_body_route(self):
        client = _mock_request([_key_payload(api_key=NEW_KEY)])
        result = ProjectKeysResource(client).regenerate(PROJ_ID, RAW_KEY)
        assert isinstance(result, ProjectKeyResponse)
        assert result.api_key == NEW_KEY
        (method, path), kwargs = client.request.call_args
        assert method == "PUT"
        assert path == f"/api/v1/projects/{PROJ_ID}/keys/regenerate"
        assert kwargs["json"] == {"key_value": RAW_KEY}

    def test_delete_uses_body_route(self):
        client = _mock_request([{"message": "deleted"}])
        ProjectKeysResource(client).delete(PROJ_ID, RAW_KEY)
        (method, path), kwargs = client.request.call_args
        assert method == "DELETE"
        assert path == f"/api/v1/projects/{PROJ_ID}/keys/delete_key"
        assert kwargs["json"] == {"key_value": RAW_KEY}

    def test_get_matches_from_list(self):
        client = _mock_request([[_key_payload()]])
        result = ProjectKeysResource(client).get(PROJ_ID, RAW_KEY)
        assert isinstance(result, ProjectKeyResponse)

    def test_get_missing_key_raises_not_found(self):
        client = _mock_request([[_key_payload()]])
        with pytest.raises(ResourceNotFoundError):
            ProjectKeysResource(client).get(PROJ_ID, NEW_KEY)


class TestUserRoutes:
    def test_update_password_uses_org_scoped_route(self):
        client = _mock_request([{"message": "ok"}])
        UsersResource(client).update_password(ORG_ID, "alice", "new-pass")
        (method, path), kwargs = client.request.call_args
        assert method == "PUT"
        assert path == f"/api/v1/organizations/{ORG_ID}/users/update_password"
        assert kwargs["json"] == {"username": "alice", "password": "new-pass"}

    def test_delete_uses_org_scoped_route(self):
        client = _mock_request([{"message": "ok"}])
        UsersResource(client).delete(ORG_ID, "alice")
        (method, path), kwargs = client.request.call_args
        assert method == "DELETE"
        assert path == f"/api/v1/organizations/{ORG_ID}/users"
        assert kwargs["json"] == {"username": "alice"}
