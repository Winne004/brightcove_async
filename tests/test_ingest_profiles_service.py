"""Tests for the IngestProfiles service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from brightcove_async.schemas.ingest_profiles_model import IngestProfile
from brightcove_async.services.ingest_profiles import IngestProfiles

BASE_URL = "https://ingestion.api.brightcove.com/v1/"


@pytest.fixture
def ip_service(mock_session, dummy_oauth):
    return IngestProfiles(
        session=mock_session,
        oauth=dummy_oauth,
        base_url=BASE_URL,
        limit=4,
    )


class TestIngestProfilesInitialization:
    def test_stores_limit_and_url(self, ip_service):
        assert ip_service._limit == 4
        assert ip_service.base_url == BASE_URL

    def test_default_limit_is_4(self, mock_session, dummy_oauth):
        """IngestProfiles.__init__ defaults limit to 4, not 10."""
        service = IngestProfiles(
            session=mock_session,
            oauth=dummy_oauth,
            base_url=BASE_URL,
        )
        assert service._limit == 4


class TestGetIngestProfiles:
    async def test_calls_fetch_data_with_exact_endpoint(self, ip_service):
        with patch.object(
            ip_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = MagicMock(spec=IngestProfile)
            await ip_service.get_ingest_profiles("my_account")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}accounts/my_account/profiles",
                model=IngestProfile,
            )

    async def test_uses_default_get_method(self, ip_service):
        """fetch_data is called without an explicit method, defaulting to GET."""
        with patch.object(
            ip_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = MagicMock(spec=IngestProfile)
            await ip_service.get_ingest_profiles("acc123")

            call_kwargs = mock_fetch.call_args.kwargs
            assert "method" not in call_kwargs
