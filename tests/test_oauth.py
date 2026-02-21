"""Tests for OAuthClient token management, caching, and retry behaviour."""

import time
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from aiohttp import BasicAuth
from tenacity import RetryError

from brightcove_async.oauth.oauth import OAuthClient

OAUTH_URL = "https://oauth.brightcove.com/v4/access_token"


# ---------------------------------------------------------------------------
# Fixtures (mock_session comes from conftest)
# ---------------------------------------------------------------------------


@pytest.fixture
def oauth_client(mock_session: AsyncMock) -> OAuthClient:
    """Create an OAuthClient wired to the shared mock_session."""
    return OAuthClient(
        client_id="test_client_id",
        client_secret="test_secret",
        session=mock_session,
    )


def _mock_token_response(token: str = "new_token") -> AsyncMock:
    """Return a mock context-manager response that yields *token*."""
    resp = AsyncMock()
    resp.json = AsyncMock(return_value={"access_token": token})
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestOAuthInitialisation:
    async def test_attributes_set(self, oauth_client: OAuthClient) -> None:
        assert oauth_client.client_id == "test_client_id"
        assert oauth_client.client_secret == "test_secret"
        assert oauth_client._access_token is None
        assert oauth_client._request_time == 0.0
        assert oauth_client._token_life == 240.0

    async def test_base_url(self, oauth_client: OAuthClient) -> None:
        assert oauth_client.base_url == OAUTH_URL


# ---------------------------------------------------------------------------
# Token fetching
# ---------------------------------------------------------------------------


class TestGetAccessToken:
    async def test_first_request(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        mock_session.post.return_value.__aenter__.return_value = _mock_token_response(
            "new_token_123"
        )

        token = await oauth_client.get_access_token()

        assert token == "new_token_123"
        assert oauth_client._access_token == "new_token_123"
        assert oauth_client._request_time > 0

        mock_session.post.assert_called_once()
        call_kwargs = mock_session.post.call_args.kwargs
        assert call_kwargs["url"] == OAUTH_URL
        assert isinstance(call_kwargs["auth"], BasicAuth)

    async def test_request_includes_correct_content_type_and_grant(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        mock_session.post.return_value.__aenter__.return_value = _mock_token_response()
        await oauth_client.get_access_token()

        call_kwargs = mock_session.post.call_args.kwargs
        assert call_kwargs["headers"] == {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        assert call_kwargs["data"] == {"grant_type": "client_credentials"}

    async def test_missing_access_token_raises_value_error(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        resp = AsyncMock()
        resp.json = AsyncMock(return_value={})
        resp.raise_for_status = MagicMock()
        mock_session.post.return_value.__aenter__.return_value = resp

        with pytest.raises(ValueError, match="Failed to fetch access token"):
            await oauth_client.get_access_token()

    async def test_raise_for_status_propagates(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        resp = AsyncMock()
        resp.raise_for_status = MagicMock(
            side_effect=aiohttp.ClientResponseError(
                request_info=AsyncMock(),
                history=(),
                status=401,
            ),
        )
        mock_session.post.return_value.__aenter__.return_value = resp

        with pytest.raises(aiohttp.ClientResponseError):
            await oauth_client.get_access_token()


# ---------------------------------------------------------------------------
# Token caching
# ---------------------------------------------------------------------------


class TestTokenCaching:
    async def test_cached_token_returned_when_valid(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        oauth_client._access_token = "cached_token"
        oauth_client._request_time = time.time()

        token = await oauth_client.get_access_token()

        assert token == "cached_token"
        oauth_client._session.post.assert_not_called()  # ty:ignore[unresolved-attribute]

    async def test_expired_token_refreshed(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        oauth_client._access_token = "old_token"
        oauth_client._request_time = time.time() - 300  # 5 min ago

        mock_session.post.return_value.__aenter__.return_value = _mock_token_response(
            "refreshed_token"
        )

        token = await oauth_client.get_access_token()

        assert token == "refreshed_token"
        assert oauth_client._access_token == "refreshed_token"
        mock_session.post.assert_called_once()

    @pytest.mark.parametrize(
        ("age_seconds", "should_refresh"),
        [
            (239.0, False),  # well under 240 s lifetime
            (240.5, True),  # clearly past expiry
        ],
        ids=["under-expiry", "past-expiry"],
    )
    async def test_expiry_boundary(
        self,
        age_seconds: float,
        should_refresh: bool,
        mock_session: AsyncMock,
    ) -> None:
        client = OAuthClient("id", "secret", mock_session)
        client._access_token = "boundary_token"
        client._request_time = time.time() - age_seconds

        if should_refresh:
            mock_session.post.return_value.__aenter__.return_value = (
                _mock_token_response("new")
            )

        token = await client.get_access_token()

        if should_refresh:
            assert token == "new"
            mock_session.post.assert_called_once()
        else:
            assert token == "boundary_token"
            mock_session.post.assert_not_called()


# ---------------------------------------------------------------------------
# Headers property
# ---------------------------------------------------------------------------


class TestHeadersProperty:
    async def test_headers_after_fresh_fetch(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        mock_session.post.return_value.__aenter__.return_value = _mock_token_response(
            "test_token"
        )

        headers = await oauth_client.headers

        assert headers == {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json",
        }

    async def test_headers_with_cached_token(
        self,
        oauth_client: OAuthClient,
    ) -> None:
        oauth_client._access_token = "cached_token_123"
        oauth_client._request_time = time.time()

        headers = await oauth_client.headers
        assert headers == {
            "Authorization": "Bearer cached_token_123",
            "Content-Type": "application/json",
        }


# ---------------------------------------------------------------------------
# Retry behaviour
# ---------------------------------------------------------------------------


class TestRetryBehaviour:
    async def test_connection_error_retried(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        ok_resp = _mock_token_response("retry_token")
        mock_session.post.return_value.__aenter__.side_effect = [
            aiohttp.ClientConnectionError("Connection failed"),
            ok_resp,
        ]

        token = await oauth_client.get_access_token()

        assert token == "retry_token"
        assert mock_session.post.call_count == 2

    async def test_retry_exhaustion_raises(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        mock_session.post.return_value.__aenter__.side_effect = (
            aiohttp.ClientConnectionError("Connection refused")
        )

        with pytest.raises(RetryError):
            await oauth_client.get_access_token()

        assert mock_session.post.call_count == 3  # stop_after_attempt(3)

    async def test_http_error_in_body_not_retried(
        self,
        oauth_client: OAuthClient,
        mock_session: AsyncMock,
    ) -> None:
        """A response without access_token raises ValueError immediately."""
        resp = AsyncMock()
        resp.json = AsyncMock(return_value={"error": "invalid"})
        resp.raise_for_status = MagicMock()
        mock_session.post.return_value.__aenter__.return_value = resp

        with pytest.raises(ValueError, match="Failed to fetch access token"):
            await oauth_client.get_access_token()
