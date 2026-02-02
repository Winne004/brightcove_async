from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from pydantic import BaseModel

from brightcove_async.exceptions import (
    BrightcoveAuthError,
    BrightcoveBadValueError,
    BrightcoveResourceNotFoundError,
)
from brightcove_async.services.base import Base


class DummyModel(BaseModel):
    """Test model for fetch_data tests."""

    id: int
    name: str


class DummyOAuth:
    """Dummy OAuth class for testing."""

    async def get_access_token(self):
        return "test_token"

    @property
    async def headers(self):
        return {"Authorization": "Bearer test_token"}


class DummyService(Base):
    """Concrete implementation of Base for testing."""


@pytest.fixture
def mock_session():
    """Create a mock aiohttp.ClientSession."""
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture
def dummy_oauth():
    """Create a dummy OAuth client."""
    return DummyOAuth()


@pytest.fixture
def base_service(mock_session, dummy_oauth):
    """Create a Base service instance for testing."""
    return DummyService(
        session=mock_session,
        oauth=dummy_oauth,
        base_url="https://api.example.com/v1",
        limit=10,
    )


def test_base_initialization(base_service, mock_session, dummy_oauth):
    """Test Base service initializes correctly."""
    assert base_service._session is mock_session
    assert base_service._oauth is dummy_oauth
    assert base_service._base_url == "https://api.example.com/v1"
    assert base_service._limit == 10
    assert base_service._limiter is None


def test_base_url_property(base_service):
    """Test base_url property returns correct URL."""
    assert base_service.base_url == "https://api.example.com/v1"


def test_limiter_lazy_initialization(base_service):
    """Test limiter is lazily initialized."""
    assert base_service._limiter is None

    limiter = base_service.limiter

    assert limiter is not None
    assert base_service._limiter is limiter
    assert limiter.max_rate == 10
    assert limiter.time_period == 1


def test_limiter_singleton(base_service):
    """Test limiter returns same instance on multiple calls."""
    limiter1 = base_service.limiter
    limiter2 = base_service.limiter

    assert limiter1 is limiter2


@pytest.mark.asyncio
async def test_fetch_data_get_success(base_service, mock_session):
    """Test successful GET request with fetch_data."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"id": 1, "name": "Test"})
    mock_response.raise_for_status = MagicMock()

    mock_session.request.return_value.__aenter__.return_value = mock_response

    result = await base_service.fetch_data(
        endpoint="https://api.example.com/v1/items/1",
        model=DummyModel,
        method="GET",
    )

    assert isinstance(result, DummyModel)
    assert result.id == 1
    assert result.name == "Test"

    mock_session.request.assert_called_once()
    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert call_args[0][1] == "https://api.example.com/v1/items/1"


@pytest.mark.asyncio
async def test_fetch_data_post_with_json(base_service, mock_session):
    """Test POST request with JSON body."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"id": 2, "name": "Created"})
    mock_response.raise_for_status = MagicMock()

    mock_session.request.return_value.__aenter__.return_value = mock_response

    request_body = DummyModel(id=2, name="Created")

    result = await base_service.fetch_data(
        endpoint="https://api.example.com/v1/items",
        model=DummyModel,
        method="POST",
        json=request_body,
    )

    assert result.id == 2
    assert result.name == "Created"

    call_kwargs = mock_session.request.call_args.kwargs
    assert call_kwargs["json"] == {"id": 2, "name": "Created"}


@pytest.mark.asyncio
async def test_fetch_data_with_params(base_service, mock_session):
    """Test request with query parameters."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"id": 3, "name": "Filtered"})
    mock_response.raise_for_status = MagicMock()

    mock_session.request.return_value.__aenter__.return_value = mock_response

    await base_service.fetch_data(
        endpoint="https://api.example.com/v1/items",
        model=DummyModel,
        params={"filter": "active", "limit": 10},
    )

    call_kwargs = mock_session.request.call_args.kwargs
    assert call_kwargs["params"] == {"filter": "active", "limit": 10}


@pytest.mark.asyncio
async def test_fetch_data_uses_oauth_headers(base_service, mock_session, dummy_oauth):
    """Test that OAuth headers are used by default."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"id": 4, "name": "Authed"})
    mock_response.raise_for_status = MagicMock()

    mock_session.request.return_value.__aenter__.return_value = mock_response

    await base_service.fetch_data(
        endpoint="https://api.example.com/v1/items",
        model=DummyModel,
    )

    call_kwargs = mock_session.request.call_args.kwargs
    assert call_kwargs["headers"] == {"Authorization": "Bearer test_token"}


