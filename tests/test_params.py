"""Tests for schema params serialization and model validation."""

import pytest
from pydantic import ValidationError
from ty_extensions import Unknown

from brightcove_async.schemas.params import (
    GetAnalyticsReportParams,
    GetLivestreamAnalyticsParams,
    GetVideoCountParams,
    GetVideosQueryParams,
    ParamsBase,
)


class TestParamsBase:
    """Tests for the ParamsBase class."""

    def test_serialize_params_excludes_none(self):
        """Test that None values are excluded from serialized params."""

        class TestParams(ParamsBase):
            a: str | None = None
            b: int | None = None

        params = TestParams(a="hello")
        result: dict[Unknown, Unknown] = params.serialize_params()
        assert result == {"a": "hello"}
        assert "b" not in result

    def test_serialize_params_includes_all_set(self):
        """Test that all set values are included."""

        class TestParams(ParamsBase):
            x: str | None = None
            y: int | None = None

        params = TestParams(x="val", y=42)
        result: dict[Unknown, Unknown] = params.serialize_params()
        assert result == {"x": "val", "y": 42}

    def test_serialize_params_empty(self):
        """Test serialization with no values set."""

        class TestParams(ParamsBase):
            a: str | None = None

        params = TestParams()
        result: dict[Unknown, Unknown] = params.serialize_params()
        assert result == {}


class TestGetVideosQueryParams:
    """Tests for GetVideosQueryParams."""

    def test_defaults_are_none(self):
        params = GetVideosQueryParams()
        assert params.limit is None
        assert params.offset is None
        assert params.sort is None
        assert params.q is None
        assert params.query is None

    def test_serialize_with_values(self):
        params = GetVideosQueryParams(limit=10, offset=20, q="tags:nature")
        result: dict[Unknown, Unknown] = params.serialize_params()
        assert result == {"limit": 10, "offset": 20, "q": "tags:nature"}

    def test_serialize_excludes_unset_fields(self):
        params = GetVideosQueryParams(limit=5)
        result: dict[Unknown, Unknown] = params.serialize_params()
        assert result == {"limit": 5}
        assert "offset" not in result
        assert "sort" not in result


class TestGetVideoCountParams:
    """Tests for GetVideoCountParams."""

    def test_default_q_is_none(self):
        params = GetVideoCountParams()
        assert params.q is None

    def test_serialize_with_q(self):
        params = GetVideoCountParams(q="state:ACTIVE")
        result = params.serialize_params()
        assert result == {"q": "state:ACTIVE"}

    def test_serialize_empty(self):
        params = GetVideoCountParams()
        result = params.serialize_params()
        assert result == {}


class TestGetAnalyticsReportParams:
    """Tests for GetAnalyticsReportParams."""

    def test_required_fields(self):
        params = GetAnalyticsReportParams(
            accounts="acc123",
            dimensions="video",
        )
        assert params.accounts == "acc123"
        assert params.dimensions == "video"

    def test_from_field_alias(self):
        """Test that 'from_' serializes to 'from' via alias."""
        params = GetAnalyticsReportParams(
            accounts="acc123",
            dimensions="video",
            from_="2024-01-01",
        )
        result = params.serialize_params()
        assert "from" in result
        assert result["from"] == "2024-01-01"
        assert "from_" not in result

    def test_format_field_alias(self):
        """Test that 'format_' serializes to 'format' via alias."""
        params = GetAnalyticsReportParams(
            accounts="acc123",
            dimensions="video",
            format_="csv",
        )
        result = params.serialize_params()
        assert "format" in result
        assert result["format"] == "csv"
        assert "format_" not in result

    def test_all_optional_fields(self):
        params = GetAnalyticsReportParams(
            accounts="acc123",
            dimensions="video",
            where="video==12345",
            limit=100,
            sort="video_view",
            offset=0,
            fields="video_view,video_impression",
            from_="2024-01-01",
            to="2024-12-31",
            format_="json",
            reconciled=True,
        )
        result = params.serialize_params()
        assert result["accounts"] == "acc123"
        assert result["where"] == "video==12345"
        assert result["limit"] == 100
        assert result["reconciled"] is True

    def test_missing_required_fields_raises(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            GetAnalyticsReportParams()  # ty: ignore[missing-argument]

    def test_from_as_integer(self):
        """Test that from_ accepts integer (epoch ms)."""
        params = GetAnalyticsReportParams(
            accounts="acc123",
            dimensions="video",
            from_=1704067200000,
        )
        result = params.serialize_params()
        assert result["from"] == 1704067200000


class TestGetLivestreamAnalyticsParams:
    """Tests for GetLivestreamAnalyticsParams."""

    def test_required_fields(self):
        params = GetLivestreamAnalyticsParams(
            dimensions="video",
            metrics="alive_ss_ad_start",
            where="video==123",
        )
        assert params.dimensions == "video"
        assert params.metrics == "alive_ss_ad_start"
        assert params.where == "video==123"

    def test_serialize_with_optional_fields(self):
        params = GetLivestreamAnalyticsParams(
            dimensions="video",
            metrics="alive_ss_ad_start",
            where="video==123",
            bucket_limit=10,
            bucket_duration="1h",
            from_="2024-01-01",
            to="2024-12-31",
        )
        result = params.serialize_params()
        assert result["bucket_limit"] == 10
        assert result["bucket_duration"] == "1h"
        assert result["from"] == "2024-01-01"
        assert result["to"] == "2024-12-31"

    def test_missing_required_fields_raises(self):
        with pytest.raises(ValidationError):
            GetLivestreamAnalyticsParams(dimensions="video")  # ty: ignore[missing-argument]
