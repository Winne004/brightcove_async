"""Tests for the DynamicIngest service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from brightcove_async.schemas.dynamic_ingest_model import (
    GetS3UrlsResponse,
    IngestMediaAssetbody,
    IngestMediaAssetResponse,
)
from brightcove_async.services.dynamic_ingest import DynamicIngest

BASE_URL = "https://ingest.api.brightcove.com/v1/accounts/"


@pytest.fixture
def di_service(mock_session, dummy_oauth):
    return DynamicIngest(
        session=mock_session,
        oauth=dummy_oauth,
        base_url=BASE_URL,
        limit=10,
    )


class TestDynamicIngestInitialization:
    def test_stores_limit_and_url(self, di_service):
        assert di_service._limit == 10
        assert di_service.base_url == BASE_URL


class TestIngestVideosAndAssets:
    async def test_calls_fetch_data_with_correct_args(self, di_service):
        with patch.object(
            di_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = IngestMediaAssetResponse(id="job123")
            mock_body = MagicMock(spec=IngestMediaAssetbody)

            result = await di_service.ingest_videos_and_assets(
                "acc1", "vid1", mock_body
            )

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc1/videos/vid1/ingest-requests",
                model=IngestMediaAssetResponse,
                method="POST",
                json=mock_body,
            )
            assert result.id == "job123"

    async def test_exact_endpoint_format(self, di_service):
        with patch.object(
            di_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = IngestMediaAssetResponse(id="j1")
            await di_service.ingest_videos_and_assets("myacc", "myvid", MagicMock())

            expected = f"{BASE_URL}myacc/videos/myvid/ingest-requests"
            assert mock_fetch.call_args.kwargs["endpoint"] == expected


class TestGetTemporaryS3Urls:
    async def test_calls_fetch_data_with_correct_args(self, di_service):
        with patch.object(
            di_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = GetS3UrlsResponse(
                bucket="my-bucket",
                object_key="key",
                access_key_id="akid",
                secret_access_key="sak",
                session_token="st",
                SignedUrl="https://signed.url",
                ApiRequestUrl="https://api.url",
            )

            result = await di_service.get_temporary_s3_urls("acc1", "source.mp4")

            call_kwargs = mock_fetch.call_args.kwargs
            assert call_kwargs["model"] == GetS3UrlsResponse
            assert call_kwargs["method"] == "GET"
            assert call_kwargs["params"] == {"source_name": "source.mp4"}
            assert "upload-urls/source.mp4" in call_kwargs["endpoint"]
            assert result.bucket == "my-bucket"
