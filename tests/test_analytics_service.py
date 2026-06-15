from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.analytics_model import (
    GetAlltimeVideoViewsResponse,
    GetAnalyticsReportResponse,
    GetAvailableDateRangeResponse,
    GetEventsResponse,
    GetTimeSeriesResponse,
    Summary,
    Timeline,
    TimelineWithDuration,
    TimeSeriesMetric,
)
from brightcove_async.schemas.params import (
    GetAnalyticsReportParams,
    GetLiveEventsParams,
    GetLivestreamAnalyticsParams,
)
from brightcove_async.services.analytics import Analytics


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
def analytics_service(mock_session, dummy_oauth):
    """Create an Analytics service instance for testing."""
    return Analytics(
        session=mock_session,
        oauth=dummy_oauth,
        base_url="https://analytics.api.brightcove.com/v1",
        limit=10,
    )


def test_analytics_initialization(analytics_service):
    """Test Analytics service initializes with correct parameters."""
    assert analytics_service._limit == 10
    assert analytics_service.base_url == "https://analytics.api.brightcove.com/v1"


@pytest.mark.asyncio
async def test_get_account_engagement(analytics_service):
    """Test get_account_engagement method."""
    with patch.object(
        analytics_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        from unittest.mock import MagicMock

        mock_fetch.return_value = MagicMock(spec=Timeline)

        await analytics_service.get_account_engagement("account123")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "engagement/accounts/account123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == Timeline


@pytest.mark.asyncio
async def test_get_player_engagement(analytics_service):
    """Test get_player_engagement method."""
    with patch.object(
        analytics_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        from unittest.mock import MagicMock

        mock_fetch.return_value = MagicMock(spec=Timeline)

        await analytics_service.get_player_engagement(
            "account123",
            "player456",
        )

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "player456" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == Timeline


@pytest.mark.asyncio
async def test_get_video_engagement(analytics_service):
    """Test get_video_engagement method."""
    with patch.object(
        analytics_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        from unittest.mock import MagicMock

        mock_fetch.return_value = MagicMock(spec=TimelineWithDuration)

        await analytics_service.get_video_engagement("account123", "video789")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "video789" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == TimelineWithDuration


@pytest.mark.asyncio
async def test_get_analytics_report(analytics_service):
    """Test get_analytics_report method."""
    with patch.object(
        analytics_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        mock_fetch.return_value = GetAnalyticsReportResponse(
            item_count=0,
            items=[],
            summary=Summary(**{}),
        )

        params = GetAnalyticsReportParams(
            accounts="account123",
            dimensions="video",
        )

        await analytics_service.get_analytics_report(params)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "data" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == GetAnalyticsReportResponse
        assert call_args.kwargs["params"] is not None


@pytest.mark.asyncio
async def test_get_available_date_range(analytics_service):
    """Test get_available_date_range method."""
    with patch.object(
        analytics_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        mock_fetch.return_value = GetAvailableDateRangeResponse(
            reconciled_from="2024-01-01",
            reconciled_to="2024-12-31",
        )

        params = GetAnalyticsReportParams(
            accounts="account123",
            dimensions="video",
        )

        await analytics_service.get_available_date_range(params)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "data/status" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == GetAvailableDateRangeResponse


@pytest.mark.asyncio
async def test_get_alltime_video_views(analytics_service):
    """Test get_alltime_video_views method."""
    with patch.object(
        analytics_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        mock_fetch.return_value = GetAlltimeVideoViewsResponse(alltime_video_views=1000)

        await analytics_service.get_alltime_video_views(
            "account123",
            "video456",
        )

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "video456" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == GetAlltimeVideoViewsResponse


@pytest.mark.asyncio
async def test_get_live_time_series(analytics_service):
    """Test get_live_time_series method."""
    with patch.object(
        analytics_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        from unittest.mock import MagicMock

        mock_fetch.return_value = MagicMock(spec=GetTimeSeriesResponse)

        params = GetLivestreamAnalyticsParams(
            dimensions="video",
            metrics="video_view,ccu",
            where="video==6063969160001",
        )

        await analytics_service.get_live_time_series("account123", params)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "timeseries/accounts/account123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == GetTimeSeriesResponse
        assert call_args.kwargs["params"] == {
            "dimensions": "video",
            "metrics": "video_view,ccu",
            "where": "video==6063969160001",
        }


@pytest.mark.asyncio
async def test_get_live_time_series_with_optional_params(analytics_service):
    """Test get_live_time_series method with bucket and time range params."""
    with patch.object(
        analytics_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        from unittest.mock import MagicMock

        mock_fetch.return_value = MagicMock(spec=GetTimeSeriesResponse)

        params = GetLivestreamAnalyticsParams(
            dimensions="video",
            metrics="ccu",
            where="video==abc",
            bucket_limit=10,
            bucket_duration="5m",
            from_="2024-01-01",
            to="2024-01-02",
        )

        await analytics_service.get_live_time_series("account456", params)

        call_args = mock_fetch.call_args
        serialized = call_args.kwargs["params"]
        assert serialized["bucket_limit"] == 10
        assert serialized["bucket_duration"] == "5m"
        assert serialized["from"] == "2024-01-01"
        assert serialized["to"] == "2024-01-02"
        assert "from_" not in serialized


@pytest.mark.asyncio
async def test_get_live_events(analytics_service):
    """Test get_live_events method."""
    with patch.object(
        analytics_service,
        "fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        from unittest.mock import MagicMock

        mock_fetch.return_value = MagicMock(spec=GetEventsResponse)

        params = GetLiveEventsParams(
            dimensions="video,country",
            metrics="video_view,video_seconds_viewed",
            where="video==6049313942001",
        )

        await analytics_service.get_live_events("account123", params)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "events/accounts/account123" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == GetEventsResponse
        assert call_args.kwargs["params"] == {
            "dimensions": "video,country",
            "metrics": "video_view,video_seconds_viewed",
            "where": "video==6049313942001",
        }


def test_get_live_events_params_serialization():
    """Test GetLiveEventsParams serializes correctly."""
    params = GetLiveEventsParams(
        dimensions="video",
        metrics="ccu",
        where="country==US",
    )
    serialized = params.serialize_params()
    assert serialized == {
        "dimensions": "video",
        "metrics": "ccu",
        "where": "country==US",
    }


def test_get_livestream_analytics_params_serialization():
    """Test GetLivestreamAnalyticsParams serializes from/to aliases and omits None."""
    params = GetLivestreamAnalyticsParams(
        dimensions="video",
        metrics="video_view",
        where="video==abc",
        bucket_limit=5,
        from_=1535654206775,
    )
    serialized = params.serialize_params()
    assert serialized["from"] == 1535654206775
    assert "from_" not in serialized
    assert "bucket_duration" not in serialized
    assert "to" not in serialized


def test_get_time_series_response_model():
    """Test GetTimeSeriesResponse parses the actual Brightcove API response shape."""
    raw = {
        "video_view": {
            "data": [
                {
                    "dimensions": {"video": "6063969160001", "account": "57838016001"},
                    "points": [
                        {"timestamp": 1564075800000, "value": 11.0},
                        {"timestamp": 1564077600000, "value": 1.0},
                    ],
                }
            ]
        },
        "alive_ss_ad_start": {},
        "ccu": {
            "data": [
                {
                    "dimensions": {"video": "6063969160001", "account": "57838016001"},
                    "points": [{"timestamp": 1564075800000, "value": 9.0}],
                }
            ]
        },
    }
    response = GetTimeSeriesResponse.model_validate(raw)
    assert "video_view" in response.root
    assert response.root["video_view"].data is not None
    assert len(response.root["video_view"].data) == 1
    assert response.root["video_view"].data[0]["dimensions"]["video"] == "6063969160001"
    assert response.root["alive_ss_ad_start"].data is None
    assert response.root["ccu"].data is not None


def test_get_time_series_response_model_is_class():
    """Test TimeSeriesMetric is accessible and models the per-metric shape."""
    metric = TimeSeriesMetric.model_validate(
        {"data": [{"dimensions": {}, "points": []}]}
    )
    assert metric.data is not None
    assert len(metric.data) == 1

    empty_metric = TimeSeriesMetric.model_validate({})
    assert empty_metric.data is None


@pytest.mark.asyncio
async def test_base_url_property(analytics_service):
    """Test base_url property returns correct URL."""
    assert analytics_service.base_url == "https://analytics.api.brightcove.com/v1"
