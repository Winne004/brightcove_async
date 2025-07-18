from pydantic import SecretStr
from pydantic_settings import BaseSettings


class BrightcoveOAuthCreds(BaseSettings):
    """
    Settings for the client.
    """

    client_secret: SecretStr
    client_id: str


class BrightcoveBaseAPIConfig(BaseSettings):
    """
    Base API configuration for Brightcove.
    """

    cms_base_url: str = "https://cms.api.brightcove.com/v1/accounts/"
    syndication_base_url: str = "https://edge.social.api.brightcove.com/v1/accounts/"
    analytics_base_url: str = "https://analytics.api.brightcove.com/v1"
