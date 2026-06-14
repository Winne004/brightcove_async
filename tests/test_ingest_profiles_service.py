"""Tests for IngestProfiles service and related schemas."""

from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.ingest_profiles_model import (
    IngestProfile,
    IngestProfileList,
)
from brightcove_async.services.ingest_profiles import IngestProfiles


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
def ingest_profiles_service(mock_session, dummy_oauth):
    """Create an IngestProfiles service instance for testing."""
    return IngestProfiles(
        session=mock_session,
        oauth=dummy_oauth,
        base_url="https://ingestion.api.brightcove.com/v1/",
        limit=4,
    )


# ---------------------------------------------------------------------------
# Service method tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_ingest_profiles_calls_fetch_data_with_correct_model(
    ingest_profiles_service,
):
    """get_ingest_profiles should call fetch_data with model=IngestProfileList."""
    with patch.object(
        ingest_profiles_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = IngestProfileList(root=[])

        await ingest_profiles_service.get_ingest_profiles("account123")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args.kwargs["model"] is IngestProfileList
        assert "account123" in call_args.kwargs["endpoint"]
        assert "profiles" in call_args.kwargs["endpoint"]


@pytest.mark.asyncio
async def test_get_ingest_profiles_returns_ingest_profile_list(
    ingest_profiles_service,
):
    """get_ingest_profiles should return an IngestProfileList."""
    expected = IngestProfileList(root=[])
    with patch.object(
        ingest_profiles_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = expected

        result = await ingest_profiles_service.get_ingest_profiles("account123")

        assert result is expected
        assert isinstance(result, IngestProfileList)


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

MINIMAL_PROFILE: dict = {
    "version": 1,
    "name": "multi-platform-standard-static",
    "account_id": 12345,
    "brightcove_standard": True,
    "date_created": 1700000000000,
    "date_last_modified": 1700000001000,
    "id": "abc123",
}


def test_ingest_profile_validates_without_optional_fields():
    """IngestProfile should validate when description, display_name, and digital_master are absent."""
    profile = IngestProfile.model_validate(MINIMAL_PROFILE)
    assert profile.name == "multi-platform-standard-static"
    assert profile.description is None
    assert profile.display_name is None
    assert profile.digital_master is None


def test_ingest_profile_list_wraps_list():
    """IngestProfileList should correctly wrap a list of IngestProfile objects."""
    raw = [
        MINIMAL_PROFILE,
        {**MINIMAL_PROFILE, "id": "def456", "name": "other-profile"},
    ]
    profile_list = IngestProfileList.model_validate(raw)
    assert len(profile_list.root) == 2
    assert profile_list.root[0].id == "abc123"
    assert profile_list.root[1].id == "def456"


def test_ingest_profile_list_empty():
    """IngestProfileList should validate an empty list."""
    profile_list = IngestProfileList.model_validate([])
    assert profile_list.root == []


def test_ingest_profile_list_default_is_empty():
    """IngestProfileList default should be an empty list."""
    profile_list = IngestProfileList()
    assert profile_list.root == []


def test_ingest_profile_with_all_fields():
    """IngestProfile should validate correctly when all optional fields are present."""
    data = {
        **MINIMAL_PROFILE,
        "description": "A test profile",
        "display_name": "Multi-Platform Standard Static",
        "digital_master": {"rendition": "passthrough", "distribute": False},
    }
    profile = IngestProfile.model_validate(data)
    assert profile.description == "A test profile"
    assert profile.display_name == "Multi-Platform Standard Static"
    assert profile.digital_master is not None
    assert profile.digital_master.rendition == "passthrough"
    assert profile.digital_master.distribute is False
