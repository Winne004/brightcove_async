from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.syndication_model import (
    Syndication as SyndicationModel,
)
from brightcove_async.schemas.syndication_model import (
    SyndicationList,
    Type,
)
from brightcove_async.services.syndication import Syndication


class DummyOAuth:
    """Dummy OAuth class for testing."""

    async def get_access_token(self):
        return "test_token"

    @property
    async def headers(self):
        return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_session():
    """Create a mock aiohttp.ClientSession."""
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture
def dummy_oauth():
    """Create a dummy OAuth client."""
    return DummyOAuth()


@pytest.fixture
def syndication_service(mock_session, dummy_oauth):
    """Create a Syndication service instance for testing."""
    return Syndication(
        session=mock_session,
        oauth=dummy_oauth,
        base_url="https://edge.social.api.brightcove.com/v1/accounts/",
        limit=10,
    )


def test_syndication_initialization(syndication_service):
    """Test Syndication service initializes with correct parameters."""
    assert syndication_service._limit == 10
    assert (
        syndication_service.base_url
        == "https://edge.social.api.brightcove.com/v1/accounts/"
    )


@pytest.mark.asyncio
async def test_get_all_syndications(syndication_service):
    """Test get_all_syndications method."""
    with patch.object(
        syndication_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        mock_fetch.return_value = SyndicationList(root=[])

        await syndication_service.get_all_syndications("account123")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "mrss/syndications" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == SyndicationList


@pytest.mark.asyncio
async def test_get_syndication(syndication_service):
    """Test get_syndication method."""
    with patch.object(
        syndication_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        mock_fetch.return_value = SyndicationModel(name="Test", type=Type.google)

        await syndication_service.get_syndication(
            "account123",
            "syndication456",
        )

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "syndication456" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == SyndicationModel


def test_base_url_property(syndication_service):
    """Test base_url property returns correct URL."""
    assert (
        syndication_service.base_url
        == "https://edge.social.api.brightcove.com/v1/accounts/"
    )
