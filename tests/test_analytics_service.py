"""Tests for the Analytics service."""

from unittest.mock import AsyncMock, MagicMock, patch

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

BASE_URL = "https://analytics.api.brightcove.com/v1"


@pytest.fixture
def analytics_service(mock_session, dummy_oauth):
    return Analytics(
        session=mock_session,
        oauth=dummy_oauth,
        base_url=BASE_URL,
        limit=10,
    )


class TestAnalyticsInitialization:
    def test_stores_limit_and_url(self, analytics_service):
        assert analytics_service._limit == 10
        assert analytics_service.base_url == BASE_URL

    def test_base_url_property_override(self, analytics_service):
        """Analytics overrides base_url as a property — verify it works."""
        assert analytics_service.base_url == BASE_URL


class TestAnalyticsEndpoints:
    """Verify each method calls fetch_data with the exact correct endpoint and model."""

    async def test_get_account_engagement(self, analytics_service):
        with patch.object(
            analytics_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = MagicMock(spec=Timeline)
            await analytics_service.get_account_engagement("acc123")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}/engagement/accounts/acc123",
                model=Timeline,
            )

    async def test_get_player_engagement(self, analytics_service):
        with patch.object(
            analytics_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = MagicMock(spec=Timeline)
            await analytics_service.get_player_engagement("acc123", "player456")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}/engagement/accounts/acc123/players/player456",
                model=Timeline,
            )

    async def test_get_video_engagement(self, analytics_service):
        with patch.object(
            analytics_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = MagicMock(spec=TimelineWithDuration)
            await analytics_service.get_video_engagement("acc123", "vid789")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}/engagement/accounts/acc123/videos/vid789",
                model=TimelineWithDuration,
            )

    async def test_get_analytics_report(self, analytics_service):
        with patch.object(
            analytics_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = GetAnalyticsReportResponse(
                item_count=0,
                items=[],
                summary=Summary(),
            )
            params = GetAnalyticsReportParams(accounts="acc123", dimensions="video")
            await analytics_service.get_analytics_report(params)

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}/data",
                model=GetAnalyticsReportResponse,
                params=params.serialize_params(),
            )

    async def test_get_analytics_report_passes_serialized_params(
        self, analytics_service
    ):
        """Verify params are serialized (aliases resolved) before passing to fetch_data."""
        with patch.object(
            analytics_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = GetAnalyticsReportResponse(
                item_count=0,
                items=[],
                summary=Summary(),
            )
            params = GetAnalyticsReportParams(
                accounts="acc123",
                dimensions="video",
                from_="2024-01-01",
            )
            await analytics_service.get_analytics_report(params)

            call_params = mock_fetch.call_args.kwargs["params"]
            assert "from" in call_params
            assert "from_" not in call_params

    async def test_get_available_date_range(self, analytics_service):
        with patch.object(
            analytics_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = GetAvailableDateRangeResponse(
                reconciled_from="2024-01-01",
                reconciled_to="2024-12-31",
            )
            params = GetAnalyticsReportParams(accounts="acc123", dimensions="video")
            await analytics_service.get_available_date_range(params)

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}/data/status",
                model=GetAvailableDateRangeResponse,
                params=params.serialize_params(),
            )

    async def test_get_alltime_video_views(self, analytics_service):
        with patch.object(
            analytics_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = GetAlltimeVideoViewsResponse(
                alltime_video_views=1000
            )
            await analytics_service.get_alltime_video_views("acc123", "vid456")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}/alltime/accounts/acc123/videos/vid456",
                model=GetAlltimeVideoViewsResponse,
            )
