"""Tests for exception hierarchy, str formatting, and status code mapping."""

from http import HTTPStatus

import pytest

from brightcove_async.exceptions import (
    BrightcoveAuthError,
    BrightcoveBadValueError,
    BrightcoveClientError,
    BrightcoveConflictError,
    BrightcoveError,
    BrightcoveIllegalFieldError,
    BrightcoveMethodNotAllowedError,
    BrightcoveReferenceInUseError,
    BrightcoveResourceNotFoundError,
    BrightcoveServerError,
    BrightcoveTooManyRequestsError,
    BrightcoveUnknownError,
    map_status_code_to_exception,
)

# --- Exception Hierarchy ---


class TestExceptionHierarchy:
    @pytest.mark.parametrize(
        ("exc_cls", "parent_cls"),
        [
            (BrightcoveClientError, BrightcoveError),
            (BrightcoveAuthError, BrightcoveClientError),
            (BrightcoveBadValueError, BrightcoveClientError),
            (BrightcoveMethodNotAllowedError, BrightcoveClientError),
            (BrightcoveResourceNotFoundError, BrightcoveClientError),
            (BrightcoveConflictError, BrightcoveClientError),
            (BrightcoveTooManyRequestsError, BrightcoveClientError),
            (BrightcoveIllegalFieldError, BrightcoveClientError),
            (BrightcoveReferenceInUseError, BrightcoveClientError),
            (BrightcoveServerError, BrightcoveError),
            (BrightcoveUnknownError, BrightcoveServerError),
        ],
    )
    def test_subclass_relationship(
        self,
        exc_cls: type[BrightcoveError],
        parent_cls: type[BrightcoveError],
    ):
        assert issubclass(exc_cls, parent_cls)

    def test_base_inherits_from_exception(self):
        assert issubclass(BrightcoveError, Exception)

    def test_catch_any_client_error_with_base(self):
        with pytest.raises(BrightcoveClientError):
            raise BrightcoveAuthError("auth")
        with pytest.raises(BrightcoveClientError):
            raise BrightcoveConflictError("conflict")

    def test_catch_any_server_error_with_base(self):
        with pytest.raises(BrightcoveServerError):
            raise BrightcoveUnknownError("server")

    def test_catch_all_with_brightcove_error(self):
        with pytest.raises(BrightcoveError):
            raise BrightcoveAuthError("auth")
        with pytest.raises(BrightcoveError):
            raise BrightcoveUnknownError("server")


# --- BrightcoveError attributes and __str__ ---


class TestBrightcoveErrorFormatting:
    def test_stores_all_attributes(self):
        err = BrightcoveError(
            "test",
            status_code=400,
            endpoint="/test",
            details={"key": "val"},
        )
        assert err.message == "test"
        assert err.status_code == 400
        assert err.endpoint == "/test"
        assert err.details == {"key": "val"}

    def test_details_defaults_to_empty_dict(self):
        assert BrightcoveError("test").details == {}

    def test_str_message_only(self):
        assert str(BrightcoveError("Something went wrong")) == "Something went wrong"

    def test_str_with_status_code(self):
        result = str(BrightcoveError("Fail", status_code=404))
        assert "Fail" in result
        assert "status_code=404" in result

    def test_str_with_endpoint(self):
        result = str(BrightcoveError("Fail", endpoint="/v1/videos"))
        assert "endpoint='/v1/videos'" in result

    def test_str_with_details(self):
        result = str(BrightcoveError("Fail", details={"response_body": "not found"}))
        assert "details=" in result
        assert "response_body" in result

    def test_str_all_fields(self):
        result = str(
            BrightcoveError(
                "API failed",
                status_code=500,
                endpoint="/v1/accounts/123/videos",
                details={"response_body": "internal error"},
            )
        )
        assert "API failed" in result
        assert "status_code=500" in result
        assert "endpoint='/v1/accounts/123/videos'" in result
        assert "details=" in result


# --- Status Code Mapping ---


class TestMapStatusCodeToException:
    @pytest.mark.parametrize(
        ("status", "expected_cls"),
        [
            (401, BrightcoveAuthError),
            (400, BrightcoveBadValueError),
            (405, BrightcoveMethodNotAllowedError),
            (404, BrightcoveResourceNotFoundError),
            (409, BrightcoveConflictError),
            (429, BrightcoveTooManyRequestsError),
            (500, BrightcoveUnknownError),
        ],
        ids=["401", "400", "405", "404", "409", "429", "500"],
    )
    def test_mapped_codes(self, status, expected_cls):
        assert map_status_code_to_exception(status) == expected_cls

    @pytest.mark.parametrize(
        ("status", "expected_cls"),
        [
            (401, BrightcoveAuthError),
            (400, BrightcoveBadValueError),
            (405, BrightcoveMethodNotAllowedError),
            (404, BrightcoveResourceNotFoundError),
            (409, BrightcoveConflictError),
            (429, BrightcoveTooManyRequestsError),
            (500, BrightcoveUnknownError),
        ],
        ids=["401", "400", "405", "404", "409", "429", "500"],
    )
    def test_mapped_codes_with_httpstatus(self, status, expected_cls):
        assert map_status_code_to_exception(HTTPStatus(status)) == expected_cls

    @pytest.mark.parametrize(
        "status",
        [418, 422, 502, 503, 504],
        ids=[
            "418-teapot",
            "422-unprocessable",
            "502-bad-gw",
            "503-unavailable",
            "504-timeout",
        ],
    )
    def test_unmapped_codes_fall_back_to_unknown(self, status):
        assert map_status_code_to_exception(status) == BrightcoveUnknownError

    def test_all_mapped_codes_are_brightcove_errors(self):
        for code in [401, 400, 405, 404, 409, 429, 500]:
            assert issubclass(map_status_code_to_exception(code), BrightcoveError)
