import pytest
import aiohttp
from unittest.mock import AsyncMock, patch, create_autospec

from brightcove_async.client import BrightcoveClient


class DummyOAuth:
    def __init__(self, client_id, client_secret, session):
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = session

    async def get_access_token(self):
        return "dummy_token"

    @property
    async def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {await self.get_access_token()}"}


@pytest.mark.asyncio
async def test_context_manager_initializes_and_closes_session():
    mock_session = create_autospec(aiohttp.ClientSession, instance=True)
    mock_session.close = AsyncMock()

    with patch("aiohttp.ClientSession", return_value=mock_session):
        client = BrightcoveClient(
            cms_base_url="cms_url",
            syndication_base_url="syn_url",
            analytics_base_url="ana_url",
            client_id="id",
            client_secret="secret",
            oauth_cls=DummyOAuth,
        )

        async with client as c:
            assert c._session is mock_session
            mock_session.close.assert_not_called()

        mock_session.close.assert_awaited_once()
        assert client._session is None


@pytest.mark.asyncio
async def test_oauth_property_lazy_instantiates():
    with patch("aiohttp.ClientSession") as MockSession:
        mock_session = create_autospec(aiohttp.ClientSession, instance=True)
        MockSession.return_value = mock_session

        client = BrightcoveClient(
            cms_base_url="cms_url",
            syndication_base_url="syn_url",
            analytics_base_url="ana_url",
            client_id="id",
            client_secret="secret",
            oauth_cls=DummyOAuth,
        )
        async with client as c:
            assert c._oauth is None
            oauth = c.oauth
            assert isinstance(oauth, DummyOAuth)
            assert c._oauth is oauth


@pytest.mark.asyncio
async def test_services_are_lazy_loaded_and_singleton():
    with (
        patch("aiohttp.ClientSession") as MockSession,
        patch("brightcove_async.services.cms.CMS") as MockCMS,
        patch("brightcove_async.services.syndication.Syndication") as MockSyndication,
        patch("brightcove_async.services.analytics.Analytics") as MockAnalytics,
    ):
        mock_session = create_autospec(aiohttp.ClientSession, instance=True)
        MockSession.return_value = mock_session

        client = BrightcoveClient(
            cms_base_url="cms_url",
            syndication_base_url="syn_url",
            analytics_base_url="ana_url",
            client_id="id",
            client_secret="secret",
            oauth_cls=DummyOAuth,
        )
        async with client as c:
            cms1 = c.cms
            cms2 = c.cms
            MockCMS.assert_called_once()
            assert cms1 is cms2

            synd1 = c.syndication
            synd2 = c.syndication
            MockSyndication.assert_called_once()
            assert synd1 is synd2

            ana1 = c.analytics
            ana2 = c.analytics
            MockAnalytics.assert_called_once()
            assert ana1 is ana2


@pytest.mark.asyncio
async def test_accessing_services_without_context_manager_raises():
    client = BrightcoveClient(
        cms_base_url="cms_url",
        syndication_base_url="syn_url",
        analytics_base_url="ana_url",
        client_id="id",
        client_secret="secret",
        oauth_cls=DummyOAuth,
    )
    with pytest.raises(RuntimeError):
        _ = client.cms
    with pytest.raises(RuntimeError):
        _ = client.syndication
    with pytest.raises(RuntimeError):
        _ = client.analytics
    with pytest.raises(RuntimeError):
        _ = client.oauth
