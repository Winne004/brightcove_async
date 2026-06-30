from brightcove_async.registry import ServiceConfig, build_service_registry
from brightcove_async.services.analytics import Analytics
from brightcove_async.services.cms import CMS
from brightcove_async.services.dynamic_ingest import DynamicIngest
from brightcove_async.services.images import Images
from brightcove_async.services.live import Live
from brightcove_async.services.playback import Playback
from brightcove_async.services.policy import Policy
from brightcove_async.services.syndication import Syndication
from brightcove_async.settings import BrightcoveBaseAPIConfig


def test_service_config_creation():
    """Test ServiceConfig dataclass creation."""
    config = ServiceConfig(
        cls=CMS,
        base_url="https://cms.api.brightcove.com/v1/accounts/",
        requests_per_second=4,
    )

    assert config.cls == CMS
    assert config.base_url == "https://cms.api.brightcove.com/v1/accounts/"
    assert config.requests_per_second == 4


def test_service_config_defaults():
    """Test ServiceConfig default values."""
    config = ServiceConfig(
        cls=CMS,
        base_url="https://cms.api.brightcove.com/v1/accounts/",
    )

    assert config.requests_per_second == 10


def test_build_service_registry():
    """Test build_service_registry creates correct registry."""
    config = BrightcoveBaseAPIConfig()

    registry = build_service_registry(config)

    assert "cms" in registry
    assert "syndication" in registry
    assert "analytics" in registry
    assert "dynamic_ingest" in registry


def test_build_service_registry_cms_config():
    """Test CMS service configuration in registry."""
    config = BrightcoveBaseAPIConfig()
    registry = build_service_registry(config)

    cms_config = registry["cms"]

    assert cms_config.cls == CMS
    assert cms_config.base_url == config.cms_base_url
    assert cms_config.requests_per_second == 4


def test_build_service_registry_syndication_config():
    """Test Syndication service configuration in registry."""
    config = BrightcoveBaseAPIConfig()
    registry = build_service_registry(config)

    syndication_config = registry["syndication"]

    assert syndication_config.cls == Syndication
    assert syndication_config.base_url == config.syndication_base_url
    assert syndication_config.requests_per_second == 10


def test_build_service_registry_analytics_config():
    """Test Analytics service configuration in registry."""
    config = BrightcoveBaseAPIConfig()
    registry = build_service_registry(config)

    analytics_config = registry["analytics"]

    assert analytics_config.cls == Analytics
    assert analytics_config.base_url == config.analytics_base_url
    assert analytics_config.requests_per_second == 10


def test_build_service_registry_dynamic_ingest_config():
    """Test DynamicIngest service configuration in registry."""
    config = BrightcoveBaseAPIConfig()
    registry = build_service_registry(config)

    di_config = registry["dynamic_ingest"]

    assert di_config.cls == DynamicIngest
    assert di_config.base_url == config.dynamic_ingest_base_url
    assert di_config.requests_per_second == 10


def test_build_service_registry_images_config():
    """Test Images service configuration in registry."""
    config = BrightcoveBaseAPIConfig()
    registry = build_service_registry(config)

    images_config = registry["images"]

    assert images_config.cls == Images
    assert images_config.base_url == config.images_base_url
    assert images_config.requests_per_second == 10


def test_build_service_registry_live_config():
    """Test Live service configuration in registry."""
    config = BrightcoveBaseAPIConfig()
    registry = build_service_registry(config)

    live_config = registry["live"]

    assert live_config.cls == Live
    assert live_config.base_url == config.live_base_url
    assert live_config.requests_per_second == 10


def test_build_service_registry_playback_config():
    """Test Playback service configuration in registry."""
    config = BrightcoveBaseAPIConfig()
    registry = build_service_registry(config)

    playback_config = registry["playback"]

    assert playback_config.cls == Playback
    assert playback_config.base_url == config.playback_base_url
    assert playback_config.requests_per_second == 10


def test_build_service_registry_policy_config():
    """Test Policy service configuration in registry."""
    config = BrightcoveBaseAPIConfig()
    registry = build_service_registry(config)

    policy_config = registry["policy"]

    assert policy_config.cls == Policy
    assert policy_config.base_url == config.policy_base_url
    assert policy_config.requests_per_second == 10


def test_build_service_registry_custom_urls():
    """Test build_service_registry with custom URLs."""
    config = BrightcoveBaseAPIConfig(
        cms_base_url="https://custom-cms.example.com/",
        syndication_base_url="https://custom-syndication.example.com/",
        analytics_base_url="https://custom-analytics.example.com/",
        dynamic_ingest_base_url="https://custom-ingest.example.com/",
        ingest_profiles_base_url="https://custom-profiles.example.com/",
    )

    registry = build_service_registry(config)

    assert registry["cms"].base_url == "https://custom-cms.example.com/"
    assert registry["syndication"].base_url == "https://custom-syndication.example.com/"
    assert registry["analytics"].base_url == "https://custom-analytics.example.com/"
    assert registry["dynamic_ingest"].base_url == "https://custom-ingest.example.com/"
    assert (
        registry["ingest_profiles"].base_url == "https://custom-profiles.example.com/"
    )


def test_service_registry_returns_dict():
    """Test that build_service_registry returns a dictionary."""
    config = BrightcoveBaseAPIConfig()
    registry = build_service_registry(config)

    assert isinstance(registry, dict)
    assert set(registry.keys()) == {
        "cms",
        "syndication",
        "analytics",
        "dynamic_ingest",
        "ingest_profiles",
        "audience",
        "images",
        "live",
        "playback",
        "policy",
    }
