"""Tests for the Base service class: fetch_data, rate limiting, error handling, retries."""

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from pydantic import BaseModel
from tenacity import RetryError

from brightcove_async.exceptions import (
    BrightcoveAuthError,
    BrightcoveBadValueError,
    BrightcoveConflictError,
    BrightcoveResourceNotFoundError,
    BrightcoveTooManyRequestsError,
    BrightcoveUnknownError,
)
from brightcove_async.services.base import Base


class DummyModel(BaseModel):
    """Test model for fetch_data tests."""

    id: int
    name: str


class DummyService(Base):
    """Concrete implementation of Base for testing."""


@pytest.fixture
def base_service(mock_session, dummy_oauth):
    """Create a Base service instance for testing."""
    return DummyService(
        session=mock_session,
        oauth=dummy_oauth,
        base_url="https://api.example.com/v1",
        limit=10,
    )


def _make_success_response(data: dict) -> AsyncMock:
    """Helper to create a mock response that returns JSON data."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=data)
    mock_response.raise_for_status = MagicMock()
    return mock_response


def _make_error_response(status: int, body: str = "error") -> AsyncMock:
    """Helper to create a mock response that raises a ClientResponseError."""
    error = aiohttp.ClientResponseError(
        request_info=AsyncMock(),
        history=(),
        status=status,
    )
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock(side_effect=error)
    mock_response.text = AsyncMock(return_value=body)
    return mock_response


# --- Initialization ---


class TestBaseInitialization:
    def test_stores_dependencies(self, base_service, mock_session, dummy_oauth):
        assert base_service._session is mock_session
        assert base_service._oauth is dummy_oauth
        assert base_service._base_url == "https://api.example.com/v1"
        assert base_service._limit == 10
        assert base_service._limiter is None

    def test_base_url_property(self, base_service):
        assert base_service.base_url == "https://api.example.com/v1"

    def test_default_limit_class_attribute(self):
        assert Base._limit == 10


# --- Rate Limiter ---


class TestLimiter:
    def test_lazy_initialization(self, base_service):
        assert base_service._limiter is None
        limiter = base_service.limiter
        assert limiter is not None
        assert base_service._limiter is limiter
        assert limiter.max_rate == 10
        assert limiter.time_period == 1

    def test_singleton(self, base_service):
        assert base_service.limiter is base_service.limiter

    def test_respects_custom_limit(self, dummy_oauth):
        service = DummyService(
            session=AsyncMock(),
            oauth=dummy_oauth,
            base_url="https://api.example.com/v1",
            limit=5,
        )
        assert service.limiter.max_rate == 5


# --- Successful Requests ---


class TestFetchDataSuccess:
    async def test_get_returns_parsed_model(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 1, "name": "Test"})
        )

        result = await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items/1",
            model=DummyModel,
            method="GET",
        )

        assert isinstance(result, DummyModel)
        assert result.id == 1
        assert result.name == "Test"

    async def test_get_sends_correct_request(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 1, "name": "Test"})
        )

        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items/1",
            model=DummyModel,
        )

        call_args = mock_session.request.call_args
        assert call_args[0] == ("GET", "https://api.example.com/v1/items/1")

    async def test_default_method_is_get(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 1, "name": "Test"})
        )

        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items/1",
            model=DummyModel,
        )

        assert mock_session.request.call_args[0][0] == "GET"

    async def test_post_with_json_body(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 2, "name": "Created"})
        )
        request_body = DummyModel(id=2, name="Created")

        result = await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
            method="POST",
            json=request_body,
        )

        assert result.id == 2
        assert mock_session.request.call_args.kwargs["json"] == {
            "id": 2,
            "name": "Created",
        }

    async def test_with_query_params(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 3, "name": "Filtered"})
        )

        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
            params={"filter": "active", "limit": 10},
        )

        assert mock_session.request.call_args.kwargs["params"] == {
            "filter": "active",
            "limit": 10,
        }

    async def test_uses_oauth_headers_by_default(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 1, "name": "Test"})
        )

        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
        )

        assert mock_session.request.call_args.kwargs["headers"] == {
            "Authorization": "Bearer test_token",
        }

    async def test_custom_headers_override_oauth(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 1, "name": "Test"})
        )
        custom_headers = {"X-Custom": "value"}

        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
            headers=custom_headers,
        )

        assert mock_session.request.call_args.kwargs["headers"] == custom_headers

    async def test_no_json_body_sends_none(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 1, "name": "Test"})
        )

        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
        )

        assert mock_session.request.call_args.kwargs["json"] is None


# --- JSON Body Serialization ---


class TestFetchDataJsonSerialization:
    async def test_excludes_none_values(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 8, "name": "Test"})
        )

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

        sent_json = mock_session.request.call_args.kwargs["json"]
        assert "optional_field" not in sent_json
        assert sent_json == {"id": 8, "name": "Test"}

    async def test_excludes_unset_values(self, base_service, mock_session):
        """Verify exclude_unset=True — fields not explicitly set are omitted."""
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 1, "name": "Test"})
        )

        class ModelWithDefaults(BaseModel):
            id: int
            name: str = "default_name"
            description: str = "default_desc"

        request_body = ModelWithDefaults(id=1)
        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
            method="POST",
            json=request_body,
        )

        sent_json = mock_session.request.call_args.kwargs["json"]
        assert sent_json == {"id": 1}

    async def test_excludes_default_values(self, base_service, mock_session):
        """Verify exclude_defaults=True — fields equal to their default are omitted."""
        mock_session.request.return_value.__aenter__.return_value = (
            _make_success_response({"id": 1, "name": "Test"})
        )

        class ModelWithDefaults(BaseModel):
            id: int
            active: bool = True
            tags: list[str] = []

        request_body = ModelWithDefaults(id=1, active=True, tags=[])
        await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
            method="POST",
            json=request_body,
        )

        sent_json = mock_session.request.call_args.kwargs["json"]
        assert sent_json == {"id": 1}


# --- Error Handling ---


class TestFetchDataErrorHandling:
    @pytest.mark.parametrize(
        ("status", "expected_exception"),
        [
            (400, BrightcoveBadValueError),
            (404, BrightcoveResourceNotFoundError),
            (409, BrightcoveConflictError),
            (429, BrightcoveTooManyRequestsError),
            (500, BrightcoveUnknownError),
        ],
        ids=[
            "400-bad-value",
            "404-not-found",
            "409-conflict",
            "429-rate-limit",
            "500-server",
        ],
    )
    async def test_status_code_maps_to_exception(
        self, base_service, mock_session, status, expected_exception
    ):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_error_response(status, f"Error {status}")
        )

        with pytest.raises(expected_exception) as exc_info:
            await base_service.fetch_data(
                endpoint="https://api.example.com/v1/items",
                model=DummyModel,
            )

        assert exc_info.value.status_code == status

    async def test_error_captures_response_body(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_error_response(400, '{"error": "bad request body"}')
        )

        with pytest.raises(BrightcoveBadValueError) as exc_info:
            await base_service.fetch_data(
                endpoint="https://api.example.com/v1/items",
                model=DummyModel,
            )

        assert "response_body" in exc_info.value.details
        assert "bad request body" in exc_info.value.details["response_body"]

    async def test_error_body_extraction_failure_still_raises(
        self, base_service, mock_session
    ):
        """When response body can't be read, exception is still raised with empty details."""
        error = aiohttp.ClientResponseError(
            request_info=AsyncMock(), history=(), status=404
        )
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock(side_effect=error)
        mock_response.text = AsyncMock(side_effect=Exception("Cannot read body"))
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with pytest.raises(BrightcoveResourceNotFoundError) as exc_info:
            await base_service.fetch_data(
                endpoint="https://api.example.com/v1/items/999",
                model=DummyModel,
            )

        assert exc_info.value.details == {}

    async def test_error_preserves_endpoint(self, base_service, mock_session):
        mock_session.request.return_value.__aenter__.return_value = (
            _make_error_response(400, "bad")
        )

        with pytest.raises(BrightcoveBadValueError) as exc_info:
            await base_service.fetch_data(
                endpoint="https://api.example.com/v1/items/42",
                model=DummyModel,
            )

        assert exc_info.value.endpoint == "https://api.example.com/v1/items/42"

    async def test_error_chains_original_exception(self, base_service, mock_session):
        """Verify the BrightcoveError is chained from the original ClientResponseError."""
        mock_session.request.return_value.__aenter__.return_value = (
            _make_error_response(400, "bad")
        )

        with pytest.raises(BrightcoveBadValueError) as exc_info:
            await base_service.fetch_data(
                endpoint="https://api.example.com/v1/items",
                model=DummyModel,
            )

        assert isinstance(exc_info.value.__cause__, aiohttp.ClientResponseError)