@pytest.mark.asyncio
async def test_fetch_data_custom_headers(base_service, mock_session):
    """Test using custom headers overrides OAuth headers."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"id": 5, "name": "Custom"})
    mock_response.raise_for_status = MagicMock()

    mock_session.request.return_value.__aenter__.return_value = mock_response

    custom_headers = {"X-Custom-Header": "value"}

    await base_service.fetch_data(
        endpoint="https://api.example.com/v1/items",
        model=DummyModel,
        headers=custom_headers,
    )

    call_kwargs = mock_session.request.call_args.kwargs
    assert call_kwargs["headers"] == custom_headers


@pytest.mark.asyncio
async def test_fetch_data_handles_404_error(base_service, mock_session):
    """Test that 404 errors are mapped to correct exception."""
    from unittest.mock import MagicMock

    # Create the error that will be raised
    error = aiohttp.ClientResponseError(
        request_info=AsyncMock(),
        history=(),
        status=404,
    )

    mock_response = AsyncMock()
    # raise_for_status is a regular method, not async - use MagicMock instead
    mock_response.raise_for_status = MagicMock(side_effect=error)
    mock_session.request.return_value.__aenter__.return_value = mock_response

    with pytest.raises(BrightcoveResourceNotFoundError):
        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items/999",
            model=DummyModel,
        )


@pytest.mark.asyncio
async def test_fetch_data_handles_400_error(base_service, mock_session):
    """Test that 400 errors are mapped to correct exception."""
    from unittest.mock import MagicMock

    # Create the error that will be raised
    error = aiohttp.ClientResponseError(
        request_info=AsyncMock(),
        history=(),
        status=400,
    )

    mock_response = AsyncMock()
    # raise_for_status is a regular method, not async - use MagicMock instead
    mock_response.raise_for_status = MagicMock(side_effect=error)
    mock_session.request.return_value.__aenter__.return_value = mock_response

    with pytest.raises(BrightcoveBadValueError):
        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
        )


@pytest.mark.asyncio
async def test_fetch_data_handles_401_error(base_service, mock_session):
    """Test that 401 errors are mapped to correct exception and retried."""
    from unittest.mock import MagicMock

    from tenacity import RetryError

    error = aiohttp.ClientResponseError(
        request_info=AsyncMock(),
        history=(),
        status=401,
    )

    mock_response = AsyncMock()

    mock_response.raise_for_status = MagicMock(side_effect=error)
    mock_session.request.return_value.__aenter__.return_value = mock_response

    with pytest.raises(RetryError):
        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
        )

    assert mock_session.request.call_count == 5


@pytest.mark.asyncio
async def test_fetch_data_retries_on_connection_error(base_service, mock_session):
    """Test that connection errors trigger retry mechanism."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"id": 6, "name": "Retry Success"})
    mock_response.raise_for_status = MagicMock()

    # First attempt fails, second succeeds
    mock_session.request.return_value.__aenter__.side_effect = [
        aiohttp.ClientConnectionError("Connection failed"),
        mock_response,
    ]

    result = await base_service.fetch_data(
        endpoint="https://api.example.com/v1/items",
        model=DummyModel,
    )

    assert result.id == 6
    assert mock_session.request.call_count == 2


@pytest.mark.asyncio
async def test_fetch_data_retries_on_auth_error(base_service, mock_session):
    """Test that auth errors trigger retry mechanism."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"id": 7, "name": "Auth Retry"})
    mock_response.raise_for_status = MagicMock()

    # First attempt fails with auth error, second succeeds
    mock_session.request.return_value.__aenter__.side_effect = [
        BrightcoveAuthError("Token expired"),
        mock_response,
    ]

    result = await base_service.fetch_data(
        endpoint="https://api.example.com/v1/items",
        model=DummyModel,
    )

    assert result.id == 7
    assert mock_session.request.call_count == 2


@pytest.mark.asyncio
async def test_fetch_data_excludes_none_values_from_json(base_service, mock_session):
    """Test that None values are excluded from JSON body."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"id": 8, "name": "Exclude None"})
    mock_response.raise_for_status = MagicMock()

    mock_session.request.return_value.__aenter__.return_value = mock_response

    class ModelWithOptional(BaseModel):
        id: int
        name: str | None = None
        optional_field: str | None = None

    request_body = ModelWithOptional(id=8, name="Test")

    await base_service.fetch_data(
        endpoint="https://api.example.com/v1/items",
        model=DummyModel,
        method="POST",
        json=request_body,
    )

    call_kwargs = mock_session.request.call_args.kwargs
    # Should only include id and name, not optional_field
    assert "optional_field" not in call_kwargs["json"]
    assert call_kwargs["json"] == {"id": 8, "name": "Test"}
