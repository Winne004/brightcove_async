from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.analytics_model import (
    GetAlltimeVideoViewsResponse,
    GetAnalyticsReportResponse,
    GetAvailableDateRangeResponse,
    Summary,
    Timeline,
    TimelineWithDuration,
)
from brightcove_async.schemas.params import GetAnalyticsReportParams
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
async def test_base_url_property(analytics_service):
    """Test base_url property returns correct URL."""
    assert analytics_service.base_url == "https://analytics.api.brightcove.com/v1"
