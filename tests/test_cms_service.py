from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.cms_model import (
    ApproveContractFields,
    AudioTrack,
    AudioTracks,
    Channel,
    ChannelAffiliateList,
    ChannelList,
    Contract,
    ContractList,
    CreateVideoRequestBodyFields,
    CustomField,
    CustomFields,
    CustomFieldUpdate,
    DigitalMaster,
    DynamicRenditionList,
    Economics,
    Folder,
    FolderCreateFields,
    FolderList,
    FolderUpdateFields,
    ImageList,
    IngestJobs,
    IngestJobStatus,
    LabelPath,
    LabelsList,
    LabelUpdate,
    Manifest,
    ManifestList,
    Playlist,
    PlaylistArray,
    PlaylistCount,
    PlaylistInputFields,
    RemoteAssetBody,
    ShareVideoRequest,
    Subscription,
    SubscriptionCreateFields,
    SubscriptionList,
    UpdateAudioTrackFields,
    UpdateChannelFields,
    UpdateVideoRequestBodyFields,
    Video,
    VideoArray,
    VideoAsset,
    VideoAssetList,
    VideoCount,
    VideoCountInPlaylist,
    VideoFields,
    VideoShare,
    VideoShareList,
    VideoSourcesList,
    VideoVariant,
    VideoVariants,
)
from brightcove_async.schemas.params import (
    GetVideosQueryParams,
)
from brightcove_async.services.cms import CMS


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
def cms_service(mock_session, dummy_oauth):
    """Create a CMS service instance for testing."""
    return CMS(
        session=mock_session,
        oauth=dummy_oauth,
        base_url="https://cms.api.brightcove.com/v1/accounts/",
        limit=4,
    )


@pytest.mark.asyncio
async def test_cms_initialization(cms_service):
    """Test CMS service initializes with correct parameters."""
    assert cms_service._limit == 4
    assert cms_service._page_limit == 100
    assert cms_service.base_url == "https://cms.api.brightcove.com/v1/accounts/"


# ── Videos ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_videos(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoArray(root=[])
        params = GetVideosQueryParams(limit=10, offset=0)
        await cms_service.get_videos("account123", params)
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == VideoArray


