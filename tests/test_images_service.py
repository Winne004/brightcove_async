from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from brightcove_async.exceptions import BrightcoveResourceNotFoundError
from brightcove_async.schemas.params import ImageTransformParams
from brightcove_async.services.images import Images

BASE_URL = "https://images.brightcovecdn.com"


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
def images_service(mock_session, dummy_oauth):
    return Images(
        session=mock_session,
        oauth=dummy_oauth,
        base_url=BASE_URL,
        limit=10,
    )


def test_images_initialization(images_service):
    assert images_service._limit == 10
    assert images_service.base_url == BASE_URL


def test_image_transform_params_serialization():
    params = ImageTransformParams(
        resize="300x200",
        crop="200x200",
        rotate="90",
        fallback=True,
        fill_area=False,
        watermark=True,
        nocache=True,
    )

    serialized = params.serialize_params()

    assert serialized == {
        "resize": "300x200",
        "crop": "200x200",
        "rotate": "90",
        "fallback": "true",
        "fillArea": "false",
        "watermark": "true",
        "nocache": "true",
    }


def test_image_transform_params_omits_none():
    params = ImageTransformParams(resize="300x200")

    assert params.serialize_params() == {"resize": "300x200"}


def test_nocache_alone_raises():
    params = ImageTransformParams(nocache=True)

    with pytest.raises(ValueError, match="nocache"):
        params.serialize_params()


def test_nocache_is_emitted_last():
    params = ImageTransformParams(nocache=True, resize="300x200", crop="200x200")

    serialized = params.serialize_params()

    assert list(serialized.keys())[-1] == "nocache"
    assert serialized["nocache"] == "true"


@pytest.mark.asyncio
async def test_transform_image_builds_endpoint_and_returns_bytes(
    images_service, mock_session
):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=b"image-bytes")
    mock_session.request.return_value.__aenter__.return_value = mock_response

    result = await images_service.transform_image(
        "account123",
        "tok456",
        "https://example.com/my image.png",
    )

    assert result == b"image-bytes"
    mock_session.request.assert_called_once()
    call_args = mock_session.request.call_args
    assert call_args.args[0] == "GET"
    endpoint = call_args.args[1]
    assert "account123" in endpoint
    assert "tok456" in endpoint
    assert "/image/v1/" in endpoint
    # Source URL must be percent-encoded (encodeURIComponent style)
    assert "https%3A%2F%2Fexample.com%2Fmy%20image.png" in endpoint
    # No transformation params and no auth headers sent
    assert call_args.kwargs.get("params") is None
    assert call_args.kwargs.get("headers") == {}


@pytest.mark.asyncio
async def test_transform_image_passes_query_params(images_service, mock_session):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=b"image-bytes")
    mock_session.request.return_value.__aenter__.return_value = mock_response

    params = ImageTransformParams(resize="640x480", fallback=True)

    result = await images_service.transform_image(
        "account123",
        "tok456",
        "https://example.com/image.jpg",
        params=params,
    )

    assert result == b"image-bytes"
    call_args = mock_session.request.call_args
    assert call_args.kwargs.get("params") == {
        "resize": "640x480",
        "fallback": "true",
    }


@pytest.mark.asyncio
async def test_transform_image_retries_on_connection_error(
    images_service, mock_session
):
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=b"image-bytes")
    mock_session.request.return_value.__aenter__.side_effect = [
        aiohttp.ClientConnectionError("Connection failed"),
        mock_response,
    ]

    result = await images_service.transform_image(
        "account123", "tok456", "https://example.com/image.gif"
    )

    assert result == b"image-bytes"
    assert mock_session.request.call_count == 2


@pytest.mark.asyncio
async def test_transform_image_redacts_token_in_errors(images_service, mock_session):
    error = aiohttp.ClientResponseError(
        request_info=AsyncMock(), history=(), status=404
    )
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock(side_effect=error)
    mock_response.text = AsyncMock(return_value="not found")
    mock_session.request.return_value.__aenter__.return_value = mock_response

    with pytest.raises(BrightcoveResourceNotFoundError) as exc_info:
        await images_service.transform_image(
            "account123",
            "supersecrettoken",
            "https://example.com/image.png",
        )

    error_text = str(exc_info.value)
    assert "supersecrettoken" not in error_text
    assert exc_info.value.endpoint is not None
    assert "supersecrettoken" not in exc_info.value.endpoint
    assert "[REDACTED]" in exc_info.value.endpoint
