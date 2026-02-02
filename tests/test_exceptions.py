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
    BrightcoveResourceNotFoundError,
    BrightcoveServerError,
    BrightcoveTooManyRequestsError,
    BrightcoveUnknownError,
    map_status_code_to_exception,
)


def test_exception_hierarchy():
    """Test that exception classes have correct inheritance."""
    # Base exception
    assert issubclass(BrightcoveError, Exception)

    # Client errors inherit from BrightcoveClientError
    assert issubclass(BrightcoveClientError, BrightcoveError)
    assert issubclass(BrightcoveAuthError, BrightcoveClientError)
    assert issubclass(BrightcoveBadValueError, BrightcoveClientError)
    assert issubclass(BrightcoveMethodNotAllowedError, BrightcoveClientError)
    assert issubclass(BrightcoveResourceNotFoundError, BrightcoveClientError)
    assert issubclass(BrightcoveConflictError, BrightcoveClientError)
    assert issubclass(BrightcoveTooManyRequestsError, BrightcoveClientError)
    assert issubclass(BrightcoveIllegalFieldError, BrightcoveClientError)

    # Server errors inherit from BrightcoveServerError
    assert issubclass(BrightcoveServerError, BrightcoveError)
    assert issubclass(BrightcoveUnknownError, BrightcoveServerError)


def test_map_status_code_unauthorized():
    """Test mapping 401 status to BrightcoveAuthError."""
    exc_class = map_status_code_to_exception(401)
    assert exc_class == BrightcoveAuthError

    exc_class = map_status_code_to_exception(HTTPStatus.UNAUTHORIZED)
    assert exc_class == BrightcoveAuthError


def test_map_status_code_bad_request():
    """Test mapping 400 status to BrightcoveBadValueError."""
    exc_class = map_status_code_to_exception(400)
    assert exc_class == BrightcoveBadValueError

    exc_class = map_status_code_to_exception(HTTPStatus.BAD_REQUEST)
    assert exc_class == BrightcoveBadValueError


def test_map_status_code_method_not_allowed():
    """Test mapping 405 status to BrightcoveMethodNotAllowedError."""
    exc_class = map_status_code_to_exception(405)
    assert exc_class == BrightcoveMethodNotAllowedError

    exc_class = map_status_code_to_exception(HTTPStatus.METHOD_NOT_ALLOWED)
    assert exc_class == BrightcoveMethodNotAllowedError


def test_map_status_code_not_found():
    """Test mapping 404 status to BrightcoveResourceNotFoundError."""
    exc_class = map_status_code_to_exception(404)
    assert exc_class == BrightcoveResourceNotFoundError

    exc_class = map_status_code_to_exception(HTTPStatus.NOT_FOUND)
    assert exc_class == BrightcoveResourceNotFoundError


def test_map_status_code_conflict():
    """Test mapping 409 status to BrightcoveConflictError."""
    exc_class = map_status_code_to_exception(409)
    assert exc_class == BrightcoveConflictError

    exc_class = map_status_code_to_exception(HTTPStatus.CONFLICT)
    assert exc_class == BrightcoveConflictError


def test_map_status_code_too_many_requests():
    """Test mapping 429 status to BrightcoveTooManyRequestsError."""
    exc_class = map_status_code_to_exception(429)
    assert exc_class == BrightcoveTooManyRequestsError

    exc_class = map_status_code_to_exception(HTTPStatus.TOO_MANY_REQUESTS)
    assert exc_class == BrightcoveTooManyRequestsError


def test_map_status_code_internal_server_error():
    """Test mapping 500 status to BrightcoveUnknownError."""
    exc_class = map_status_code_to_exception(500)
    assert exc_class == BrightcoveUnknownError

    exc_class = map_status_code_to_exception(HTTPStatus.INTERNAL_SERVER_ERROR)
    assert exc_class == BrightcoveUnknownError


def test_map_status_code_unknown():
    """Test mapping unknown status code defaults to BrightcoveUnknownError."""
    exc_class = map_status_code_to_exception(418)  # I'm a teapot
    assert exc_class == BrightcoveUnknownError

    exc_class = map_status_code_to_exception(502)  # Bad Gateway
    assert exc_class == BrightcoveUnknownError

    # Note: 999 is not a valid HTTPStatus, so we skip testing it
    # The function expects valid HTTP status codes


def test_exceptions_can_be_raised():
    """Test that exception classes can be instantiated and raised."""
    with pytest.raises(BrightcoveAuthError):
        raise BrightcoveAuthError("Authentication failed")

    with pytest.raises(BrightcoveBadValueError):
        raise BrightcoveBadValueError("Bad value provided")

    with pytest.raises(BrightcoveResourceNotFoundError):
        raise BrightcoveResourceNotFoundError("Resource not found")

    with pytest.raises(BrightcoveUnknownError):
        raise BrightcoveUnknownError("Unknown error occurred")


def test_catch_base_exception():
    """Test that base exception can catch all Brightcove exceptions."""
    with pytest.raises(BrightcoveError):
        raise BrightcoveAuthError("Auth error")

    with pytest.raises(BrightcoveError):
        raise BrightcoveUnknownError("Unknown error")


def test_catch_client_errors():
    """Test that BrightcoveClientError catches all 4xx errors."""
    with pytest.raises(BrightcoveClientError):
        raise BrightcoveAuthError("Auth error")

    with pytest.raises(BrightcoveClientError):
        raise BrightcoveResourceNotFoundError("Not found")

    with pytest.raises(BrightcoveClientError):
        raise BrightcoveConflictError("Conflict")


def test_catch_server_errors():
    """Test that BrightcoveServerError catches all 5xx errors."""
    with pytest.raises(BrightcoveServerError):
        raise BrightcoveUnknownError("Server error")
