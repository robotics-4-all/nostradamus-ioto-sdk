"""Live integration tests against a real Nostradamus API.

Every test is marked ``integration`` and is skipped unless credentials are
present (see ``tests/integration/conftest.py``). Run them with::

    make test-integration

Only read-only operations are exercised, so the suite is safe to point at a
production deployment.
"""

from __future__ import annotations

import os

import pytest

from nostradamus_ioto_sdk import (
    HealthResponse,
    OrganizationResponse,
    ProjectResponse,
    ReadyResponse,
)

pytestmark = pytest.mark.integration

PROJECT_ID_ENV = "NOSTRADAMUS_PROJECT_ID"


class TestLiveServiceHealth:
    """Service health endpoints."""

    def test_health_returns_status(self, live_client):
        """GET /health reports a status."""
        result = live_client.health.health()

        assert isinstance(result, HealthResponse)
        assert result.status

    def test_ready_reports_checks(self, live_client):
        """GET /ready reports readiness checks."""
        result = live_client.health.ready()

        assert isinstance(result, ReadyResponse)
        assert result.status
        assert isinstance(result.checks, dict)


class TestLiveOrganization:
    """Organization endpoint scoped to the caller's credentials."""

    def test_get_organization(self, live_client):
        """Sync client resolves the caller's organization."""
        organization = live_client.organizations.get()

        assert isinstance(organization, OrganizationResponse)
        assert organization.organization_id is not None
        assert organization.organization_name

    async def test_aget_organization(self, live_async_client):
        """Async client resolves the caller's organization."""
        organization = await live_async_client.organizations.aget()

        assert isinstance(organization, OrganizationResponse)
        assert organization.organization_name


class TestLiveProjects:
    """Project listing and retrieval."""

    def test_list_projects(self, live_client):
        """Projects list returns parsed models."""
        projects = live_client.projects.list()

        assert isinstance(projects, list)
        assert all(isinstance(project, ProjectResponse) for project in projects)

    def test_get_project(self, live_client):
        """A project can be fetched by id."""
        project_id = os.getenv(PROJECT_ID_ENV)
        if not project_id:
            pytest.skip(f"{PROJECT_ID_ENV} not set")

        project = live_client.projects.get(project_id)

        assert isinstance(project, ProjectResponse)
        assert str(project.project_id) == str(project_id)
