"""Tests for schema models validation and serialization."""

import pytest
from pydantic import ValidationError

from brightcove_async.schemas.analytics_model import (
    Dimensions,
    Format,
    GetAlltimeVideoViewsResponse,
    GetAnalyticsReportResponse,
    GetAvailableDateRangeResponse,
    Items,
    Summary,
    Timeline,
    TimeSeries,
    Where,
)
from brightcove_async.schemas.cms_model import (
    Economics,
    Playlist,
    PlaylistType,
    State,
    State3,
    Video,
    VideoArray,
    VideoCount,
)
from brightcove_async.schemas.cms_model.Image import Sources
from brightcove_async.schemas.cms_model.Videofields import CustomField, StandardField
from brightcove_async.schemas.ingest_profiles_model import (
    DigitalMaster,
    DynamicOrigin,
    DynamicOriginImage,
    IngestProfile,
)
from brightcove_async.schemas.syndication_model import (
    Explicit,
    Syndication,
    SyndicationList,
    Type,
)

# --- Analytics Models ---


class TestSummary:
    def test_all_optional_fields(self):
        summary = Summary()
        assert summary.ad_mode_begin is None
        assert summary.video_view is None

    def test_with_values(self):
        summary = Summary(video_view=1000, play_request=500)
        assert summary.video_view == 1000
        assert summary.play_request == 500


class TestTimeSeries:
    def test_valid_time_series(self):
        ts = TimeSeries(type="flat", values=[0.1, 0.5, 0.9])
        assert ts.type == "flat"
        assert len(ts.values) == 3

    def test_empty_values(self):
        ts = TimeSeries(type="empty", values=[])
        assert ts.values == []

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            TimeSeries()


class TestTimeline:
    def test_valid_timeline(self):
        ts = TimeSeries(type="flat", values=[0.1])
        tl = Timeline(timeline=ts)
        assert tl.timeline.type == "flat"


class TestGetAnalyticsReportResponse:
    def test_valid_response(self):
        resp = GetAnalyticsReportResponse(
            item_count=1,
            items=[Items(video="vid1", video_view=100)],
            summary=Summary(),
        )
        assert resp.item_count == 1
        assert len(resp.items) == 1
        assert resp.items[0].video == "vid1"

    def test_empty_items(self):
        resp = GetAnalyticsReportResponse(
            item_count=0,
            items=[],
            summary=Summary(),
        )
        assert resp.item_count == 0
        assert resp.items == []


class TestGetAvailableDateRangeResponse:
    def test_valid_response(self):
        resp = GetAvailableDateRangeResponse(
            reconciled_from="2024-01-01",
            reconciled_to="2024-12-31",
        )
        assert resp.reconciled_from == "2024-01-01"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            GetAvailableDateRangeResponse()


class TestGetAlltimeVideoViewsResponse:
    def test_valid(self):
        resp = GetAlltimeVideoViewsResponse(alltime_video_views=5000)
        assert resp.alltime_video_views == 5000

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            GetAlltimeVideoViewsResponse()


class TestDimensions:
    def test_dimension_values(self):
        assert Dimensions.video == "video"
        assert Dimensions.country == "country"
        assert Dimensions.date == "date"

    def test_format_values(self):
        assert Format.csv == "csv"
        assert Format.json == "json"

    def test_where_values(self):
        assert Where.video == "video"
        assert Where.device_type == "device_type"


# --- Syndication Models ---


class TestSyndicationModel:
    def test_minimal_syndication(self):
        s = Syndication(name="Test Feed", type=Type.google)
        assert s.name == "Test Feed"
        assert s.type == Type.google
        assert s.id is None

    def test_full_syndication(self):
        s = Syndication(
            id="syn123",
            name="Full Feed",
            type=Type.universal,
            include_all_content=True,
            title="My Feed Title",
            description="A test feed",
            language="en",
            explicit=Explicit.no,
        )
        assert s.id == "syn123"
        assert s.include_all_content is True
        assert s.explicit == Explicit.no

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            Syndication()

    def test_type_enum_values(self):
        assert Type.google.value == "google"
        assert Type.universal.value == "universal"
        assert Type.roku.value == "roku"


