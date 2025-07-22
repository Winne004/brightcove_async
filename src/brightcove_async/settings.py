from dataclasses import dataclass
from pydantic import SecretStr
from pydantic_settings import BaseSettings

from brightcove_async.services.base import Base


@dataclass
class ServiceConfig:
    cls: type[Base]
    base_url: str
    requests_per_second: int = 10
    kwargs: dict | None = None


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
    dynamic_ingest_base_url: str = "https://ingest.api.brightcove.com/v1/accounts/"
