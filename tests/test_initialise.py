from unittest.mock import MagicMock, patch

from brightcove_async.client import BrightcoveClient
from brightcove_async.initalise import initialise_brightcove_client
from brightcove_async.oauth.oauth import OAuthClient
from brightcove_async.settings import BrightcoveBaseAPIConfig, BrightcoveOAuthCreds


def test_initialise_brightcove_client_with_defaults():
    """Test initialise_brightcove_client with default parameters."""
    with (
        patch("brightcove_async.initalise.BrightcoveOAuthCreds") as MockOAuthCreds,
        patch("brightcove_async.initalise.BrightcoveBaseAPIConfig") as MockAPIConfig,
    ):
        mock_creds = MagicMock()
        mock_creds.client_id = "test_id"
        mock_creds.client_secret = MagicMock()
        mock_creds.client_secret.get_secret_value.return_value = "test_secret"
        MockOAuthCreds.return_value = mock_creds

        mock_config = MagicMock()
        MockAPIConfig.return_value = mock_config

        with patch(
            "brightcove_async.initalise.build_service_registry",
        ) as mock_registry:
            mock_registry.return_value = {}

            client = initialise_brightcove_client()

            assert isinstance(client, BrightcoveClient)
            MockOAuthCreds.assert_called_once()
            MockAPIConfig.assert_called_once()


def test_initialise_brightcove_client_with_custom_creds():
    """Test initialise_brightcove_client with custom OAuth credentials."""
    with patch("brightcove_async.initalise.build_service_registry") as mock_registry:
        mock_registry.return_value = {}

        mock_creds = MagicMock(spec=BrightcoveOAuthCreds)
        mock_creds.client_id = "custom_id"
        mock_creds.client_secret = MagicMock()
        mock_creds.client_secret.get_secret_value.return_value = "custom_secret"

        client = initialise_brightcove_client(oauth_creds=mock_creds)

        assert isinstance(client, BrightcoveClient)
        assert client._client_id == "custom_id"
        assert client._client_secret == "custom_secret"


def test_initialise_brightcove_client_with_custom_config():
    """Test initialise_brightcove_client with custom API configuration."""
    with patch("brightcove_async.initalise.BrightcoveOAuthCreds") as MockOAuthCreds:
        mock_creds = MagicMock()
        mock_creds.client_id = "test_id"
        mock_creds.client_secret = MagicMock()
        mock_creds.client_secret.get_secret_value.return_value = "test_secret"
        MockOAuthCreds.return_value = mock_creds

        custom_config = BrightcoveBaseAPIConfig(
            cms_base_url="https://custom-cms.example.com/",
            syndication_base_url="https://custom-syndication.example.com/",
        )

        with patch(
            "brightcove_async.initalise.build_service_registry",
        ) as mock_registry:
            mock_registry.return_value = {}

            client = initialise_brightcove_client(client_config=custom_config)

            assert isinstance(client, BrightcoveClient)
            mock_registry.assert_called_once_with(custom_config)


def test_initialise_brightcove_client_uses_oauth_client():
    """Test that initialise_brightcove_client uses OAuthClient class."""
    with (
        patch("brightcove_async.initalise.BrightcoveOAuthCreds") as MockOAuthCreds,
        patch("brightcove_async.initalise.build_service_registry") as mock_registry,
    ):
        mock_creds = MagicMock()
        mock_creds.client_id = "test_id"
        mock_creds.client_secret = MagicMock()
        mock_creds.client_secret.get_secret_value.return_value = "test_secret"
        MockOAuthCreds.return_value = mock_creds

        mock_registry.return_value = {}

        client = initialise_brightcove_client()

        assert client._oauth_cls == OAuthClient


def test_initialise_brightcove_client_builds_service_registry():
    """Test that initialise_brightcove_client builds service registry."""
    with (
        patch("brightcove_async.initalise.BrightcoveOAuthCreds") as MockOAuthCreds,
        patch("brightcove_async.initalise.BrightcoveBaseAPIConfig") as MockAPIConfig,
        patch("brightcove_async.initalise.build_service_registry") as mock_registry,
    ):
        mock_creds = MagicMock()
        mock_creds.client_id = "test_id"
        mock_creds.client_secret = MagicMock()
        mock_creds.client_secret.get_secret_value.return_value = "test_secret"
        MockOAuthCreds.return_value = mock_creds

        mock_config = MagicMock()
        MockAPIConfig.return_value = mock_config

        mock_service_config = MagicMock()
        mock_registry.return_value = {"cms": mock_service_config}

        client = initialise_brightcove_client()

        mock_registry.assert_called_once_with(mock_config)
        assert "cms" in client._service_classes
        assert client._service_classes["cms"] is mock_service_config
