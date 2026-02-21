"""Tests for the CMS service."""

from unittest.mock import AsyncMock, MagicMock, patch

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
from brightcove_async.schemas.params import GetVideosQueryParams
from brightcove_async.services.cms import CMS

BASE_URL = "https://cms.api.brightcove.com/v1/accounts/"


@pytest.fixture
def cms_service(mock_session, dummy_oauth):
    return CMS(
        session=mock_session,
        oauth=dummy_oauth,
        base_url=BASE_URL,
        limit=4,
    )


class TestCMSInitialization:
    def test_stores_limit_and_page_limit(self, cms_service):
        assert cms_service._limit == 4
        assert cms_service._page_limit == 100
        assert cms_service.base_url == BASE_URL


# --- Video endpoints ---


class TestVideoEndpoints:
    async def test_get_videos_with_params(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            params = GetVideosQueryParams(limit=10, offset=0)
            await cms_service.get_videos("acc123", params)

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/videos",
                model=VideoArray,
                params=params.serialize_params(),
            )

    async def test_get_videos_without_params(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            await cms_service.get_videos("acc123")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/videos",
                model=VideoArray,
                params=None,
            )

    async def test_create_video(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = Video(
                id="vid1",
                name="Test Video",
                economics=Economics.AD_SUPPORTED,
            )
            video_data = CreateVideoRequestBodyFields(name="Test Video")
            await cms_service.create_video("acc123", video_data)

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/videos",
                model=Video,
                method="POST",
                json=video_data,
            )

    async def test_get_video_count(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoCount(count=100)
            result = await cms_service.get_video_count("acc123")

            assert result.count == 100
            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/counts/videos",
                model=VideoCount,
                params=None,
            )

    async def test_get_video_fields(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomFields(root=[])
            await cms_service.get_video_fields("acc123")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/video_fields/custom_fields",
                model=CustomFields,
            )


# --- Video by ID ---


class TestGetVideoById:
    async def test_single_id(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            await cms_service.get_video_by_id("acc123", ["vid1"])

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/videos/vid1",
                model=VideoArray,
            )

    async def test_multiple_ids_joined_by_comma(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            await cms_service.get_video_by_id("acc123", ["vid1", "vid2", "vid3"])

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/videos/vid1,vid2,vid3",
                model=VideoArray,
            )

    async def test_max_10_ids_allowed(self, cms_service):
        """Exactly 10 should succeed."""
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            ten_ids = [f"vid{i}" for i in range(10)]
            await cms_service.get_video_by_id("acc123", ten_ids)
            mock_fetch.assert_called_once()

    async def test_more_than_10_ids_raises(self, cms_service):
        with pytest.raises(ValueError, match="video_ids must contain 10 or fewer IDs"):
            await cms_service.get_video_by_id("acc123", [f"vid{i}" for i in range(11)])

    async def test_empty_list_raises(self, cms_service):
        with pytest.raises(ValueError, match="video_ids must contain at least one ID"):
            await cms_service.get_video_by_id("acc123", [])


# --- Video sub-resource endpoints ---


class TestVideoSubResources:
    @pytest.mark.parametrize(
        ("method_name", "extra_args", "model", "endpoint_suffix"),
        [
            ("get_video_sources", ["vid1"], VideoSourcesList, "vid1/sources"),
            ("get_video_images", ["vid1"], ImageList, "vid1/images"),
            ("get_video_variants", ["vid1"], VideoVariants, "vid1/variants"),
            ("get_video_audio_tracks", ["vid1"], AudioTracks, "vid1/audio_tracks"),
            ("get_digital_master_info", ["vid1"], DigitalMaster, "vid1/digital_master"),
            ("get_playlists_for_video", ["vid1"], Playlist, "vid1/references"),
            ("get_status_of_ingest_jobs", ["vid1"], IngestJobs, "vid1/ingest_jobs"),
            ("list_shares", ["vid1"], VideoShareList, "vid1/shares"),
        ],
        ids=[
            "sources",
            "images",
            "variants",
            "audio_tracks",
            "digital_master",
            "playlists",
            "ingest_jobs",
            "shares",
        ],
    )
    async def test_video_sub_resource_endpoint(
        self, cms_service, method_name, extra_args, model, endpoint_suffix
    ):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = MagicMock(spec=model)
            method = getattr(cms_service, method_name)
            await method("acc123", *extra_args)

            expected_endpoint = f"{BASE_URL}acc123/videos/{endpoint_suffix}"
            assert mock_fetch.call_args.kwargs["endpoint"] == expected_endpoint
            assert mock_fetch.call_args.kwargs["model"] == model

    async def test_get_video_variant_with_id(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoVariant()
            await cms_service.get_video_variant("acc123", "vid1", "var1")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/videos/vid1/variants/var1",
                model=VideoVariant,
            )

    async def test_get_video_audio_track_with_id(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = AudioTrack()
            await cms_service.get_video_audio_track("acc123", "vid1", "track1")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/videos/vid1/audio_tracks/track1",
                model=AudioTrack,
            )

    async def test_get_ingest_job_status(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = IngestJobStatus()
            await cms_service.get_ingest_job_status("acc123", "vid1", "job1")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/videos/vid1/ingest_jobs/job1",
                model=IngestJobStatus,
            )


