from unittest.mock import AsyncMock, create_autospec, patch

import aiohttp
import pytest

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
    from brightcove_async.registry import ServiceConfig
    from brightcove_async.services.cms import CMS

    services_registry = {
        "cms": ServiceConfig(cls=CMS, base_url="cms_url", requests_per_second=4),
    }

    mock_session = create_autospec(aiohttp.ClientSession, instance=True)
    mock_session.close = AsyncMock()

    with patch("aiohttp.ClientSession", return_value=mock_session):
        client = BrightcoveClient(
            services_registry=services_registry,
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
    from brightcove_async.registry import ServiceConfig
    from brightcove_async.services.cms import CMS

    services_registry = {
        "cms": ServiceConfig(cls=CMS, base_url="cms_url", requests_per_second=4),
    }

    with patch("aiohttp.ClientSession") as MockSession:
        mock_session = AsyncMock()
        MockSession.return_value = mock_session

        client = BrightcoveClient(
            services_registry=services_registry,
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
    from brightcove_async.registry import ServiceConfig
    from brightcove_async.services.analytics import Analytics
    from brightcove_async.services.cms import CMS
    from brightcove_async.services.syndication import Syndication

    services_registry = {
        "cms": ServiceConfig(cls=CMS, base_url="cms_url", requests_per_second=4),
        "syndication": ServiceConfig(cls=Syndication, base_url="syn_url"),
        "analytics": ServiceConfig(cls=Analytics, base_url="ana_url"),
    }

    with (
        patch("aiohttp.ClientSession") as MockSession,
        patch(
            "brightcove_async.services.cms.CMS.__init__",
            return_value=None,
        ) as MockCMS,
        patch(
            "brightcove_async.services.syndication.Syndication.__init__",
            return_value=None,
        ) as MockSyndication,
        patch(
            "brightcove_async.services.analytics.Analytics.__init__",
            return_value=None,
        ) as MockAnalytics,
    ):
        mock_session = AsyncMock()
        MockSession.return_value = mock_session

        client = BrightcoveClient(
            services_registry=services_registry,
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
    from brightcove_async.registry import ServiceConfig
    from brightcove_async.services.analytics import Analytics
    from brightcove_async.services.cms import CMS
    from brightcove_async.services.syndication import Syndication

    services_registry = {
        "cms": ServiceConfig(cls=CMS, base_url="cms_url", requests_per_second=4),
        "syndication": ServiceConfig(cls=Syndication, base_url="syn_url"),
        "analytics": ServiceConfig(cls=Analytics, base_url="ana_url"),
    }

    client = BrightcoveClient(
        services_registry=services_registry,
        client_id="id",
        client_secret="secret",
        oauth_cls=DummyOAuth,
    )
    with pytest.raises(RuntimeError, match="Client session not initialized"):
        _ = client.cms
    with pytest.raises(RuntimeError, match="Client session not initialized"):
        _ = client.syndication
    with pytest.raises(RuntimeError, match="Client session not initialized"):
        _ = client.analytics
    with pytest.raises(RuntimeError, match="Client session not initialized"):
        _ = client.oauth


@pytest.mark.asyncio
async def test_client_with_external_session():
    """Test client with externally provided session."""
    from brightcove_async.registry import ServiceConfig
    from brightcove_async.services.cms import CMS

    services_registry = {
        "cms": ServiceConfig(cls=CMS, base_url="cms_url", requests_per_second=4),
    }

    external_session = create_autospec(aiohttp.ClientSession, instance=True)
    external_session.close = AsyncMock()

    client = BrightcoveClient(
        services_registry=services_registry,
        client_id="id",
        client_secret="secret",
        oauth_cls=DummyOAuth,
        session=external_session,
    )

    async with client as c:
        assert c._session is external_session
        assert c._external_session is external_session

    # External session should NOT be closed
    external_session.close.assert_not_called()


@pytest.mark.asyncio
async def test_client_aexit_clears_services_and_oauth():
    """Test that __aexit__ clears services and oauth."""
    from brightcove_async.registry import ServiceConfig
    from brightcove_async.services.cms import CMS

    services_registry = {
        "cms": ServiceConfig(cls=CMS, base_url="cms_url", requests_per_second=4),
    }

    with patch("aiohttp.ClientSession") as MockSession:
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()
        MockSession.return_value = mock_session

        client = BrightcoveClient(
            services_registry=services_registry,
            client_id="id",
            client_secret="secret",
            oauth_cls=DummyOAuth,
        )

        async with client as c:
            _ = c.oauth  # Initialize OAuth
            _ = c.cms  # Initialize service
            assert c._oauth is not None
            assert len(c._services) > 0

        # After exit, should be cleared
        assert client._oauth is None
        assert len(client._services) == 0


@pytest.mark.asyncio
async def test_get_service_returns_same_instance():
    """Test _get_service returns singleton instances."""
    from brightcove_async.registry import ServiceConfig
    from brightcove_async.services.cms import CMS

    services_registry = {
        "cms": ServiceConfig(cls=CMS, base_url="cms_url", requests_per_second=4),
    }

    with patch("aiohttp.ClientSession") as MockSession:
        mock_session = AsyncMock()
        MockSession.return_value = mock_session

        client = BrightcoveClient(
            services_registry=services_registry,
            client_id="id",
            client_secret="secret",
            oauth_cls=DummyOAuth,
        )

        async with client as c:
            service1 = c._get_service("cms", CMS)
            service2 = c._get_service("cms", CMS)

            assert service1 is service2


@pytest.mark.asyncio
async def test_client_getattr_dynamic_service_access():
    """Test __getattr__ allows dynamic service access."""
    from brightcove_async.registry import ServiceConfig
    from brightcove_async.services.analytics import Analytics
    from brightcove_async.services.cms import CMS

    services_registry = {
        "cms": ServiceConfig(cls=CMS, base_url="cms_url", requests_per_second=4),
        "analytics": ServiceConfig(cls=Analytics, base_url="ana_url"),
    }

    with patch("aiohttp.ClientSession") as MockSession:
        mock_session = AsyncMock()
        MockSession.return_value = mock_session

        client = BrightcoveClient(
            services_registry=services_registry,
            client_id="id",
            client_secret="secret",
            oauth_cls=DummyOAuth,
        )

        async with client as c:
            cms = c.cms
            analytics = c.analytics

            assert cms is not None
            assert analytics is not None
            assert cms is not analytics


@pytest.mark.asyncio
async def test_client_reentry_creates_new_session():
    """Test that re-entering context manager creates new session."""
    from brightcove_async.registry import ServiceConfig
    from brightcove_async.services.cms import CMS

    services_registry = {
        "cms": ServiceConfig(cls=CMS, base_url="cms_url", requests_per_second=4),
    }

    with patch("aiohttp.ClientSession") as MockSession:
        sessions = []

        def create_session(*args, **kwargs):
            session = AsyncMock()
            session.close = AsyncMock()
            sessions.append(session)
            return session

        MockSession.side_effect = create_session

        client = BrightcoveClient(
            services_registry=services_registry,
            client_id="id",
            client_secret="secret",
            oauth_cls=DummyOAuth,
        )

        async with client as c1:
            first_session = c1._session

        async with client as c2:
            second_session = c2._session

        assert first_session is not second_session
        assert len(sessions) == 2
        sessions[0].close.assert_awaited_once()
        sessions[1].close.assert_awaited_once()