class TestSyndicationList:
    def test_empty_list(self):
        sl = SyndicationList(root=[])
        assert sl.root == []

    def test_with_items(self):
        sl = SyndicationList(
            root=[
                Syndication(name="Feed1", type=Type.google),
                Syndication(name="Feed2", type=Type.mp4),
            ]
        )
        assert len(sl.root) == 2


# --- Ingest Profiles Models ---


class TestIngestProfile:
    def test_valid_profile(self):
        profile = IngestProfile(
            version=1,
            name="test-profile",
            display_name="Test Profile",
            description="A test profile",
            account_id=12345,
            brightcove_standard=True,
            date_created=1700000000,
            date_last_modified=1700000001,
            digital_master=DigitalMaster(rendition="passthrough", distribute=True),
            id="prof123",
        )
        assert profile.name == "test-profile"
        assert profile.digital_master.distribute is True
        assert profile.renditions == []
        assert profile.packages == []
        assert profile.dynamic_origin is None

    def test_with_dynamic_origin(self):
        profile = IngestProfile(
            version=2,
            name="dynamic-profile",
            display_name="Dynamic",
            description="Profile with dynamic origin",
            account_id=12345,
            brightcove_standard=False,
            date_created=1700000000,
            date_last_modified=1700000001,
            digital_master=DigitalMaster(rendition="passthrough", distribute=False),
            dynamic_origin=DynamicOrigin(
                renditions=["rendition1"],
                images=[DynamicOriginImage(label="poster", height=720, width=1280)],
            ),
            id="prof456",
        )
        assert profile.dynamic_origin is not None
        assert len(profile.dynamic_origin.images) == 1


# --- CMS Models ---


class TestVideoArray:
    def test_empty_array(self):
        va = VideoArray(root=[])
        assert va.root == []

    def test_ensure_list_validator_with_single_dict(self):
        """Test that the field_validator wraps a single video dict in a list."""
        va = VideoArray.model_validate([{"name": "Test Video", "id": "vid1"}])
        assert len(va.root) == 1

    def test_ensure_list_validator_with_list(self):
        va = VideoArray.model_validate([{"name": "V1"}, {"name": "V2"}])
        assert len(va.root) == 2


class TestVideoCount:
    def test_with_count(self):
        vc = VideoCount(count=42)
        assert vc.count == 42

    def test_with_none(self):
        vc = VideoCount()
        assert vc.count is None


class TestPlaylist:
    def test_minimal_playlist(self):
        p = Playlist()
        assert p.id is None
        assert p.name is None

    def test_playlist_type_enum(self):
        assert PlaylistType.EXPLICIT == "EXPLICIT"
        assert PlaylistType.ALPHABETICAL == "ALPHABETICAL"


class TestEconomics:
    def test_values(self):
        assert Economics.AD_SUPPORTED == "AD_SUPPORTED"
        assert Economics.FREE == "FREE"


class TestState:
    def test_values(self):
        assert State.ACTIVE == "ACTIVE"
        assert State.INACTIVE == "INACTIVE"


class TestVideo:
    def test_minimal_video(self):
        v = Video()
        assert v.id is None
        assert v.name is None

    def test_video_with_fields(self):
        v = Video(
            id="vid123",
            name="My Video",
            state=State3.ACTIVE,
            economics=Economics.AD_SUPPORTED,
        )
        assert v.id == "vid123"
        assert v.name == "My Video"


# --- CMS Sub-Models ---


class TestSources:
    def test_valid_source(self):
        s = Sources(src="https://example.com/image.jpg")
        assert s.src == "https://example.com/image.jpg"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            Sources()


class TestCustomField:
    def test_defaults(self):
        cf = CustomField()
        assert cf.description is None
        assert cf.required is False
        assert cf.type is None

    def test_with_values(self):
        cf = CustomField(
            id="genre",
            display_name="Genre",
            type="enum",
            enum_values=["action", "comedy"],
        )
        assert cf.id == "genre"
        assert cf.enum_values is not None
        assert len(cf.enum_values) == 2


class TestStandardField:
    def test_defaults(self):
        sf = StandardField()
        assert sf.id is None
        assert sf.required is None

    def test_with_values(self):
        sf = StandardField(id="tags", description="Video tags")
        assert sf.id == "tags"