# --- Retry Behavior ---


class TestFetchDataRetries:
    async def test_401_retries_then_raises(self, base_service, mock_session):
        """401 maps to BrightcoveAuthError which is retried up to 5 times."""
        mock_session.request.return_value.__aenter__.return_value = (
            _make_error_response(401, "Unauthorized")
        )

        with pytest.raises(RetryError):
            await base_service.fetch_data(
                endpoint="https://api.example.com/v1/items",
                model=DummyModel,
            )

        assert mock_session.request.call_count == 5

    async def test_connection_error_retries_then_succeeds(
        self, base_service, mock_session
    ):
        success_response = _make_success_response({"id": 6, "name": "Retry Success"})

        mock_session.request.return_value.__aenter__.side_effect = [
            aiohttp.ClientConnectionError("Connection failed"),
            success_response,
        ]

        result = await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
        )

        assert result.id == 6
        assert mock_session.request.call_count == 2

    async def test_auth_error_retries_then_succeeds(self, base_service, mock_session):
        success_response = _make_success_response({"id": 7, "name": "Auth Retry"})

        mock_session.request.return_value.__aenter__.side_effect = [
            BrightcoveAuthError("Token expired"),
            success_response,
        ]

        result = await base_service.fetch_data(
            endpoint="https://api.example.com/v1/items",
            model=DummyModel,
        )

        assert result.id == 7
        assert mock_session.request.call_count == 2

    async def test_connection_error_exhausts_all_retries(
        self, base_service, mock_session
    ):
        mock_session.request.return_value.__aenter__.side_effect = (
            aiohttp.ClientConnectionError("Connection refused")
        )

        with pytest.raises(RetryError):
            await base_service.fetch_data(
                endpoint="https://api.example.com/v1/items",
                model=DummyModel,
            )

        assert mock_session.request.call_count == 5

    async def test_non_retryable_error_is_not_retried(self, base_service, mock_session):
        """400 errors should NOT be retried — only auth and connection errors are."""
        mock_session.request.return_value.__aenter__.return_value = (
            _make_error_response(400, "Bad Request")
        )

        with pytest.raises(BrightcoveBadValueError):
            await base_service.fetch_data(
                endpoint="https://api.example.com/v1/items",
                model=DummyModel,
            )

        assert mock_session.request.call_count == 1
