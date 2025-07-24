from http import HTTPStatus


class BrightcoveError(Exception):
    """Base exception for Brightcove API errors."""


class BrightcoveClientError(BrightcoveError):
    """Base class for 4xx errors."""


class BrightcoveAuthError(BrightcoveClientError):
    """Raised when authentication with the Brightcove API fails."""


class BrightcoveBadValueError(BrightcoveClientError):
    """Raised when a bad value is provided to the Brightcove API."""


class BrightcoveMethodNotAllowedError(BrightcoveClientError):
    """Raised when the http method specified is not allowed for a resource."""


class BrightcoveResourceNotFoundError(BrightcoveClientError):
    """Raised when a requested resource is not found in the Brightcove API."""


class BrightcoveReferenceInUseError(BrightcoveClientError):
    """Raised when a reference is already in use in the Brightcove API."""


class BrightcoveConflictError(BrightcoveClientError):
    """Raised when the request could not be processed because of conflict
    in the current state of the resource.

    """


class BrightcoveIllegalFieldError(BrightcoveClientError):
    """Raised when an illegal field is used in a Brightcove API request."""


class BrightcoveTooManyRequestsError(BrightcoveClientError):
    """Raised when too many requests are made to the Brightcove API."""


class BrightcoveServerError(Exception):
    """Base class for server errors."""


class BrightcoveUnknownError(BrightcoveServerError):
    """Raised when there is an unknown issue with Brightcove."""


def map_status_code_to_exception(status_code: int) -> type[Exception]:
    """Map HTTP status codes to Brightcove exception classes using HTTPStatus."""
    mapping = {
        HTTPStatus.UNAUTHORIZED: BrightcoveAuthError,
        HTTPStatus.BAD_REQUEST: BrightcoveBadValueError,
        HTTPStatus.METHOD_NOT_ALLOWED: BrightcoveMethodNotAllowedError,
        HTTPStatus.NOT_FOUND: BrightcoveResourceNotFoundError,
        HTTPStatus.CONFLICT: BrightcoveConflictError,
        HTTPStatus.TOO_MANY_REQUESTS: BrightcoveTooManyRequestsError,
        HTTPStatus.INTERNAL_SERVER_ERROR: BrightcoveUnknownError,
    }

    status = HTTPStatus(status_code)

    return mapping.get(status, BrightcoveUnknownError)
