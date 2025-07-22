from brightcove_async.client import BrightcoveClient
from brightcove_async.oauth.oauth import OAuthClient
from brightcove_async.settings import BrightcoveBaseAPIConfig, BrightcoveOAuthCreds


def initialise_brightcove_client(
    oauth_creds: BrightcoveOAuthCreds | None = None,
    client_config: BrightcoveBaseAPIConfig | None = None,
) -> BrightcoveClient:
    """Initialise the Brightcove client with OAuth credentials.
    Returns the configured OAuthClient.
    """
    client_credentials = BrightcoveOAuthCreds() if oauth_creds is None else oauth_creds  # type: ignore[ReportCallIssueType]

    client_config = (
        BrightcoveBaseAPIConfig() if client_config is None else client_config
    )  # type: ignore[ReportCallIssueType]

    return BrightcoveClient(
        client_id=client_credentials.client_id,
        client_secret=client_credentials.client_secret.get_secret_value(),
        oauth_cls=OAuthClient,
        cms_base_url=client_config.cms_base_url,
        syndication_base_url=client_config.syndication_base_url,
        analytics_base_url=client_config.analytics_base_url,
        dynamic_ingest_base_url=client_config.dynamic_ingest_base_url,
    )
