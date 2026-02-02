import time
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from aiohttp import BasicAuth

from brightcove_async.oauth.oauth import OAuthClient


@pytest.fixture
def mock_session():
    """Create a mock aiohttp.ClientSession."""
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture
def oauth_client(mock_session):
    """Create an OAuthClient instance with mock session."""
    return OAuthClient(
        client_id="test_client_id",
        client_secret="test_secret",
        session=mock_session,
    )


@pytest.mark.asyncio
async def test_oauth_initialization(oauth_client):
    """Test OAuthClient initializes with correct attributes."""
    assert oauth_client.client_id == "test_client_id"
    assert oauth_client.client_secret == "test_secret"
    assert oauth_client._access_token is None
    assert oauth_client._request_time == 0.0
    assert oauth_client._token_life == 240.0


@pytest.mark.asyncio
async def test_get_access_token_first_request(oauth_client, mock_session):
    """Test fetching access token for the first time."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"access_token": "new_token_123"})
    mock_response.raise_for_status = MagicMock()

    mock_session.post.return_value.__aenter__.return_value = mock_response

    token = await oauth_client.get_access_token()

    assert token == "new_token_123"
    assert oauth_client._access_token == "new_token_123"
    assert oauth_client._request_time > 0

    mock_session.post.assert_called_once()
    call_kwargs = mock_session.post.call_args.kwargs
    assert call_kwargs["url"] == "https://oauth.brightcove.com/v4/access_token"
    assert isinstance(call_kwargs["auth"], BasicAuth)


@pytest.mark.asyncio
async def test_get_access_token_uses_cached_token(oauth_client):
    """Test that cached token is used when still valid."""
    oauth_client._access_token = "cached_token"
    oauth_client._request_time = time.time()

    token = await oauth_client.get_access_token()

    assert token == "cached_token"
    oauth_client._session.post.assert_not_called()


@pytest.mark.asyncio
async def test_get_access_token_refreshes_expired_token(oauth_client, mock_session):
    """Test that expired token is refreshed."""
    oauth_client._access_token = "old_token"
    oauth_client._request_time = time.time() - 300  # 5 minutes ago

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"access_token": "refreshed_token"})
    mock_response.raise_for_status = MagicMock()

    mock_session.post.return_value.__aenter__.return_value = mock_response

    token = await oauth_client.get_access_token()

    assert token == "refreshed_token"
    assert oauth_client._access_token == "refreshed_token"
    mock_session.post.assert_called_once()


@pytest.mark.asyncio
async def test_get_access_token_raises_on_failure(oauth_client, mock_session):
    """Test that ValueError is raised when token fetch fails."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={})  # No access_token
    mock_response.raise_for_status = MagicMock()

    mock_session.post.return_value.__aenter__.return_value = mock_response

    with pytest.raises(ValueError, match="Failed to fetch access token"):
        await oauth_client.get_access_token()


@pytest.mark.asyncio
async def test_headers_property(oauth_client, mock_session):
    """Test headers property returns correctly formatted headers."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"access_token": "test_token"})
    mock_response.raise_for_status = MagicMock()

    mock_session.post.return_value.__aenter__.return_value = mock_response

    headers = await oauth_client.headers

    assert headers == {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json",
    }


@pytest.mark.asyncio
async def test_retry_on_connection_error(oauth_client, mock_session):
    """Test that connection errors are retried."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"access_token": "retry_token"})
    mock_response.raise_for_status = MagicMock()

    # First call fails, second succeeds
    mock_session.post.return_value.__aenter__.side_effect = [
        aiohttp.ClientConnectionError("Connection failed"),
        mock_response,
    ]

    token = await oauth_client.get_access_token()

    assert token == "retry_token"
    assert mock_session.post.call_count == 2


@pytest.mark.asyncio
async def test_http_error_response(oauth_client, mock_session):
    """Test handling of HTTP error responses - retries on connection errors only."""
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"error": "invalid"})
    mock_response.raise_for_status = MagicMock()  # Don't raise, just return empty

    mock_session.post.return_value.__aenter__.return_value = mock_response

    # Should raise ValueError because no access_token in response
    with pytest.raises(ValueError, match="Failed to fetch access token"):
        await oauth_client.get_access_token()