# --- Channel endpoints ---


class TestChannelEndpoints:
    async def test_list_channels(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = ChannelList(root=[])
            await cms_service.list_channels("acc123")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/channels",
                model=ChannelList,
                params=None,
            )

    async def test_get_channel_details(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = Channel()
            await cms_service.get_channel_details("acc123", "ch1")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/channels/ch1",
                model=Channel,
            )

    async def test_list_channel_affiliates(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = ChannelAffiliateList(root=[])
            await cms_service.list_channel_affiliates("acc123", "ch1")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/channels/ch1/members",
                model=ChannelAffiliateList,
            )

    async def test_list_contracts(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = ContractList(root=[])
            await cms_service.list_contracts("acc123", "ch1")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/channels/ch1/contracts",
                model=ContractList,
            )

    async def test_get_contract(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = ContractList(root=[])
            await cms_service.get_contract("acc123", "ch1", "contract1")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/channels/ch1/contracts/contract1",
                model=ContractList,
            )


# --- Pagination (get_videos_for_account) ---


class TestGetVideosForAccount:
    async def test_pagination_fetches_correct_page_count(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            with patch.object(
                cms_service,
                "get_video_count",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_count.return_value = VideoCount(count=50)
                await cms_service.get_videos_for_account(
                    "acc123",
                    page_size=25,
                    number_of_pages=2,
                )

                assert mock_fetch.call_count == 2

    async def test_pagination_combines_results(self, cms_service):
        """Verify that pages are actually combined into a single VideoArray."""
        page1 = VideoArray(root=[Video(name="V1"), Video(name="V2")])
        page2 = VideoArray(root=[Video(name="V3")])

        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.side_effect = [page1, page2]
            with patch.object(
                cms_service,
                "get_video_count",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_count.return_value = VideoCount(count=50)
                result = await cms_service.get_videos_for_account(
                    "acc123",
                    page_size=25,
                    number_of_pages=2,
                )

                assert len(result.root) == 3
                assert result.root[0].name == "V1"
                assert result.root[2].name == "V3"

    async def test_pagination_offset_increments(self, cms_service):
        """Verify each page uses the correct offset."""
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            with patch.object(
                cms_service,
                "get_video_count",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_count.return_value = VideoCount(count=75)
                await cms_service.get_videos_for_account(
                    "acc123",
                    page_size=25,
                    number_of_pages=3,
                )

                offsets = [
                    call.kwargs["params"]["offset"]
                    for call in mock_fetch.call_args_list
                ]
                assert offsets == [0, 25, 50]

    async def test_auto_calculates_pages_when_not_specified(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            with patch.object(
                cms_service,
                "get_video_count",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_count.return_value = VideoCount(count=60)
                await cms_service.get_videos_for_account("acc123", page_size=25)

                # ceil(60/25) = 3 pages
                assert mock_fetch.call_count == 3

    async def test_returns_empty_when_count_is_zero(self, cms_service):
        with patch.object(
            cms_service,
            "get_video_count",
            new_callable=AsyncMock,
        ) as mock_count:
            mock_count.return_value = VideoCount(count=0)
            result = await cms_service.get_videos_for_account("acc123")

            assert len(result.root) == 0

    async def test_returns_empty_when_count_is_none(self, cms_service):
        with patch.object(
            cms_service,
            "get_video_count",
            new_callable=AsyncMock,
        ) as mock_count:
            mock_count.return_value = VideoCount(count=None)
            result = await cms_service.get_videos_for_account("acc123")

            assert len(result.root) == 0

    async def test_page_size_over_100_raises(self, cms_service):
        with pytest.raises(
            ValueError, match="page_size must be less than or equal to 100"
        ):
            await cms_service.get_videos_for_account("acc123", page_size=101)

    async def test_page_size_exactly_100_is_allowed(self, cms_service):
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            with patch.object(
                cms_service,
                "get_video_count",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_count.return_value = VideoCount(count=100)
                await cms_service.get_videos_for_account("acc123", page_size=100)
                mock_fetch.assert_called_once()

    async def test_passes_query_filter_to_count_and_fetch(self, cms_service):
        """When params with q= is passed, it should filter both count and fetch calls."""
        with patch.object(
            cms_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = VideoArray(root=[])
            with patch.object(
                cms_service,
                "get_video_count",
                new_callable=AsyncMock,
            ) as mock_count:
                mock_count.return_value = VideoCount(count=10)
                params = GetVideosQueryParams(q="tags:nature")
                await cms_service.get_videos_for_account(
                    "acc123",
                    page_size=25,
                    params=params,
                )

                # Count call should pass q filter
                count_call = mock_count.call_args
                count_params = count_call.kwargs.get("params") or count_call[1].get(
                    "params"
                )
                assert count_params.q == "tags:nature"

                # Fetch call should include q in params
                fetch_params = mock_fetch.call_args.kwargs["params"]
                assert fetch_params["q"] == "tags:nature"
