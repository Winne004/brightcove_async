from typing import ClassVar, Self, cast

import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.services.analytics import Analytics
from brightcove_async.services.base import Base
from brightcove_async.services.cms import CMS
from brightcove_async.services.syndication import Syndication


class BrightcoveClient:
    _service_classes: ClassVar[dict[str, type[Base]]] = {
        "cms": CMS,
        "syndication": Syndication,
        "analytics": Analytics,
    }

    def __init__(
        self,
        cms_base_url: str,
        syndication_base_url: str,
        analytics_base_url: str,
        client_id: str,
        client_secret: str,
        oauth_cls: type[OAuthClientProtocol],
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._oauth_cls = oauth_cls
        self._cms_base_url = cms_base_url
        self._syndication_base_url = syndication_base_url
        self._analytics_base_url = analytics_base_url
        self._session: aiohttp.ClientSession | None = session
        self._external_session = session
        self._oauth: OAuthClientProtocol | None = None
        self._client_id = client_id
        self._client_secret = client_secret
        self._services: dict[str, Base] = {}

    @property
    def oauth(self) -> OAuthClientProtocol:
        if self._session is None:
            raise RuntimeError(
                "Client session not initialized. Use as an async context manager."
            )
        if self._oauth is None:
            self._oauth = self._oauth_cls(
                client_id=self._client_id,
                client_secret=self._client_secret,
                session=self._session,
            )
        return self._oauth

    def _get_service(self, name: str, base_url: str) -> Base:
        if name not in self._services:
            service_cls = self._service_classes[name]
            if self._session is None:
                raise RuntimeError(
                    "Client session not initialized. Use as an async context manager."
                )
            self._services[name] = service_cls(self._session, self.oauth, base_url)
        return self._services[name]

    @property
    def cms(self) -> CMS:
        return cast("CMS", self._get_service("cms", self._cms_base_url))

    @property
    def syndication(self) -> Syndication:
        return cast(
            "Syndication", self._get_service("syndication", self._syndication_base_url)
        )

    @property
    def analytics(self) -> Analytics:
        return cast(
            "Analytics", self._get_service("analytics", self._analytics_base_url)
        )

    async def __aenter__(self) -> Self:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=100)
            )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session and not self._external_session:
            await self._session.close()
            self._session = None
        self._services.clear()
        self._oauth = None
