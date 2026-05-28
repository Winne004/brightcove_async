from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.audience_model import (
    GetLeadsResponse,
    GetViewEventsResponse,
)
from brightcove_async.schemas.params import GetLeadsParams, GetViewEventsParams
from brightcove_async.services.audience import Audience


class DummyOAuth:
    async def get_access_token(self):
        return "test_token"

    @property
    async def headers(self):
        return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_session():
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture
def dummy_oauth():
    return DummyOAuth()


@pytest.fixture
def audience_service(mock_session, dummy_oauth):
    return Audience(
        session=mock_session,
        oauth=dummy_oauth,
        base_url="https://audience.api.brightcove.com/v1",
        limit=10,
    )


def test_audience_initialization(audience_service):
    assert audience_service._limit == 10
    assert audience_service.base_url == "https://audience.api.brightcove.com/v1"


@pytest.mark.asyncio
async def test_get_leads(audience_service):
    with patch.object(
        audience_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=GetLeadsResponse)

        await audience_service.get_leads("account123")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "leads" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == GetLeadsResponse
        assert call_args.kwargs["params"] is None


@pytest.mark.asyncio
async def test_get_leads_with_params(audience_service):
    with patch.object(
        audience_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=GetLeadsResponse)

        params = GetLeadsParams(limit=10, offset=5, sort="created_at")
        await audience_service.get_leads("account123", params=params)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args.kwargs["params"] == {
            "limit": 10,
            "offset": 5,
            "sort": "created_at",
        }


@pytest.mark.asyncio
async def test_get_view_events(audience_service):
    with patch.object(
        audience_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=GetViewEventsResponse)

        await audience_service.get_view_events("account123")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "view_events" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == GetViewEventsResponse
        assert call_args.kwargs["params"] is None


@pytest.mark.asyncio
async def test_get_view_events_with_params(audience_service):
    with patch.object(
        audience_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=GetViewEventsResponse)

        params = GetViewEventsParams(limit=50, where="video_id==abc123")
        await audience_service.get_view_events("account456", params=params)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account456" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["params"] == {"limit": 50, "where": "video_id==abc123"}


def test_get_leads_params_serialization():
    params = GetLeadsParams(
        limit=25,
        offset=0,
        sort="created_at",
        fields="email_address",
        where="video_id==abc",
        from_="2024-01-01",
        to="2024-12-31",
    )
    serialized = params.serialize_params()
    assert serialized["limit"] == 25
    assert serialized["offset"] == 0
    assert serialized["sort"] == "created_at"
    assert serialized["fields"] == "email_address"
    assert serialized["where"] == "video_id==abc"
    assert serialized["from"] == "2024-01-01"
    assert serialized["to"] == "2024-12-31"
    assert "from_" not in serialized


def test_get_view_events_params_serialization():
    params = GetViewEventsParams(limit=100, from_=-30, to="now")
    serialized = params.serialize_params()
    assert serialized["limit"] == 100
    assert serialized["from"] == -30
    assert serialized["to"] == "now"
    assert "from_" not in serialized


def test_get_leads_params_excludes_none():
    params = GetLeadsParams(limit=10)
    serialized = params.serialize_params()
    assert "offset" not in serialized
    assert "sort" not in serialized
    assert "fields" not in serialized


def test_get_leads_response_model():
    data = {
        "count": 14,
        "limit": 4,
        "offset": 0,
        "result": [
            {
                "email_address": "test@example.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "business_phone": "",
                "company_name": "Acme",
                "page_url": "https://example.com",
                "player_id": "abc123",
                "video_id": "vid001",
                "video_name": "Test Video",
                "created_at": "2024-01-01T00:00:00Z",
                "external_id": "ext-001",
            }
        ],
    }
    response = GetLeadsResponse.model_validate(data)
    assert response.count == 14
    assert response.limit == 4
    assert response.offset == 0
    assert response.result is not None
    assert len(response.result) == 1
    assert response.result[0].email_address == "test@example.com"
    assert response.result[0].first_name == "Jane"


def test_get_view_events_response_model():
    data = {
        "count": 27,
        "limit": 25,
        "offset": 0,
        "result": [
            {
                "created_at": "2016-04-25T18:30:21.651Z",
                "page_url": "https://players.brightcove.net/example",
                "player_id": "V1s6NOwRx",
                "time_watched": 2,
                "updated_at": "2016-04-25T18:30:21.651Z",
                "video_id": "4842718056001",
                "video_name": "Test Video",
                "watched": 19,
            }
        ],
    }
    response = GetViewEventsResponse.model_validate(data)
    assert response.count == 27
    assert response.limit == 25
    assert response.offset == 0
    assert response.result is not None
    assert len(response.result) == 1
    assert response.result[0].video_id == "4842718056001"
    assert response.result[0].watched == 19
