from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.syndication_model import (
    Syndication as SyndicationModel,
)
from brightcove_async.schemas.syndication_model import (
    SyndicationList,
    Type,
)
from brightcove_async.services.syndication import Syndication

BASE_URL = "https://social.api.brightcove.com/v1"


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
def syndication_service(mock_session, dummy_oauth):
    return Syndication(
        session=mock_session,
        oauth=dummy_oauth,
        base_url=BASE_URL,
        limit=10,
    )


def test_syndication_initialization(syndication_service):
    assert syndication_service._limit == 10
    assert syndication_service.base_url == BASE_URL


@pytest.mark.asyncio
async def test_get_all_syndications(syndication_service):
    with patch.object(
        syndication_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = SyndicationList(root=[])

        await syndication_service.get_all_syndications("account123")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "mrss/syndications" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == SyndicationList


@pytest.mark.asyncio
async def test_get_syndication(syndication_service):
    with patch.object(
        syndication_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = SyndicationModel(name="Test", type=Type.google)

        await syndication_service.get_syndication("account123", "syndication456")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "syndication456" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["model"] == SyndicationModel


@pytest.mark.asyncio
async def test_create_syndication(syndication_service):
    syndication = SyndicationModel(name="Test Feed", type=Type.google)

    with patch.object(
        syndication_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=SyndicationModel)

        await syndication_service.create_syndication("account123", syndication)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "mrss/syndications" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["model"] == SyndicationModel
        assert call_args.kwargs["payload"] == syndication


@pytest.mark.asyncio
async def test_update_syndication(syndication_service):
    syndication = SyndicationModel(name="Updated Feed", type=Type.itunes)

    with patch.object(
        syndication_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=SyndicationModel)

        await syndication_service.update_syndication(
            "account123", "syn456", syndication
        )

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "syn456" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PUT"
        assert call_args.kwargs["model"] == SyndicationModel
        assert call_args.kwargs["payload"] == syndication


@pytest.mark.asyncio
async def test_patch_syndication(syndication_service):
    syndication = SyndicationModel(name="Patched Feed", type=Type.roku)

    with patch.object(
        syndication_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=SyndicationModel)

        await syndication_service.patch_syndication("account123", "syn456", syndication)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "account123" in call_args.kwargs["endpoint"]
        assert "syn456" in call_args.kwargs["endpoint"]
        assert call_args.kwargs["method"] == "PATCH"
        assert call_args.kwargs["model"] == SyndicationModel
        assert call_args.kwargs["payload"] == syndication


@pytest.mark.asyncio
async def test_delete_syndication(syndication_service, mock_session):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_session.request.return_value.__aenter__.return_value = mock_response

    await syndication_service.delete_syndication("account123", "syn456")

    mock_session.request.assert_called_once()
    call_args = mock_session.request.call_args
    assert call_args.args[0] == "DELETE"
    assert "account123" in call_args.args[1]
    assert "syn456" in call_args.args[1]
    assert "mrss/syndications" in call_args.args[1]


@pytest.mark.asyncio
async def test_get_template(syndication_service, mock_session):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.text = AsyncMock(return_value="<feed>template content</feed>")
    mock_session.request.return_value.__aenter__.return_value = mock_response

    result = await syndication_service.get_template("account123", "syn456")

    mock_session.request.assert_called_once()
    call_args = mock_session.request.call_args
    assert call_args.args[0] == "GET"
    assert "account123" in call_args.args[1]
    assert "syn456" in call_args.args[1]
    assert "template" in call_args.args[1]
    assert result == "<feed>template content</feed>"


@pytest.mark.asyncio
async def test_upload_template(syndication_service, mock_session):
    template_content = "<feed>my custom template</feed>"
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_session.request.return_value.__aenter__.return_value = mock_response

    await syndication_service.upload_template("account123", "syn456", template_content)

    mock_session.request.assert_called_once()
    call_args = mock_session.request.call_args
    assert call_args.args[0] == "PUT"
    assert "account123" in call_args.args[1]
    assert "syn456" in call_args.args[1]
    assert "template" in call_args.args[1]
    assert call_args.kwargs.get("data") == template_content
    assert call_args.kwargs.get("headers", {}).get("Content-Type") == "text/plain"


@pytest.mark.asyncio
async def test_delete_syndication_retries_on_connection_error(
    syndication_service, mock_session
):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_session.request.return_value.__aenter__.side_effect = [
        aiohttp.ClientConnectionError("Connection failed"),
        mock_response,
    ]

    await syndication_service.delete_syndication("account123", "syn456")

    assert mock_session.request.call_count == 2


@pytest.mark.asyncio
async def test_get_template_retries_on_connection_error(
    syndication_service, mock_session
):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.text = AsyncMock(return_value="<feed/>")
    mock_session.request.return_value.__aenter__.side_effect = [
        aiohttp.ClientConnectionError("Connection failed"),
        mock_response,
    ]

    result = await syndication_service.get_template("account123", "syn456")

    assert result == "<feed/>"
    assert mock_session.request.call_count == 2


@pytest.mark.asyncio
async def test_upload_template_retries_on_connection_error(
    syndication_service, mock_session
):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_session.request.return_value.__aenter__.side_effect = [
        aiohttp.ClientConnectionError("Connection failed"),
        mock_response,
    ]

    await syndication_service.upload_template("account123", "syn456", "<feed/>")

    assert mock_session.request.call_count == 2
