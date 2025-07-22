from typing import Literal, Self, overload

import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.registry import ServiceConfig
from brightcove_async.services.analytics import Analytics
from brightcove_async.services.base import Base
from brightcove_async.services.cms import CMS
from brightcove_async.services.dynamic_ingest import DynamicIngest
from brightcove_async.services.syndication import Syndication


class BrightcoveClient:
    def __init__(
        self,
        services_registry: dict[str, ServiceConfig],
        client_id: str,
        client_secret: str,
        oauth_cls: type[OAuthClientProtocol],
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._oauth_cls = oauth_cls
        self._service_classes = services_registry
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
                "Client session not initialized. Use as an async context manager.",
            )
        if self._oauth is None:
            self._oauth = self._oauth_cls(
                client_id=self._client_id,
                client_secret=self._client_secret,
                session=self._session,
            )
        return self._oauth

    def _get_service(self, name) -> Base:
        if name not in self._services:
            service_cls = self._service_classes[name]
            if self._session is None:
                raise RuntimeError(
                    "Client session not initialized. Use as an async context manager.",
                )
            self._services[name] = service_cls.cls(
                self._session,
                self.oauth,
                service_cls.base_url,
                limit=service_cls.requests_per_second,
            )
        return self._services[name]

    @overload  # type: ignore[misc]
    def __getattr__(self, name: Literal["cms"]) -> CMS: ...
    @overload  # type: ignore[misc]
    def __getattr__(self, name: Literal["syndication"]) -> Syndication: ...
    @overload  # type: ignore[misc]
    def __getattr__(self, name: Literal["analytics"]) -> Analytics: ...
    @overload  # type: ignore[misc]
    def __getattr__(self, name: Literal["dynamic_ingest"]) -> DynamicIngest: ...
    @overload  # type: ignore[misc]
    def __getattr__(self, name: str) -> Base: ...

    def __getattr__(self, name: str) -> Base:
        return self._get_service(name)

    async def __aenter__(self) -> Self:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=100),
            )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session and not self._external_session:
            await self._session.close()
            self._session = None
        self._services.clear()
        self._oauth = None
