from dataclasses import dataclass

from brightcove_async.services.analytics import Analytics
from brightcove_async.services.audience import Audience
from brightcove_async.services.base import Base
from brightcove_async.services.cms import CMS
from brightcove_async.services.dynamic_ingest import DynamicIngest
from brightcove_async.services.images import Images
from brightcove_async.services.ingest_profiles import IngestProfiles
from brightcove_async.services.live import Live
from brightcove_async.services.playback import Playback
from brightcove_async.services.policy import Policy
from brightcove_async.services.syndication import Syndication
from brightcove_async.settings import BrightcoveBaseAPIConfig


@dataclass
class ServiceConfig:
    cls: type[Base]
    base_url: str
    requests_per_second: int = 10


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
        "ingest_profiles": ServiceConfig(
            cls=IngestProfiles,
            base_url=config.ingest_profiles_base_url,
            requests_per_second=4,
        ),
        "audience": ServiceConfig(
            cls=Audience,
            base_url=config.audience_base_url,
        ),
        "images": ServiceConfig(
            cls=Images,
            base_url=config.images_base_url,
        ),
        "live": ServiceConfig(
            cls=Live,
            base_url=config.live_base_url,
        ),
        "playback": ServiceConfig(
            cls=Playback,
            base_url=config.playback_base_url,
        ),
        "policy": ServiceConfig(
            cls=Policy,
            base_url=config.policy_base_url,
        ),
    }
