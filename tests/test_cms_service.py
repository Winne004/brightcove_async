from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.cms_model import (
    AudioTrack,
    AudioTracks,
    Channel,
    ChannelAffiliateList,
    ChannelList,
    ContractList,
    CreateVideoRequestBodyFields,
    CustomFields,
    DigitalMaster,
    Economics,
    ImageList,
    IngestJobs,
    IngestJobStatus,
    Playlist,
    Video,
    VideoArray,
    VideoCount,
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


@pytest.mark.asyncio
async def test_get_videos(cms_service):
    """Test get_videos method."""
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
    """Test create_video method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_video = Video(
            id="video123",
            name="Test Video",
            economics=Economics.AD_SUPPORTED,
        )
        mock_fetch.return_value = mock_video

        video_data = CreateVideoRequestBodyFields(name="Test Video")
        await cms_service.create_video("account123", video_data)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["json"] == video_data


@pytest.mark.asyncio
async def test_get_video_count(cms_service):
    """Test get_video_count method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoCount(count=100)

        result = await cms_service.get_video_count("account123")

        assert result.count == 100
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_video_by_id_single(cms_service):
    """Test get_video_by_id with single ID."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoArray(root=[])

        await cms_service.get_video_by_id("account123", ["video123"])

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "video123" in call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_video_by_id_multiple(cms_service):
    """Test get_video_by_id with multiple IDs."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoArray(root=[])

        video_ids = ["video1", "video2", "video3"]
        await cms_service.get_video_by_id("account123", video_ids)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "video1,video2,video3" in call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_video_by_id_too_many_ids(cms_service):
    """Test get_video_by_id raises error with more than 10 IDs."""
    video_ids = [f"video{i}" for i in range(11)]

    with pytest.raises(ValueError, match="video_ids must contain 10 or fewer IDs"):
        await cms_service.get_video_by_id("account123", video_ids)


@pytest.mark.asyncio
async def test_get_video_by_id_empty_list(cms_service):
    """Test get_video_by_id raises error with empty list."""
    with pytest.raises(ValueError, match="video_ids must contain at least one ID"):
        await cms_service.get_video_by_id("account123", [])


@pytest.mark.asyncio
async def test_get_video_sources(cms_service):
    """Test get_video_sources method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoSourcesList(root=[])

        await cms_service.get_video_sources("account123", "video123")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "video123/sources" in call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_video_images(cms_service):
    """Test get_video_images method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        from unittest.mock import MagicMock

        mock_fetch.return_value = MagicMock(spec=ImageList)

        await cms_service.get_video_images("account123", "video123")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "video123/images" in call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_video_variants(cms_service):
    """Test get_video_variants method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoVariants(root=[])

        await cms_service.get_video_variants("account123", "video123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_video_variant(cms_service):
    """Test get_video_variant method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoVariant()

        await cms_service.get_video_variant(
            "account123",
            "video123",
            "variant123",
        )

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "variant123" in call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_video_audio_tracks(cms_service):
    """Test get_video_audio_tracks method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = AudioTracks(root=[])

        await cms_service.get_video_audio_tracks("account123", "video123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_video_audio_track(cms_service):
    """Test get_video_audio_track method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = AudioTrack()

        await cms_service.get_video_audio_track(
            "account123",
            "video123",
            "track123",
        )

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_digital_master_info(cms_service):
    """Test get_digital_master_info method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = DigitalMaster()

        await cms_service.get_digital_master_info("account123", "video123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_playlists_for_video(cms_service):
    """Test get_playlists_for_video method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Playlist()

        await cms_service.get_playlists_for_video("account123", "video123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_status_of_ingest_jobs(cms_service):
    """Test get_status_of_ingest_jobs method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = IngestJobs(root=[])

        await cms_service.get_status_of_ingest_jobs("account123", "video123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_ingest_job_status(cms_service):
    """Test get_ingest_job_status method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = IngestJobStatus()

        await cms_service.get_ingest_job_status(
            "account123",
            "video123",
            "job123",
        )

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "job123" in call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_list_channels(cms_service):
    """Test list_channels method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ChannelList(root=[])

        await cms_service.list_channels("account123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_channel_details(cms_service):
    """Test get_channel_details method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = Channel()

        await cms_service.get_channel_details("account123", "channel123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_list_channel_affiliates(cms_service):
    """Test list_channel_affiliates method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ChannelAffiliateList(root=[])

        await cms_service.list_channel_affiliates("account123", "channel123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_list_contracts(cms_service):
    """Test list_contracts method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ContractList(root=[])

        await cms_service.list_contracts("account123", "channel123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_contract(cms_service):
    """Test get_contract method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ContractList(root=[])

        await cms_service.get_contract(
            "account123",
            "channel123",
            "contract123",
        )

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "contract123" in call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_list_shares(cms_service):
    """Test list_shares method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = VideoShareList(root=[])

        await cms_service.list_shares("account123", "video123")

        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_video_fields(cms_service):
    """Test get_video_fields method."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = CustomFields(root=[])

        await cms_service.get_video_fields("account123")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "video_fields/custom_fields" in call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_videos_for_account_pagination(cms_service):
    """Test get_videos_for_account handles pagination correctly."""
    with patch.object(cms_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        # Mock count response
        mock_fetch.return_value = VideoArray(root=[])

        with patch.object(
            cms_service,
            "get_video_count",
            new_callable=AsyncMock,
        ) as mock_count:
            mock_count.return_value = VideoCount(count=50)

            await cms_service.get_videos_for_account(
                "account123",
                page_size=25,
                number_of_pages=2,
            )

            # Should have fetched 2 pages
            assert mock_fetch.call_count == 2


@pytest.mark.asyncio
async def test_get_videos_for_account_no_results(cms_service):
    """Test get_videos_for_account returns empty when count is 0."""
    with patch.object(
        cms_service,
        "get_video_count",
        new_callable=AsyncMock,
    ) as mock_count:
        mock_count.return_value = VideoCount(count=0)

        result = await cms_service.get_videos_for_account("account123")

        assert len(result.root) == 0


@pytest.mark.asyncio
async def test_get_videos_for_account_page_size_too_large(cms_service):
    """Test get_videos_for_account raises error for page_size > 100."""
    with pytest.raises(ValueError, match="page_size must be less than or equal to 100"):
        await cms_service.get_videos_for_account("account123", page_size=101)
