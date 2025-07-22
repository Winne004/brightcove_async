from dataclasses import dataclass

from brightcove_async.services.analytics import Analytics
from brightcove_async.services.base import Base
from brightcove_async.services.cms import CMS
from brightcove_async.services.dynamic_ingest import DynamicIngest
from brightcove_async.services.syndication import Syndication
from brightcove_async.settings import BrightcoveBaseAPIConfig


@dataclass
class ServiceConfig:
    cls: type[Base]
    base_url: str
    requests_per_second: int = 10
    kwargs: dict | None = None


def build_service_registry(config: BrightcoveBaseAPIConfig) -> dict[str, ServiceConfig]:
    return {
        "cms": ServiceConfig(
            cls=CMS,
            base_url=config.cms_base_url,
            requests_per_second=4,
        ),
        "syndication": ServiceConfig(
            cls=Syndication,
            base_url=config.syndication_base_url,
        ),
        "analytics": ServiceConfig(cls=Analytics, base_url=config.analytics_base_url),
        "dynamic_ingest": ServiceConfig(
            cls=DynamicIngest,
            base_url=config.dynamic_ingest_base_url,
        ),
    }
