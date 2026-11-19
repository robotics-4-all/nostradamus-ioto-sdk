"""Fixtures for live integration tests.

These tests talk to a real Nostradamus API deployment. They are skipped
unless credentials are supplied through the environment:

    NOSTRADAMUS_API_KEY                           API key auth (preferred)
    NOSTRADAMUS_USERNAME + NOSTRADAMUS_PASSWORD   OAuth2 password grant
    NOSTRADAMUS_BASE_URL                          Optional API base URL
    NOSTRADAMUS_PROJECT_ID                        Optional project for
                                                  project-scoped tests
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import pytest

from nostradamus_ioto_sdk import AsyncNostradamusClient, NostradamusClient

DEFAULT_BASE_URL = "https://nostradamus-ioto.issel.ee.auth.gr"


def _credentials() -> dict[str, str]:
    """Return client constructor kwargs, or an empty dict when unset."""
    api_key = os.getenv("NOSTRADAMUS_API_KEY")
    if api_key:
        return {"api_key": api_key}

    username = os.getenv("NOSTRADAMUS_USERNAME")
    password = os.getenv("NOSTRADAMUS_PASSWORD")
    if username and password:
        return {"username": username, "password": password}

    return {}


@pytest.fixture(scope="session")
def live_base_url() -> str:
    """API base URL for live tests."""
    return os.getenv("NOSTRADAMUS_BASE_URL", DEFAULT_BASE_URL)


@pytest.fixture(scope="session")
def live_credentials() -> dict[str, str]:
    """Credentials for live tests, skipping when none are configured."""
    credentials = _credentials()
    if not credentials:
        pytest.skip(
            "live credentials not set: export NOSTRADAMUS_API_KEY or "
            "NOSTRADAMUS_USERNAME/NOSTRADAMUS_PASSWORD"
        )
    return credentials


@pytest.fixture(scope="session")
def live_client(
    live_credentials: dict[str, str], live_base_url: str
) -> Iterator[NostradamusClient]:
    """Authenticated synchronous client for live tests."""
    with NostradamusClient(
        base_url=live_base_url, timeout=30.0, **live_credentials
    ) as client:
        yield client


@pytest.fixture
async def live_async_client(
    live_credentials: dict[str, str], live_base_url: str
) -> AsyncIterator[AsyncNostradamusClient]:
    """Authenticated asynchronous client for live tests."""
    async with AsyncNostradamusClient(
        base_url=live_base_url, timeout=30.0, **live_credentials
    ) as client:
        yield client
