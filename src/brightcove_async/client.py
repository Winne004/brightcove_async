from importlib.metadata import PackageNotFoundError, version
from typing import Self, TypeVar, cast

import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.registry import ServiceConfig
from brightcove_async.services.analytics import Analytics
from brightcove_async.services.audience import Audience
from brightcove_async.services.base import Base
from brightcove_async.services.cms import CMS
from brightcove_async.services.dynamic_ingest import DynamicIngest
from brightcove_async.services.images import Images
from brightcove_async.services.ingest_profiles import IngestProfiles
from brightcove_async.services.live import Live
from brightcove_async.services.playback import Playback
from brightcove_async.services.policy import Policy
from brightcove_async.services.syndication import Syndication

T = TypeVar("T", bound=Base)

try:
    _CLIENT_VERSION = version("brightcove_async")
except PackageNotFoundError:
    _CLIENT_VERSION = "unknown"

# Akamai (fronting Brightcove APIs) blocks the default aiohttp User-Agent as bot
# traffic, returning an errors.edgesuite.net page.
_USER_AGENT = f"brightcove_async/{_CLIENT_VERSION}"


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
        self._entry_count = 0

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

    def _get_service(self, name: str, service_type: type[T]) -> T:
        """Lazy-load and cache a service instance by name.

        Args:
            name: The service name in the registry
            service_type: The expected service class type

        Returns:
            The cached or newly created service instance
        """
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
        # Cast is safe because the registry maps service names to their correct types
        return cast(T, self._services[name])

    @property
    def cms(self) -> CMS:
        """Access the CMS (Content Management System) API service."""
        return self._get_service("cms", CMS)

    @property
    def analytics(self) -> Analytics:
        """Access the Analytics API service."""
        return self._get_service("analytics", Analytics)

    @property
    def syndication(self) -> Syndication:
        """Access the Syndication API service."""
        return self._get_service("syndication", Syndication)

    @property
    def dynamic_ingest(self) -> DynamicIngest:
        """Access the Dynamic Ingest API service."""
        return self._get_service("dynamic_ingest", DynamicIngest)

    @property
    def ingest_profiles(self) -> IngestProfiles:
        """Access the Ingest Profiles API service."""
        return self._get_service("ingest_profiles", IngestProfiles)

    @property
    def audience(self) -> Audience:
        """Access the Audience API service."""
        return self._get_service("audience", Audience)

    @property
    def images(self) -> Images:
        """Access the Image API service."""
        return self._get_service("images", Images)

    @property
    def live(self) -> Live:
        """Access the Live (NextGen Live) API service."""
        return self._get_service("live", Live)

    @property
    def playback(self) -> Playback:
        """Access the Playback (client-facing delivery) API service."""
        return self._get_service("playback", Playback)

    @property
    def policy(self) -> Policy:
        """Access the Policy API service."""
        return self._get_service("policy", Policy)

    async def __aenter__(self) -> Self:
        # Nested or concurrent entries share the open session; the outermost
        # exit is the one that tears it down.
        if self._entry_count > 0:
            self._entry_count += 1
            return self

        if self._external_session is not None:
            self._session = self._external_session
            # Keep any User-Agent the caller configured on their own session.
            self._session.headers.setdefault("User-Agent", _USER_AGENT)
        else:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=100),
                headers={"User-Agent": _USER_AGENT},
            )
        self._entry_count = 1
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._entry_count = max(self._entry_count - 1, 0)
        if self._entry_count > 0:
            return

        # Detach before awaiting close so an entry made during the close starts
        # clean and its new session isn't cleared when the close finishes.
        session = self._session
        self._session = None
        self._services.clear()
        self._oauth = None
        if session is not None and self._external_session is None:
            await session.close()
