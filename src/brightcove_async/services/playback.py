import aiohttp

from brightcove_async.exceptions import BrightcoveAuthError
from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.params import (
    PlaybackListParams,
    PlaybackManifestParams,
    PlaybackVideoParams,
    PlaybackVideosParams,
)
from brightcove_async.schemas.playback_model import (
    GetVideosResponse,
    PlaybackVideo,
    PlaylistResponse,
)
from brightcove_async.services.base import Base


class Playback(Base):
    """Brightcove Playback API service.

    The Playback API is the client-facing, read-only delivery API for videos
    and playlists. Unlike the rest of the Brightcove platform it does **not**
    use OAuth: it authenticates with an account *policy key* sent in the
    ``BCOV-Policy`` request header. Searching (the ``q`` parameter on Get
    Videos / Get Related Videos) additionally requires a *search-enabled*
    policy key, which Brightcove recommends keeping server-side only.

    Because policy keys are per-account and may differ by purpose
    (search-enabled vs. not), they are supplied per request. A default key may
    also be set once on the service::

        client.playback.policy_key = "BCpkAD..."
        video = await client.playback.get_video(account_id, video_id)

    and overridden on any individual call::

        results = await client.playback.get_videos(
            account_id, policy_key="search-enabled-key",
            params=PlaybackVideosParams(q="nature"),
        )

    The OAuth client passed in by the registry is accepted for a uniform
    construction signature but is never used.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 10,
        policy_key: str | None = None,
    ) -> None:
        super().__init__(session=session, oauth=oauth, base_url=base_url, limit=limit)
        self._policy_key = policy_key

    @property
    def policy_key(self) -> str | None:
        """Default policy key used when a method is called without one."""
        return self._policy_key

    @policy_key.setter
    def policy_key(self, value: str | None) -> None:
        self._policy_key = value

    def _policy_headers(self, policy_key: str | None) -> dict[str, str]:
        """Build the ``BCOV-Policy`` auth header, resolving the default key.

        Raises:
            BrightcoveAuthError: if no policy key is supplied for the call and
                none has been set as the service default.
        """
        key = policy_key or self._policy_key
        if not key:
            raise BrightcoveAuthError(
                message=(
                    "A Playback API policy key is required. Pass policy_key=... "
                    "to the method or set client.playback.policy_key once."
                ),
                status_code=401,
            )
        return {"BCOV-Policy": key}

    def _videos_url(self, account_id: str) -> str:
        return f"{self.base_url}/accounts/{account_id}/videos"

    # ── Videos ──────────────────────────────────────────────────────────────────

    async def get_video(
        self,
        account_id: str,
        video_id: str,
        policy_key: str | None = None,
        params: PlaybackVideoParams | None = None,
    ) -> PlaybackVideo:
        """Get a single video by video id or reference id.

        To look a video up by reference id, prefix it with ``ref:`` (e.g.
        ``video_id="ref:my-reference-id"``).
        """
        return await self.fetch_data(
            endpoint=f"{self._videos_url(account_id)}/{video_id}",
            model=PlaybackVideo,
            headers=self._policy_headers(policy_key),
            params=params.serialize_params() if params else None,
        )

    async def get_videos(
        self,
        account_id: str,
        policy_key: str | None = None,
        params: PlaybackVideosParams | None = None,
    ) -> GetVideosResponse:
        """Get a page of videos, optionally filtered by a search query.

        Supplying ``params.q`` performs a search and requires a search-enabled
        policy key.
        """
        return await self.fetch_data(
            endpoint=self._videos_url(account_id),
            model=GetVideosResponse,
            headers=self._policy_headers(policy_key),
            params=params.serialize_params() if params else None,
        )

    async def get_related_videos(
        self,
        account_id: str,
        video_id: str,
        policy_key: str | None = None,
        params: PlaybackListParams | None = None,
    ) -> GetVideosResponse:
        """Get a page of videos related to the specified video."""
        return await self.fetch_data(
            endpoint=f"{self._videos_url(account_id)}/{video_id}/related",
            model=GetVideosResponse,
            headers=self._policy_headers(policy_key),
            params=params.serialize_params() if params else None,
        )

    # ── Playlists ───────────────────────────────────────────────────────────────

    async def get_playlist(
        self,
        account_id: str,
        playlist_id: str,
        policy_key: str | None = None,
        params: PlaybackListParams | None = None,
    ) -> PlaylistResponse:
        """Get a playlist by playlist id or reference id.

        Playlists may contain up to 1000 videos; by default only the first 20
        are returned. Use ``params.limit`` / ``params.offset`` to page.
        """
        return await self.fetch_data(
            endpoint=f"{self.base_url}/accounts/{account_id}/playlists/{playlist_id}",
            model=PlaylistResponse,
            headers=self._policy_headers(policy_key),
            params=params.serialize_params() if params else None,
        )

    # ── Static URLs ─────────────────────────────────────────────────────────────

    async def _get_static_manifest(
        self,
        account_id: str,
        video_id: str,
        suffix: str,
        policy_key: str | None,
        params: PlaybackManifestParams | None,
    ) -> str:
        return await self._get_text(
            endpoint=f"{self._videos_url(account_id)}/{video_id}/{suffix}",
            params=params.serialize_params() if params else None,
            headers=self._policy_headers(policy_key),
        )

    async def get_hls_manifest(
        self,
        account_id: str,
        video_id: str,
        policy_key: str | None = None,
        params: PlaybackManifestParams | None = None,
    ) -> str:
        """Get an HLS (``master.m3u8``) manifest with static rendition URLs."""
        return await self._get_static_manifest(
            account_id, video_id, "master.m3u8", policy_key, params
        )

    async def get_dash_manifest(
        self,
        account_id: str,
        video_id: str,
        policy_key: str | None = None,
        params: PlaybackManifestParams | None = None,
    ) -> str:
        """Get a DASH (``manifest.mpd``) manifest with static rendition URLs."""
        return await self._get_static_manifest(
            account_id, video_id, "manifest.mpd", policy_key, params
        )

    async def get_hls_vmap(
        self,
        account_id: str,
        video_id: str,
        policy_key: str | None = None,
        params: PlaybackManifestParams | None = None,
    ) -> str:
        """Get an HLS VMAP. Requires a JWT (``bcov_auth``) with an ``ssai`` claim."""
        return await self._get_static_manifest(
            account_id, video_id, "hls.vmap", policy_key, params
        )

    async def get_dash_vmap(
        self,
        account_id: str,
        video_id: str,
        policy_key: str | None = None,
        params: PlaybackManifestParams | None = None,
    ) -> str:
        """Get a DASH VMAP. Requires a JWT (``bcov_auth``) with an ``ssai`` claim."""
        return await self._get_static_manifest(
            account_id, video_id, "dash.vmap", policy_key, params
        )

    async def get_highest_mp4(
        self,
        account_id: str,
        video_id: str,
        policy_key: str | None = None,
        params: PlaybackManifestParams | None = None,
    ) -> bytes:
        """Get the highest-bitrate MP4 rendition as raw bytes."""
        return await self._get_bytes(
            endpoint=f"{self._videos_url(account_id)}/{video_id}/high.mp4",
            params=params.serialize_params() if params else None,
            headers=self._policy_headers(policy_key),
        )

    async def get_lowest_mp4(
        self,
        account_id: str,
        video_id: str,
        policy_key: str | None = None,
        params: PlaybackManifestParams | None = None,
    ) -> bytes:
        """Get the lowest-bitrate MP4 rendition as raw bytes."""
        return await self._get_bytes(
            endpoint=f"{self._videos_url(account_id)}/{video_id}/low.mp4",
            params=params.serialize_params() if params else None,
            headers=self._policy_headers(policy_key),
        )
