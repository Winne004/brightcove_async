from brightcove_async.client import BrightcoveClient
from brightcove_async.oauth.oauth import OAuthClient
from brightcove_async.registry import build_service_registry
from brightcove_async.settings import (
    BrightcoveBaseAPIConfig,
    BrightcoveClientConfig,
    BrightcoveOAuthCreds,
)


def initialise_brightcove_client(
    oauth_creds: BrightcoveOAuthCreds | None = None,
    client_config: BrightcoveBaseAPIConfig | None = None,
    http_config: BrightcoveClientConfig | None = None,
    user_agent: str | None = None,
    default_headers: dict[str, str] | None = None,
) -> BrightcoveClient:
    """Initialise the Brightcove client with OAuth credentials.

    Args:
        oauth_creds: OAuth client credentials. Read from the environment
            (``CLIENT_ID``/``CLIENT_SECRET``) when omitted.
        client_config: API base URL configuration.
        http_config: HTTP transport configuration (User-Agent, connection
            limit). Read from ``BRIGHTCOVE_``-prefixed environment variables
            when omitted.
        user_agent: Overrides the User-Agent for every request. Takes
            precedence over ``http_config.user_agent``. Use this to work around
            Akamai edge blocks that reject the default client as bot traffic.
        default_headers: Extra headers sent on every request (e.g. to satisfy
            Akamai edge rules).

    Returns the configured BrightcoveClient.
    """
    client_credentials = BrightcoveOAuthCreds() if oauth_creds is None else oauth_creds  # ty:ignore[missing-argument]

    client_config = (
        BrightcoveBaseAPIConfig() if client_config is None else client_config
    )

    http_config = BrightcoveClientConfig() if http_config is None else http_config

    services_registry = build_service_registry(client_config)

    return BrightcoveClient(
        client_id=client_credentials.client_id,
        client_secret=client_credentials.client_secret.get_secret_value(),
        oauth_cls=OAuthClient,
        services_registry=services_registry,
        user_agent=user_agent or http_config.user_agent,
        default_headers=default_headers,
        connection_limit=http_config.connection_limit,
    )
