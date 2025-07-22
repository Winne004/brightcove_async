class BrightcoveError(Exception):
    """Base exception for Brightcove API errors."""

    pass


class BrightcoveAuthError(BrightcoveError):
    """Raised when authentication with the Brightcove API fails."""

    pass