@pytest.mark.asyncio
async def test_create_video(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Video(
            id="video123", name="Test Video", economics=Economics.AD_SUPPORTED
        )
        video_data = CreateVideoRequestBodyFields(name="Test Video")
        await cms_service.create_video("account123", video_data)
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["payload"] == video_data


@pytest.mark.asyncio
async def test_update_video(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Video()
        data = UpdateVideoRequestBodyFields(name="Updated")
        await cms_service.update_video("account123", "video123", data)
        call_args = mock_fetch.call_args
        assert "video123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"
        assert call_args.kwargs["model"] == Video


@pytest.mark.asyncio
async def test_delete_video(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_video("account123", ["v1", "v2"])
        mock_delete.assert_called_once()
        assert "v1,v2" in mock_delete.call_args.args[0]


@pytest.mark.asyncio
async def test_delete_video_empty_raises(cms_service):
    with pytest.raises(ValueError, match="at least one ID"):
        await cms_service.delete_video("account123", [])


@pytest.mark.asyncio
async def test_get_video_count(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoCount(count=100)
        result = await cms_service.get_video_count("account123")
        assert result.count == 100


@pytest.mark.asyncio
async def test_get_video_by_id_single(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoArray(root=[])
        await cms_service.get_video_by_id("account123", ["video123"])
        assert "video123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_video_by_id_multiple(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoArray(root=[])
        await cms_service.get_video_by_id("account123", ["video1", "video2", "video3"])
        assert "video1,video2,video3" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_video_by_id_too_many_ids(cms_service):
    with pytest.raises(ValueError, match="video_ids must contain 10 or fewer IDs"):
        await cms_service.get_video_by_id(
            "account123", [f"video{i}" for i in range(11)]
        )


@pytest.mark.asyncio
async def test_get_video_by_id_empty_list(cms_service):
    with pytest.raises(ValueError, match="video_ids must contain at least one ID"):
        await cms_service.get_video_by_id("account123", [])


@pytest.mark.asyncio
async def test_get_video_sources(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoSourcesList(root=[])
        await cms_service.get_video_sources("account123", "video123")
        assert "video123/sources" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_video_images(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        from unittest.mock import MagicMock

        mock_fetch.return_value = MagicMock(spec=ImageList)
        await cms_service.get_video_images("account123", "video123")
        assert "video123/images" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_delete_video_image(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_video_image("account123", "video123", "poster")
        assert "image_sources/poster" in mock_delete.call_args.args[0]


@pytest.mark.asyncio
async def test_get_clear_video(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Video()
        await cms_service.get_clear_video("account123", "video123")
        assert "clear_videos/video123" in mock_fetch.call_args.kwargs["endpoint"]
        assert mock_fetch.call_args.kwargs["model"] == Video


@pytest.mark.asyncio
async def test_get_video_clear_sources(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoSourcesList(root=[])
        await cms_service.get_video_clear_sources("account123", "video123")
        assert "clear_sources" in mock_fetch.call_args.kwargs["endpoint"]
        assert mock_fetch.call_args.kwargs["model"] == VideoSourcesList


# ── Video Variants ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_video_variants(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoVariants(root=[])
        await cms_service.get_video_variants("account123", "video123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_create_video_variant(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoVariant()
        data = VideoVariant(language="es-ES", name="Nombre")
        await cms_service.create_video_variant("account123", "video123", data)
        call_args = mock_fetch.call_args
        assert "variants" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_video_variant(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoVariant()
        await cms_service.get_video_variant("account123", "video123", "variant123")
        assert "variant123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_video_variant(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoVariant()
        data = VideoVariant(name="Updated")
        await cms_service.update_video_variant("account123", "video123", "es-ES", data)
        call_args = mock_fetch.call_args
        assert "es-ES" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_video_variant(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_video_variant("account123", "video123", "es-ES")
        assert "es-ES" in mock_delete.call_args.args[0]


# ── Audio Tracks ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_video_audio_tracks(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = AudioTracks(root=[])
        await cms_service.get_video_audio_tracks("account123", "video123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_video_audio_track(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = AudioTrack()
        await cms_service.get_video_audio_track("account123", "video123", "track123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_update_video_audio_track(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = AudioTrack()
        data = UpdateAudioTrackFields(is_default=True)
        await cms_service.update_video_audio_track(
            "account123", "video123", "track123", data
        )
        call_args = mock_fetch.call_args
        assert "track123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_video_audio_track(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_video_audio_track("account123", "video123", "track123")
        assert "track123" in mock_delete.call_args.args[0]


# ── Digital Master ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_digital_master_info(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = DigitalMaster()
        await cms_service.get_digital_master_info("account123", "video123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_delete_digital_master(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_digital_master("account123", "video123")
        assert "digital_master" in mock_delete.call_args.args[0]


# ── Ingest Jobs ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_status_of_ingest_jobs(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = IngestJobs(root=[])
        await cms_service.get_status_of_ingest_jobs("account123", "video123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_ingest_job_status(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = IngestJobStatus()
        await cms_service.get_ingest_job_status("account123", "video123", "job123")
        assert "job123" in mock_fetch.call_args.kwargs["endpoint"]


# ── Playlist References ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_playlists_for_video(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Playlist()
        await cms_service.get_playlists_for_video("account123", "video123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_remove_video_from_all_playlists(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.remove_video_from_all_playlists("account123", "video123")
        assert "references" in mock_delete.call_args.args[0]


# ── Playlists ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_playlists(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = PlaylistArray(root=[])
        await cms_service.get_playlists("account123")
        call_args = mock_fetch.call_args
        assert "playlists" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == PlaylistArray


@pytest.mark.asyncio
async def test_create_playlist(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Playlist()
        data = PlaylistInputFields(name="My Playlist")
        await cms_service.create_playlist("account123", data)
        call_args = mock_fetch.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["model"] == Playlist


@pytest.mark.asyncio
async def test_get_playlist_count(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = PlaylistCount(count=5)
        result = await cms_service.get_playlist_count("account123")
        assert result.count == 5
        assert "counts/playlists" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_playlist(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Playlist()
        await cms_service.get_playlist("account123", "playlist123")
        assert "playlist123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_playlist(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Playlist()
        data = PlaylistInputFields(name="Updated")
        await cms_service.update_playlist("account123", "playlist123", data)
        call_args = mock_fetch.call_args
        assert "playlist123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_playlist(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_playlist("account123", "playlist123")
        assert "playlist123" in mock_delete.call_args.args[0]


@pytest.mark.asyncio
async def test_get_videos_in_playlist(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoArray(root=[])
        await cms_service.get_videos_in_playlist("account123", "playlist123")
        call_args = mock_fetch.call_args
        assert "playlist123/videos" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == VideoArray


@pytest.mark.asyncio
async def test_get_video_count_in_playlist(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoCountInPlaylist(count=3)
        result = await cms_service.get_video_count_in_playlist(
            "account123", "playlist123"
        )
        assert result.count == 3
        assert (
            "counts/playlists/playlist123/videos"
            in mock_fetch.call_args.kwargs["endpoint"]
        )


# ── Custom Fields ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_all_video_fields(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoFields()
        await cms_service.get_all_video_fields("account123")
        call_args = mock_fetch.call_args
        assert call_args.kwargs["endpoint"].endswith("video_fields")
        assert call_args.kwargs["model"] == VideoFields


@pytest.mark.asyncio
async def test_get_video_fields(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = CustomFields(root=[])
        await cms_service.get_video_fields("account123")
        assert "video_fields/custom_fields" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_create_custom_field(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = CustomField()
        data = CustomField(id="myfield", type="string")
        await cms_service.create_custom_field("account123", data)
        call_args = mock_fetch.call_args
        assert "video_fields/custom_fields" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_custom_field(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = CustomField()
        await cms_service.get_custom_field("account123", "myfield")
        assert "custom_fields/myfield" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_custom_field(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = CustomField()
        data = CustomFieldUpdate(display_name="My Field")
        await cms_service.update_custom_field("account123", "myfield", data)
        call_args = mock_fetch.call_args
        assert "custom_fields/myfield" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_custom_field(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_custom_field("account123", "myfield")
        assert "custom_fields/myfield" in mock_delete.call_args.args[0]


# ── Folders ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_folders(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = FolderList(root=[])
        await cms_service.get_folders("account123")
        call_args = mock_fetch.call_args
        assert call_args.kwargs["endpoint"].endswith("folders")
        assert call_args.kwargs["model"] == FolderList


@pytest.mark.asyncio
async def test_create_folder(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Folder()
        data = FolderCreateFields(name="My Folder")
        await cms_service.create_folder("account123", data)
        call_args = mock_fetch.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["model"] == Folder


@pytest.mark.asyncio
async def test_get_folder(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Folder()
        await cms_service.get_folder("account123", "folder123")
        assert "folders/folder123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_folder(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Folder()
        data = FolderUpdateFields(name="Renamed")
        await cms_service.update_folder("account123", "folder123", data)
        call_args = mock_fetch.call_args
        assert "folders/folder123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_folder(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_folder("account123", "folder123")
        assert "folders/folder123" in mock_delete.call_args.args[0]


@pytest.mark.asyncio
async def test_get_videos_in_folder(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoArray(root=[])
        await cms_service.get_videos_in_folder("account123", "folder123")
        assert "folder123/videos" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_add_video_to_folder(cms_service):
    with patch.object(cms_service, "_put_empty", new_callable=AsyncMock) as mock_put:
        await cms_service.add_video_to_folder("account123", "folder123", "video123")
        assert "folder123/videos/video123" in mock_put.call_args.args[0]


@pytest.mark.asyncio
async def test_remove_video_from_folder(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.remove_video_from_folder(
            "account123", "folder123", "video123"
        )
        assert "folder123/videos/video123" in mock_delete.call_args.args[0]


# ── Labels ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_labels(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = LabelsList()
        await cms_service.get_labels("account123")
        call_args = mock_fetch.call_args
        assert call_args.kwargs["endpoint"].endswith("labels")
        assert call_args.kwargs["model"] == LabelsList


@pytest.mark.asyncio
async def test_create_label(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = LabelsList()
        data = LabelPath(path="/nature/birds")
        await cms_service.create_label("account123", data)
        call_args = mock_fetch.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["model"] == LabelsList


@pytest.mark.asyncio
async def test_update_label(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = LabelsList()
        data = LabelUpdate(new_label="shorebirds")
        await cms_service.update_label("account123", "nature/birds", data)
        call_args = mock_fetch.call_args
        assert "labels/by_path/nature/birds" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_label(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_label("account123", "nature/birds")
        assert "labels/by_path/nature/birds" in mock_delete.call_args.args[0]


# ── Channels ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_channels(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ChannelList(root=[])
        await cms_service.list_channels("account123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_channel_details(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Channel()
        await cms_service.get_channel_details("account123", "channel123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_update_channel(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Channel()
        data = UpdateChannelFields(enforce_geo=True)
        await cms_service.update_channel("account123", "my_channel", data)
        call_args = mock_fetch.call_args
        assert "channels/my_channel" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"
        assert call_args.kwargs["model"] == Channel


@pytest.mark.asyncio
async def test_list_channel_affiliates(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ChannelAffiliateList(root=[])
        await cms_service.list_channel_affiliates("account123", "channel123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_add_affiliate(cms_service):
    with patch.object(cms_service, "_put_empty", new_callable=AsyncMock) as mock_put:
        await cms_service.add_affiliate("account123", "my_channel", "affiliate456")
        assert "channels/my_channel/members/affiliate456" in mock_put.call_args.args[0]


@pytest.mark.asyncio
async def test_remove_affiliate(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.remove_affiliate("account123", "my_channel", "affiliate456")
        assert (
            "channels/my_channel/members/affiliate456" in mock_delete.call_args.args[0]
        )


# ── Contracts ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_contracts(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ContractList(root=[])
        await cms_service.list_contracts("account123")
        call_args = mock_fetch.call_args
        assert call_args.kwargs["endpoint"].endswith("account123/contracts")
        assert call_args.kwargs["model"] == ContractList


@pytest.mark.asyncio
async def test_get_contract(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Contract()
        await cms_service.get_contract("account123", "master456")
        call_args = mock_fetch.call_args
        assert "contracts/master456" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == Contract


@pytest.mark.asyncio
async def test_approve_contract(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Contract()
        data = ApproveContractFields(approved=True, auto_accept=True)
        await cms_service.approve_contract("account123", "master456", data)
        call_args = mock_fetch.call_args
        assert "contracts/master456" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"
        assert call_args.kwargs["model"] == Contract


# ── Video Shares ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_shares(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoShareList(root=[])
        await cms_service.list_shares("account123", "video123")
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_share_video(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoShareList(root=[])
        data = ShareVideoRequest(id="affiliate456")
        await cms_service.share_video("account123", "video123", data)
        call_args = mock_fetch.call_args
        assert "video123/shares" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_share(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoShare(
            affiliate_id="affiliate456",
            affiliate_video_id="v999",
            video_id="video123",
        )
        await cms_service.get_share("account123", "video123", "affiliate456")
        assert "shares/affiliate456" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_unshare_video(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.unshare_video("account123", "video123", "affiliate456")
        assert "shares/affiliate456" in mock_delete.call_args.args[0]


# ── Subscriptions ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_subscriptions(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = SubscriptionList(root=[])
        await cms_service.get_subscriptions("account123")
        call_args = mock_fetch.call_args
        assert call_args.kwargs["endpoint"].endswith("subscriptions")
        assert call_args.kwargs["model"] == SubscriptionList


@pytest.mark.asyncio
async def test_create_subscription(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Subscription()
        from brightcove_async.schemas.cms_model import Event

        data = SubscriptionCreateFields(
            endpoint="https://example.com/hook",
            events=[Event.video_change],
        )
        await cms_service.create_subscription("account123", data)
        call_args = mock_fetch.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["model"] == Subscription


@pytest.mark.asyncio
async def test_get_subscription(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Subscription()
        await cms_service.get_subscription("account123", "sub123")
        assert "subscriptions/sub123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_delete_subscription(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_subscription("account123", "sub123")
        assert "subscriptions/sub123" in mock_delete.call_args.args[0]


# ── Assets ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_assets(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoAssetList(root=[])
        await cms_service.get_assets("account123", "video123")
        call_args = mock_fetch.call_args
        assert call_args.kwargs["endpoint"].endswith("assets")
        assert call_args.kwargs["model"] == VideoAssetList


@pytest.mark.asyncio
async def test_get_dynamic_renditions(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = DynamicRenditionList(root=[])
        await cms_service.get_dynamic_renditions("account123", "video123")
        assert "dynamic_renditions" in mock_fetch.call_args.kwargs["endpoint"]


# ── HLS Manifests ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_hls_manifests(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ManifestList(root=[])
        await cms_service.get_hls_manifests("account123", "video123")
        assert "hls_manifest" in mock_fetch.call_args.kwargs["endpoint"]
        assert mock_fetch.call_args.kwargs["model"] == ManifestList


@pytest.mark.asyncio
async def test_add_hls_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/manifest.m3u8")
        await cms_service.add_hls_manifest("account123", "video123", body)
        call_args = mock_fetch.call_args
        assert "hls_manifest" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_hls_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        await cms_service.get_hls_manifest("account123", "video123", "asset123")
        assert "hls_manifest/asset123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_hls_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/new.m3u8")
        await cms_service.update_hls_manifest(
            "account123", "video123", "asset123", body
        )
        call_args = mock_fetch.call_args
        assert "hls_manifest/asset123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_hls_manifest(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_hls_manifest("account123", "video123", "asset123")
        assert "hls_manifest/asset123" in mock_delete.call_args.args[0]


# ── DASH Manifests ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_dash_manifests(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ManifestList(root=[])
        await cms_service.get_dash_manifests("account123", "video123")
        assert "dash_manifests" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_add_dash_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/manifest.mpd")
        await cms_service.add_dash_manifest("account123", "video123", body)
        assert mock_fetch.call_args.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_dash_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        await cms_service.get_dash_manifest("account123", "video123", "asset123")
        assert "dash_manifests/asset123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_dash_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/new.mpd")
        await cms_service.update_dash_manifest(
            "account123", "video123", "asset123", body
        )
        assert mock_fetch.call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_dash_manifest(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_dash_manifest("account123", "video123", "asset123")
        assert "dash_manifests/asset123" in mock_delete.call_args.args[0]


# ── HDS Manifests ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_hds_manifests(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ManifestList(root=[])
        await cms_service.get_hds_manifests("account123", "video123")
        assert "hds_manifest" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_add_hds_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/manifest.f4m")
        await cms_service.add_hds_manifest("account123", "video123", body)
        assert mock_fetch.call_args.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_hds_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        await cms_service.get_hds_manifest("account123", "video123", "asset123")
        assert "hds_manifest/asset123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_hds_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/new.f4m")
        await cms_service.update_hds_manifest(
            "account123", "video123", "asset123", body
        )
        assert mock_fetch.call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_hds_manifest(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_hds_manifest("account123", "video123", "asset123")
        assert "hds_manifest/asset123" in mock_delete.call_args.args[0]


# ── ISM Manifests ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_ism_manifests(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ManifestList(root=[])
        await cms_service.get_ism_manifests("account123", "video123")
        assert "ism_manifest" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_add_ism_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/manifest.ism")
        await cms_service.add_ism_manifest("account123", "video123", body)
        assert mock_fetch.call_args.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_ism_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        await cms_service.get_ism_manifest("account123", "video123", "asset123")
        assert "ism_manifest/asset123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_ism_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/new.ism")
        await cms_service.update_ism_manifest(
            "account123", "video123", "asset123", body
        )
        assert mock_fetch.call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_ism_manifest(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_ism_manifest("account123", "video123", "asset123")
        assert "ism_manifest/asset123" in mock_delete.call_args.args[0]


# ── ISMC Manifests ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_ismc_manifests(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ManifestList(root=[])
        await cms_service.get_ismc_manifests("account123", "video123")
        assert "ismc_manifest" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_add_ismc_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/manifest.ismc")
        await cms_service.add_ismc_manifest("account123", "video123", body)
        assert mock_fetch.call_args.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_ismc_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        await cms_service.get_ismc_manifest("account123", "video123", "asset123")
        assert "ismc_manifest/asset123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_ismc_manifest(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Manifest()
        body = RemoteAssetBody(remote_url="https://example.com/new.ismc")
        await cms_service.update_ismc_manifest(
            "account123", "video123", "asset123", body
        )
        assert mock_fetch.call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_ismc_manifest(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_ismc_manifest("account123", "video123", "asset123")
        assert "ismc_manifest/asset123" in mock_delete.call_args.args[0]


# ── Renditions ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_add_rendition(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoAsset()
        body = RemoteAssetBody(remote_url="https://example.com/video.mp4")
        await cms_service.add_rendition("account123", "video123", body)
        call_args = mock_fetch.call_args
        assert "renditions" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["model"] == VideoAsset


@pytest.mark.asyncio
async def test_get_rendition(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoAsset()
        await cms_service.get_rendition("account123", "video123", "asset123")
        assert "renditions/asset123" in mock_fetch.call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_update_rendition(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoAsset()
        body = RemoteAssetBody(remote_url="https://example.com/new.mp4")
        await cms_service.update_rendition("account123", "video123", "asset123", body)
        call_args = mock_fetch.call_args
        assert "renditions/asset123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"


@pytest.mark.asyncio
async def test_delete_rendition(cms_service):
    with patch.object(cms_service, "_delete", new_callable=AsyncMock) as mock_delete:
        await cms_service.delete_rendition("account123", "video123", "asset123")
        assert "renditions/asset123" in mock_delete.call_args.args[0]


# ── Paginated helpers ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_videos_for_account_pagination(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoArray(root=[])
        await cms_service.get_videos_for_account(
            "account123", page_size=25, number_of_pages=2
        )
        assert mock_fetch.call_count == 2


@pytest.mark.asyncio
async def test_get_videos_for_account_skips_count_when_pages_provided(cms_service):
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoArray(root=[])
        with patch.object(
            cms_service, "get_video_count", new_callable=AsyncMock
        ) as mock_count:
            await cms_service.get_videos_for_account(
                "account123", page_size=25, number_of_pages=2
            )
            mock_count.assert_not_called()
            assert mock_fetch.call_count == 2


@pytest.mark.asyncio
async def test_get_videos_for_account_no_results(cms_service):
    with patch.object(
        cms_service, "get_video_count", new_callable=AsyncMock
    ) as mock_count:
        mock_count.return_value = VideoCount(count=0)
        result = await cms_service.get_videos_for_account("account123")
        assert len(result.root) == 0


@pytest.mark.asyncio
async def test_get_videos_for_account_page_size_too_large(cms_service):
    with pytest.raises(ValueError, match="page_size must be less than or equal to 100"):
        await cms_service.get_videos_for_account("account123", page_size=101)
