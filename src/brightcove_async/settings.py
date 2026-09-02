from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BrightcoveOAuthCreds(BaseSettings):
    """Settings for the client."""

    client_secret: SecretStr
    client_id: str


class BrightcoveClientConfig(BaseSettings):
    """HTTP transport configuration for the client.

    These knobs exist mainly to work around Akamai's edge suite, which fronts
    the Brightcove APIs and blocks requests it treats as bot traffic (returning
    an ``errors.edgesuite.net`` page). Overriding the ``User-Agent`` and/or
    sending extra default headers is the usual fix.

    Values can be supplied programmatically or via ``BRIGHTCOVE_``-prefixed
    environment variables, e.g. ``BRIGHTCOVE_USER_AGENT``.
    """

    model_config = SettingsConfigDict(env_prefix="BRIGHTCOVE_")

    # None => fall back to the built-in "brightcove_async/<version>" UA.
    user_agent: str | None = None
    # Max simultaneous connections for the underlying aiohttp connector.
    connection_limit: int = 100


class BrightcoveBaseAPIConfig(BaseSettings):
    """Base API configuration for Brightcove."""

    cms_base_url: str = "https://cms.api.brightcove.com/v1/accounts/"
    syndication_base_url: str = "https://social.api.brightcove.com/v1"
    analytics_base_url: str = "https://analytics.api.brightcove.com/v1"
    dynamic_ingest_base_url: str = "https://ingest.api.brightcove.com/v1/accounts/"
    ingest_profiles_base_url: str = "https://ingestion.api.brightcove.com/v1/"
    audience_base_url: str = "https://audience.api.brightcove.com/v1"
    images_base_url: str = "https://images.brightcovecdn.com"
    live_base_url: str = "https://api.live.brightcove.com"
    playback_base_url: str = "https://edge.api.brightcove.com/playback/v1"
    policy_base_url: str = "https://policy.api.brightcove.com/v1"
