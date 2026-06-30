from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from brightcove_async.exceptions import BrightcoveAuthError
from brightcove_async.schemas.params import (
    PlaybackListParams,
    PlaybackManifestParams,
    PlaybackVideosParams,
)
from brightcove_async.schemas.playback_model import (
    GetVideosResponse,
    PlaybackVideo,
    PlaylistResponse,
)
from brightcove_async.services.playback import Playback

BASE_URL = "https://edge.api.brightcove.com/playback/v1"
POLICY_KEY = "BCpkADtest_policy_key"


class DummyOAuth:
    async def get_access_token(self):
        return "test_token"

    def invalidate_token(self) -> None:
        pass

    @property
    async def headers(self):
        return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_session():
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture
def playback_service(mock_session):
    return Playback(
        session=mock_session,
        oauth=DummyOAuth(),
        base_url=BASE_URL,
        limit=10,
    )


def _json_response(mock_session, payload):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = AsyncMock(return_value=payload)
    mock_session.request.return_value.__aenter__.return_value = mock_response
    return mock_response


def _text_response(mock_session, text):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.text = AsyncMock(return_value=text)
    mock_session.request.return_value.__aenter__.return_value = mock_response
    return mock_response


def _bytes_response(mock_session, data):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=data)
    mock_session.request.return_value.__aenter__.return_value = mock_response
    return mock_response


# ── Construction / policy key handling ────────────────────────────────────────


def test_playback_initialization(playback_service):
    assert playback_service._limit == 10
    assert playback_service.base_url == BASE_URL
    assert playback_service.policy_key is None


def test_policy_key_property_round_trip(playback_service):
    playback_service.policy_key = POLICY_KEY
    assert playback_service.policy_key == POLICY_KEY
    assert playback_service._policy_headers(None) == {"BCOV-Policy": POLICY_KEY}


def test_per_call_policy_key_overrides_default(playback_service):
    playback_service.policy_key = "default-key"
    assert playback_service._policy_headers("override-key") == {
        "BCOV-Policy": "override-key"
    }


def test_missing_policy_key_raises(playback_service):
    with pytest.raises(BrightcoveAuthError, match="policy key is required"):
        playback_service._policy_headers(None)


@pytest.mark.asyncio
async def test_missing_policy_key_raises_before_request(playback_service, mock_session):
    with pytest.raises(BrightcoveAuthError):
        await playback_service.get_video("acct", "vid")
    mock_session.request.assert_not_called()


def test_constructor_accepts_default_policy_key(mock_session):
    service = Playback(
        session=mock_session,
        oauth=DummyOAuth(),
        base_url=BASE_URL,
        policy_key=POLICY_KEY,
    )
    assert service.policy_key == POLICY_KEY


# ── Videos ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_video_sends_policy_header_and_parses(playback_service, mock_session):
    _json_response(mock_session, {"id": "vid123", "name": "My Video"})

    result = await playback_service.get_video(
        "acct123", "vid123", policy_key=POLICY_KEY
    )

    assert isinstance(result, PlaybackVideo)
    assert result.id == "vid123"
    assert result.name == "My Video"

    call = mock_session.request.call_args
    assert call.args[0] == "GET"
    assert call.args[1] == f"{BASE_URL}/accounts/acct123/videos/vid123"
    assert call.kwargs["headers"] == {"BCOV-Policy": POLICY_KEY}


@pytest.mark.asyncio
async def test_get_video_supports_reference_id(playback_service, mock_session):
    _json_response(mock_session, {"id": "vid123"})

    await playback_service.get_video("acct123", "ref:my-ref", policy_key=POLICY_KEY)

    call = mock_session.request.call_args
    assert call.args[1] == f"{BASE_URL}/accounts/acct123/videos/ref:my-ref"


@pytest.mark.asyncio
async def test_get_video_uses_default_policy_key(playback_service, mock_session):
    playback_service.policy_key = POLICY_KEY
    _json_response(mock_session, {"id": "vid123"})

    await playback_service.get_video("acct123", "vid123")

    call = mock_session.request.call_args
    assert call.kwargs["headers"] == {"BCOV-Policy": POLICY_KEY}


@pytest.mark.asyncio
async def test_get_videos_serializes_search_params(playback_service, mock_session):
    _json_response(mock_session, [{"id": "a"}, {"id": "b"}])

    params = PlaybackVideosParams(q="nature", limit=10, offset=5)
    result = await playback_service.get_videos(
        "acct123", policy_key=POLICY_KEY, params=params
    )

    assert isinstance(result, GetVideosResponse)
    assert len(result) == 2
    assert [v.id for v in result] == ["a", "b"]

    call = mock_session.request.call_args
    assert call.args[1] == f"{BASE_URL}/accounts/acct123/videos"
    assert call.kwargs["params"] == {"q": "nature", "limit": 10, "offset": 5}


