"""Shared fixtures for all test modules."""

from unittest.mock import AsyncMock

import aiohttp
import pytest


class DummyOAuth:
    """Dummy OAuth class satisfying OAuthClientProtocol for testing."""

    def __init__(
        self,
        client_id: str = "test_client_id",
        client_secret: str = "test_secret",
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = session

    async def get_access_token(self) -> str:
        return "test_token"

    @property
    async def headers(self) -> dict[str, str]:
        return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock aiohttp.ClientSession."""
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture
def dummy_oauth() -> DummyOAuth:
    """Create a dummy OAuth client."""
    return DummyOAuth()
