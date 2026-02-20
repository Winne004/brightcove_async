from http import HTTPStatus


class BrightcoveError(Exception):
    """Base exception for Brightcove API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        endpoint: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.endpoint = endpoint
        self.details = details or {}

    def __str__(self) -> str:
        """Return a formatted error message with context."""
        parts = [self.message]

        if self.status_code is not None:
            parts.append(f"status_code={self.status_code}")

        if self.endpoint is not None:
            parts.append(f"endpoint='{self.endpoint}'")

        if self.details:
            details_str = ", ".join(f"{k}={v!r}" for k, v in self.details.items())
            parts.append(f"details={{{details_str}}}")

        return ", ".join(parts)


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


class BrightcoveServerError(BrightcoveError):
    """Base class for server errors."""


class BrightcoveUnknownError(BrightcoveServerError):
    """Raised when there is an unknown issue with Brightcove."""


def map_status_code_to_exception(status_code: int) -> type[BrightcoveError]:
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

    status = (
        status_code if isinstance(status_code, HTTPStatus) else HTTPStatus(status_code)
    )

    return mapping.get(status, BrightcoveUnknownError)