@pytest.mark.asyncio
async def test_get_related_videos(playback_service, mock_session):
    _json_response(mock_session, [{"id": "rel1"}])

    result = await playback_service.get_related_videos(
        "acct123", "vid123", policy_key=POLICY_KEY, params=PlaybackListParams(limit=3)
    )

    assert result[0].id == "rel1"
    call = mock_session.request.call_args
    assert call.args[1] == f"{BASE_URL}/accounts/acct123/videos/vid123/related"
    assert call.kwargs["params"] == {"limit": 3}


# ── Playlists ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_playlist_parses_videos(playback_service, mock_session):
    _json_response(
        mock_session,
        {
            "id": "pl1",
            "name": "My Playlist",
            "type": "EXPLICIT",
            "videos": [{"id": "vid1"}, {"id": "vid2"}],
        },
    )

    result = await playback_service.get_playlist(
        "acct123", "pl1", policy_key=POLICY_KEY
    )

    assert isinstance(result, PlaylistResponse)
    assert result.id == "pl1"
    assert result.videos is not None
    assert [v.id for v in result.videos] == ["vid1", "vid2"]
    call = mock_session.request.call_args
    assert call.args[1] == f"{BASE_URL}/accounts/acct123/playlists/pl1"


# ── Static URLs ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_hls_manifest_returns_text_with_jwt_param(
    playback_service, mock_session
):
    _text_response(mock_session, "#EXTM3U\n...")

    result = await playback_service.get_hls_manifest(
        "acct123",
        "vid123",
        policy_key=POLICY_KEY,
        params=PlaybackManifestParams(bcov_auth="jwt-token"),
    )

    assert result.startswith("#EXTM3U")
    call = mock_session.request.call_args
    assert call.args[1] == f"{BASE_URL}/accounts/acct123/videos/vid123/master.m3u8"
    assert call.kwargs["headers"] == {"BCOV-Policy": POLICY_KEY}
    assert call.kwargs["params"] == {"bcov_auth": "jwt-token"}


@pytest.mark.asyncio
async def test_get_dash_manifest_endpoint(playback_service, mock_session):
    _text_response(mock_session, "<MPD></MPD>")

    await playback_service.get_dash_manifest("acct", "vid", policy_key=POLICY_KEY)

    call = mock_session.request.call_args
    assert call.args[1] == f"{BASE_URL}/accounts/acct/videos/vid/manifest.mpd"


@pytest.mark.asyncio
async def test_vmap_endpoints(playback_service, mock_session):
    _text_response(mock_session, "<vmap></vmap>")
    await playback_service.get_hls_vmap("acct", "vid", policy_key=POLICY_KEY)
    assert (
        mock_session.request.call_args.args[1]
        == f"{BASE_URL}/accounts/acct/videos/vid/hls.vmap"
    )

    _text_response(mock_session, "<vmap></vmap>")
    await playback_service.get_dash_vmap("acct", "vid", policy_key=POLICY_KEY)
    assert (
        mock_session.request.call_args.args[1]
        == f"{BASE_URL}/accounts/acct/videos/vid/dash.vmap"
    )


@pytest.mark.asyncio
async def test_mp4_endpoints_return_bytes(playback_service, mock_session):
    _bytes_response(mock_session, b"mp4-bytes")
    high = await playback_service.get_highest_mp4("acct", "vid", policy_key=POLICY_KEY)
    assert high == b"mp4-bytes"
    assert (
        mock_session.request.call_args.args[1]
        == f"{BASE_URL}/accounts/acct/videos/vid/high.mp4"
    )

    _bytes_response(mock_session, b"mp4-bytes-low")
    low = await playback_service.get_lowest_mp4("acct", "vid", policy_key=POLICY_KEY)
    assert low == b"mp4-bytes-low"
    assert (
        mock_session.request.call_args.args[1]
        == f"{BASE_URL}/accounts/acct/videos/vid/low.mp4"
    )


# ── Param serialization ───────────────────────────────────────────────────────


def test_playback_videos_params_omit_none():
    params = PlaybackVideosParams(q="dog")
    assert params.serialize_params() == {"q": "dog"}


def test_playback_manifest_params_serialization():
    params = PlaybackManifestParams(bcov_auth="jwt", config_id="cfg")
    assert params.serialize_params() == {"bcov_auth": "jwt", "config_id": "cfg"}
