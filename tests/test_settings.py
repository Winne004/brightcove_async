"""Tests for settings module (BrightcoveOAuthCreds and BrightcoveBaseAPIConfig)."""

from brightcove_async.settings import BrightcoveBaseAPIConfig


class TestBrightcoveBaseAPIConfig:
    """Tests for BrightcoveBaseAPIConfig default values and overrides."""

    def test_default_cms_base_url(self):
        config = BrightcoveBaseAPIConfig()
        assert config.cms_base_url == "https://cms.api.brightcove.com/v1/accounts/"

    def test_default_syndication_base_url(self):
        config = BrightcoveBaseAPIConfig()
        assert (
            config.syndication_base_url
            == "https://edge.social.api.brightcove.com/v1/accounts/"
        )

    def test_default_analytics_base_url(self):
        config = BrightcoveBaseAPIConfig()
        assert config.analytics_base_url == "https://analytics.api.brightcove.com/v1"

    def test_default_dynamic_ingest_base_url(self):
        config = BrightcoveBaseAPIConfig()
        assert (
            config.dynamic_ingest_base_url
            == "https://ingest.api.brightcove.com/v1/accounts/"
        )

    def test_default_ingest_profiles_base_url(self):
        config = BrightcoveBaseAPIConfig()
        assert (
            config.ingest_profiles_base_url
            == "https://ingestion.api.brightcove.com/v1/"
        )

    def test_custom_urls(self):
        config = BrightcoveBaseAPIConfig(
            cms_base_url="https://custom.com/cms/",
            syndication_base_url="https://custom.com/syn/",
            analytics_base_url="https://custom.com/analytics/",
            dynamic_ingest_base_url="https://custom.com/di/",
            ingest_profiles_base_url="https://custom.com/ip/",
        )
        assert config.cms_base_url == "https://custom.com/cms/"
        assert config.syndication_base_url == "https://custom.com/syn/"
        assert config.analytics_base_url == "https://custom.com/analytics/"
        assert config.dynamic_ingest_base_url == "https://custom.com/di/"
        assert config.ingest_profiles_base_url == "https://custom.com/ip/"

    def test_partial_override(self):
        """Test overriding only some URLs while keeping defaults."""
        config = BrightcoveBaseAPIConfig(
            cms_base_url="https://custom.com/cms/",
        )
        assert config.cms_base_url == "https://custom.com/cms/"
        assert (
            config.syndication_base_url
            == "https://edge.social.api.brightcove.com/v1/accounts/"
        )
