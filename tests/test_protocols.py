"""Tests for the OAuthClientProtocol runtime checkable protocol."""

from brightcove_async.oauth.oauth import OAuthClient
from brightcove_async.protocols import OAuthClientProtocol


def test_oauthclient_is_instance_of_protocol():
    """Test that an OAuthClient instance satisfies the OAuthClientProtocol."""
    from unittest.mock import AsyncMock

    session = AsyncMock()
    client = OAuthClient("id", "secret", session)
    assert isinstance(client, OAuthClientProtocol)


def test_protocol_is_runtime_checkable():
    """Test that OAuthClientProtocol is runtime-checkable."""

    # It should already be decorated with @runtime_checkable
    assert hasattr(OAuthClientProtocol, "__protocol_attrs__") or hasattr(
        OAuthClientProtocol, "__abstractmethods__"
    )


def test_non_conforming_class_is_not_instance():
    """Test that a class lacking protocol methods is not an instance."""

    class NotOAuth:
        pass

    assert not isinstance(NotOAuth(), OAuthClientProtocol)


def test_conforming_class_is_instance():
    """Test that a class implementing all protocol methods is an instance."""

    class FakeOAuth:
        def __init__(self, client_id: str, client_secret: str, session):
            pass

        async def get_access_token(self) -> str:
            return "token"

        @property
        async def headers(self) -> dict[str, str]:
            return {}

    assert isinstance(FakeOAuth("id", "secret", None), OAuthClientProtocol)
