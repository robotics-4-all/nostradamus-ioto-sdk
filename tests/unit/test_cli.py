"""Unit tests for CLI module."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from nostradamus_ioto_sdk.cli.main import cli
from nostradamus_ioto_sdk.exceptions import (
    AuthenticationError,
    NostradamusError,
    ResourceNotFoundError,
    ValidationError,
)
from nostradamus_ioto_sdk.models import (
    CollectionResponse,
    OrganizationResponse,
    ProjectKeyResponse,
    ProjectResponse,
)

PID = "22345678-1234-5678-1234-567812345678"
CID = "32345678-1234-5678-1234-567812345678"
PATCH_CLIENT = "nostradamus_ioto_sdk.cli.main.NostradamusClient"


class TestCliRoot:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_org(self):
        return OrganizationResponse(
            organization_id="12345678-1234-5678-1234-567812345678",
            organization_name="Test Org",
            description="Test description",
            creation_date="2024-01-01T00:00:00Z",
            tags=["iot"],
        )

    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_verbose(self, runner, mock_org):
        with patch(PATCH_CLIENT) as mock_cls:
            mock_cls.return_value.organizations.get.return_value = mock_org
            result = runner.invoke(cli, ["--verbose", "org", "get", "--api-key", "k"])
            assert result.exit_code == 0
            assert "Verbose" in result.output


class TestCliGetClient:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_no_api_key_exits(self, runner, monkeypatch):
        monkeypatch.delenv("NOSTRADAMUS_API_KEY", raising=False)
        result = runner.invoke(cli, ["org", "get"])
        assert result.exit_code == 1
        assert "No API key" in result.output


class TestCliHandleError:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch(PATCH_CLIENT)
    def test_authentication_error(self, mock_cls, runner):
        mock_cls.return_value.organizations.get.side_effect = AuthenticationError(
            "Invalid"
        )
        result = runner.invoke(cli, ["org", "get", "--api-key", "bad"])
        assert result.exit_code == 1
        assert "Authentication Error" in result.output

    @patch(PATCH_CLIENT)
    def test_not_found_error(self, mock_cls, runner):
        mock_cls.return_value.projects.get.side_effect = ResourceNotFoundError(
            "Not found"
        )
        result = runner.invoke(cli, ["projects", "get", PID, "--api-key", "k"])
        assert result.exit_code == 1
        assert "Not Found" in result.output

    @patch(PATCH_CLIENT)
    def test_validation_error(self, mock_cls, runner):
        mock_cls.return_value.projects.create.side_effect = ValidationError("Bad input")
        result = runner.invoke(
            cli, ["projects", "create", "--name", "x", "--api-key", "k"]
        )
        assert result.exit_code == 1
        assert "Validation Error" in result.output

    @patch(PATCH_CLIENT)
    def test_generic_nostradamus_error(self, mock_cls, runner):
        mock_cls.return_value.organizations.get.side_effect = NostradamusError(
            "Something"
        )
        result = runner.invoke(cli, ["org", "get", "--api-key", "k"])
        assert result.exit_code == 1
        assert "API Error" in result.output

    @patch(PATCH_CLIENT)
    def test_unexpected_error(self, mock_cls, runner):
        mock_cls.return_value.organizations.get.side_effect = RuntimeError("Unexpected")
        result = runner.invoke(cli, ["org", "get", "--api-key", "k"])
        assert result.exit_code == 1
        assert "Error" in result.output


class TestCliOrganization:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_org(self):
        return OrganizationResponse(
            organization_id="12345678-1234-5678-1234-567812345678",
            organization_name="Test Org",
            description="Test description",
            creation_date="2024-01-01T00:00:00Z",
            tags=["iot"],
        )

    @patch(PATCH_CLIENT)
    def test_org_get_table(self, mock_cls, runner, mock_org):
        mock_cls.return_value.organizations.get.return_value = mock_org
        result = runner.invoke(cli, ["org", "get", "--api-key", "k"])
        assert result.exit_code == 0
        assert "Test Org" in result.output

    @patch(PATCH_CLIENT)
    def test_org_get_json(self, mock_cls, runner, mock_org):
        mock_cls.return_value.organizations.get.return_value = mock_org
        result = runner.invoke(cli, ["org", "get", "--api-key", "k", "-f", "json"])
        assert result.exit_code == 0
        assert "Test Org" in result.output

    @patch(PATCH_CLIENT)
    def test_org_get_compact(self, mock_cls, runner, mock_org):
        mock_cls.return_value.organizations.get.return_value = mock_org
        result = runner.invoke(cli, ["org", "get", "--api-key", "k", "-f", "compact"])
        assert result.exit_code == 0
        assert "Test Org" in result.output

    @patch(PATCH_CLIENT)
    def test_org_update_with_description(self, mock_cls, runner, mock_org):
        mock_cls.return_value.organizations.update.return_value = mock_org
        result = runner.invoke(
            cli, ["org", "update", "--api-key", "k", "-d", "New desc"]
        )
        assert result.exit_code == 0
        assert "Updated" in result.output

    @patch(PATCH_CLIENT)
    def test_org_update_no_params(self, mock_cls, runner):
        result = runner.invoke(cli, ["org", "update", "--api-key", "k"])
        assert result.exit_code == 0
        assert "No updates" in result.output


class TestCliProjects:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_project(self):
        return ProjectResponse(
            organization_id="12345678-1234-5678-1234-567812345678",
            project_id="22345678-1234-5678-1234-567812345678",
            organization_name="Test Org",
            project_name="Test Project",
            description="Test description",
            tags=["iot"],
            creation_date="2024-01-01T00:00:00Z",
        )

    @patch(PATCH_CLIENT)
    def test_projects_list_table(self, mock_cls, runner, mock_project):
        mock_cls.return_value.projects.list.return_value = [mock_project]
        result = runner.invoke(cli, ["projects", "list", "--api-key", "k"])
        assert result.exit_code == 0
        assert "Test Project" in result.output

    @patch(PATCH_CLIENT)
    def test_projects_list_json(self, mock_cls, runner, mock_project):
        mock_cls.return_value.projects.list.return_value = [mock_project]
        result = runner.invoke(
            cli, ["projects", "list", "--api-key", "k", "-f", "json"]
        )
        assert result.exit_code == 0
        assert "Test Project" in result.output

    @patch(PATCH_CLIENT)
    def test_projects_list_compact(self, mock_cls, runner, mock_project):
        mock_cls.return_value.projects.list.return_value = [mock_project]
        result = runner.invoke(
            cli, ["projects", "list", "--api-key", "k", "-f", "compact"]
        )
        assert result.exit_code == 0
        assert "Test Project" in result.output

    @patch(PATCH_CLIENT)
    def test_projects_list_empty(self, mock_cls, runner):
        mock_cls.return_value.projects.list.return_value = []
        result = runner.invoke(cli, ["projects", "list", "--api-key", "k"])
        assert result.exit_code == 0
        assert "No projects found" in result.output

    @patch(PATCH_CLIENT)
    def test_projects_list_with_limit(self, mock_cls, runner, mock_project):
        mock_cls.return_value.projects.list.return_value = [mock_project, mock_project]
        result = runner.invoke(cli, ["projects", "list", "--api-key", "k", "-n", "1"])
        assert result.exit_code == 0

    @patch(PATCH_CLIENT)
    def test_projects_get_table(self, mock_cls, runner, mock_project):
        mock_cls.return_value.projects.get.return_value = mock_project
        result = runner.invoke(cli, ["projects", "get", PID, "--api-key", "k"])
        assert result.exit_code == 0
        assert "Test Project" in result.output

    @patch(PATCH_CLIENT)
    def test_projects_get_json(self, mock_cls, runner, mock_project):
        mock_cls.return_value.projects.get.return_value = mock_project
        result = runner.invoke(
            cli, ["projects", "get", PID, "--api-key", "k", "-f", "json"]
        )
        assert result.exit_code == 0

    @patch(PATCH_CLIENT)
    def test_projects_get_compact(self, mock_cls, runner, mock_project):
        mock_cls.return_value.projects.get.return_value = mock_project
        result = runner.invoke(
            cli, ["projects", "get", PID, "--api-key", "k", "-f", "compact"]
        )
        assert result.exit_code == 0
        assert "Test Project" in result.output

    @patch(PATCH_CLIENT)
    def test_projects_create(self, mock_cls, runner, mock_project):
        mock_cls.return_value.projects.create.return_value = mock_project
        result = runner.invoke(
            cli, ["projects", "create", "--name", "P", "--api-key", "k"]
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    @patch(PATCH_CLIENT)
    def test_projects_update_with_description(self, mock_cls, runner, mock_project):
        mock_cls.return_value.projects.update.return_value = mock_project
        result = runner.invoke(
            cli, ["projects", "update", PID, "--api-key", "k", "-d", "New"]
        )
        assert result.exit_code == 0
        assert "Updated" in result.output

    @patch(PATCH_CLIENT)
    def test_projects_update_no_params(self, mock_cls, runner):
        result = runner.invoke(cli, ["projects", "update", PID, "--api-key", "k"])
        assert result.exit_code == 0
        assert "No updates" in result.output

    @patch(PATCH_CLIENT)
    def test_projects_delete_confirmed(self, mock_cls, runner):
        mock_cls.return_value.projects.delete.return_value = None
        result = runner.invoke(cli, ["projects", "delete", PID, "--api-key", "k", "-y"])
        assert result.exit_code == 0
        assert "Deleted" in result.output

    @patch(PATCH_CLIENT)
    def test_projects_delete_cancelled(self, mock_cls, runner):
        result = runner.invoke(
            cli, ["projects", "delete", PID, "--api-key", "k"], input="n\n"
        )
        assert result.exit_code == 0
        assert "Cancelled" in result.output


class TestCliCollections:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_collection(self):
        return CollectionResponse(
            collection_name="Test Collection",
            collection_id="32345678-1234-5678-1234-567812345678",
            project_id="22345678-1234-5678-1234-567812345678",
            project_name="Test Project",
            organization_id="12345678-1234-5678-1234-567812345678",
            organization_name="Test Org",
            description="Test description",
            tags=["iot"],
            creation_date="2024-01-01T00:00:00Z",
            collection_schema={"type": "timeseries"},
        )

    @patch(PATCH_CLIENT)
    def test_collections_list_table(self, mock_cls, runner, mock_collection):
        mock_cls.return_value.collections.list.return_value = [mock_collection]
        result = runner.invoke(
            cli, ["collections", "list", "-p", PID, "--api-key", "k"]
        )
        assert result.exit_code == 0
        assert "Test Collection" in result.output

    @patch(PATCH_CLIENT)
    def test_collections_list_json(self, mock_cls, runner, mock_collection):
        mock_cls.return_value.collections.list.return_value = [mock_collection]
        result = runner.invoke(
            cli, ["collections", "list", "-p", PID, "--api-key", "k", "-f", "json"]
        )
        assert result.exit_code == 0

    @patch(PATCH_CLIENT)
    def test_collections_list_compact(self, mock_cls, runner, mock_collection):
        mock_cls.return_value.collections.list.return_value = [mock_collection]
        result = runner.invoke(
            cli, ["collections", "list", "-p", PID, "--api-key", "k", "-f", "compact"]
        )
        assert result.exit_code == 0
        assert "Test Collection" in result.output

    @patch(PATCH_CLIENT)
    def test_collections_list_empty(self, mock_cls, runner):
        mock_cls.return_value.collections.list.return_value = []
        result = runner.invoke(
            cli, ["collections", "list", "-p", PID, "--api-key", "k"]
        )
        assert result.exit_code == 0
        assert "No collections found" in result.output

    @patch(PATCH_CLIENT)
    def test_collections_list_with_limit(self, mock_cls, runner, mock_collection):
        mock_cls.return_value.collections.list.return_value = [
            mock_collection,
            mock_collection,
        ]
        result = runner.invoke(
            cli, ["collections", "list", "-p", PID, "--api-key", "k", "-n", "1"]
        )
        assert result.exit_code == 0

    @patch(PATCH_CLIENT)
    def test_collections_get_table(self, mock_cls, runner, mock_collection):
        mock_cls.return_value.collections.get.return_value = mock_collection
        result = runner.invoke(
            cli, ["collections", "get", CID, "-p", PID, "--api-key", "k"]
        )
        assert result.exit_code == 0
        assert "Test Collection" in result.output

    @patch(PATCH_CLIENT)
    def test_collections_get_json(self, mock_cls, runner, mock_collection):
        mock_cls.return_value.collections.get.return_value = mock_collection
        result = runner.invoke(
            cli, ["collections", "get", CID, "-p", PID, "--api-key", "k", "-f", "json"]
        )
        assert result.exit_code == 0

    @patch(PATCH_CLIENT)
    def test_collections_get_compact(self, mock_cls, runner, mock_collection):
        mock_cls.return_value.collections.get.return_value = mock_collection
        result = runner.invoke(
            cli,
            ["collections", "get", CID, "-p", PID, "--api-key", "k", "-f", "compact"],
        )
        assert result.exit_code == 0
        assert "Test Collection" in result.output

    @patch(PATCH_CLIENT)
    def test_collections_create(self, mock_cls, runner, mock_collection):
        mock_cls.return_value.collections.create.return_value = mock_collection
        result = runner.invoke(
            cli,
            [
                "collections",
                "create",
                "-p",
                PID,
                "-n",
                "C",
                "-d",
                "D",
                "-s",
                '{"type": "ts"}',
                "--api-key",
                "k",
            ],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    @patch(PATCH_CLIENT)
    def test_collections_create_invalid_json(self, mock_cls, runner):
        result = runner.invoke(
            cli,
            [
                "collections",
                "create",
                "-p",
                PID,
                "-n",
                "C",
                "-d",
                "D",
                "-s",
                "not-json",
                "--api-key",
                "k",
            ],
        )
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output

    @patch(PATCH_CLIENT)
    def test_collections_delete_confirmed(self, mock_cls, runner):
        mock_cls.return_value.collections.delete.return_value = None
        result = runner.invoke(
            cli, ["collections", "delete", CID, "-p", PID, "--api-key", "k", "-y"]
        )
        assert result.exit_code == 0
        assert "Deleted" in result.output

    @patch(PATCH_CLIENT)
    def test_collections_delete_cancelled(self, mock_cls, runner):
        result = runner.invoke(
            cli,
            ["collections", "delete", CID, "-p", PID, "--api-key", "k"],
            input="n\n",
        )
        assert result.exit_code == 0
        assert "Cancelled" in result.output


class TestCliData:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch(PATCH_CLIENT)
    def test_data_send(self, mock_cls, runner):
        mock_cls.return_value.data.send.return_value = None
        result = runner.invoke(
            cli,
            [
                "data",
                "send",
                "-p",
                PID,
                "-c",
                CID,
                "-d",
                '[{"value": 25.5}]',
                "--api-key",
                "k",
            ],
        )
        assert result.exit_code == 0
        assert "Sent" in result.output

    @patch(PATCH_CLIENT)
    def test_data_send_single_object(self, mock_cls, runner):
        mock_cls.return_value.data.send.return_value = None
        result = runner.invoke(
            cli,
            [
                "data",
                "send",
                "-p",
                PID,
                "-c",
                CID,
                "-d",
                '{"value": 25.5}',
                "--api-key",
                "k",
            ],
        )
        assert result.exit_code == 0
        assert "Sent 1 data point" in result.output

    @patch(PATCH_CLIENT)
    def test_data_send_invalid_json(self, mock_cls, runner):
        result = runner.invoke(
            cli,
            [
                "data",
                "send",
                "-p",
                PID,
                "-c",
                CID,
                "-d",
                "not-json",
                "--api-key",
                "k",
            ],
        )
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output

    @patch(PATCH_CLIENT)
    def test_data_get_json(self, mock_cls, runner):
        mock_cls.return_value.data.get.return_value = [{"value": 25.5}]
        result = runner.invoke(
            cli,
            ["data", "get", "-p", PID, "-c", CID, "--api-key", "k", "-f", "json"],
        )
        assert result.exit_code == 0

    @patch(PATCH_CLIENT)
    def test_data_get_table(self, mock_cls, runner):
        mock_cls.return_value.data.get.return_value = [{"value": 25.5}]
        result = runner.invoke(
            cli, ["data", "get", "-p", PID, "-c", CID, "--api-key", "k"]
        )
        assert result.exit_code == 0
        assert "Records" in result.output

    @patch(PATCH_CLIENT)
    def test_data_get_empty(self, mock_cls, runner):
        mock_cls.return_value.data.get.return_value = []
        result = runner.invoke(
            cli, ["data", "get", "-p", PID, "-c", CID, "--api-key", "k"]
        )
        assert result.exit_code == 0
        assert "Records" in result.output


class TestCliKeys:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_key(self):
        return ProjectKeyResponse(
            api_key="test-api-key-12345",
            project_id="22345678-1234-5678-1234-567812345678",
            key_type="read",
            created_at="2024-01-01T00:00:00Z",
        )

    @patch(PATCH_CLIENT)
    def test_keys_list_table(self, mock_cls, runner, mock_key):
        mock_cls.return_value.project_keys.list.return_value = [mock_key]
        result = runner.invoke(cli, ["keys", "list", "-p", PID, "--api-key", "k"])
        assert result.exit_code == 0
        assert "test-api-key" in result.output

    @patch(PATCH_CLIENT)
    def test_keys_list_json(self, mock_cls, runner, mock_key):
        mock_cls.return_value.project_keys.list.return_value = [mock_key]
        result = runner.invoke(
            cli, ["keys", "list", "-p", PID, "--api-key", "k", "-f", "json"]
        )
        assert result.exit_code == 0

    @patch(PATCH_CLIENT)
    def test_keys_list_compact(self, mock_cls, runner, mock_key):
        mock_cls.return_value.project_keys.list.return_value = [mock_key]
        result = runner.invoke(
            cli, ["keys", "list", "-p", PID, "--api-key", "k", "-f", "compact"]
        )
        assert result.exit_code == 0
        assert "read" in result.output

    @patch(PATCH_CLIENT)
    def test_keys_list_empty(self, mock_cls, runner):
        mock_cls.return_value.project_keys.list.return_value = []
        result = runner.invoke(cli, ["keys", "list", "-p", PID, "--api-key", "k"])
        assert result.exit_code == 0
        assert "No API keys found" in result.output

    @patch(PATCH_CLIENT)
    def test_keys_create(self, mock_cls, runner, mock_key):
        mock_cls.return_value.project_keys.create.return_value = mock_key
        result = runner.invoke(
            cli, ["keys", "create", "-p", PID, "-t", "read", "--api-key", "k"]
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    @patch(PATCH_CLIENT)
    def test_keys_delete_confirmed(self, mock_cls, runner):
        mock_cls.return_value.project_keys.delete.return_value = None
        result = runner.invoke(
            cli,
            ["keys", "delete", "key-to-del", "-p", PID, "--api-key", "k", "-y"],
        )
        assert result.exit_code == 0
        assert "Deleted" in result.output

    @patch(PATCH_CLIENT)
    def test_keys_delete_cancelled(self, mock_cls, runner):
        result = runner.invoke(
            cli,
            ["keys", "delete", "key-to-del", "-p", PID, "--api-key", "k"],
            input="n\n",
        )
        assert result.exit_code == 0
        assert "Cancelled" in result.output
