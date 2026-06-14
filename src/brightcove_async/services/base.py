import contextlib
import logging
from abc import ABC
from typing import TypeVar

import aiohttp
from aiolimiter import AsyncLimiter
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from brightcove_async.exceptions import (
    BrightcoveAuthError,
    BrightcoveConnectionError,
    BrightcoveError,
    BrightcoveTooManyRequestsError,
    map_status_code_to_exception,
)
from brightcove_async.protocols import OAuthClientProtocol

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

# Exceptions that indicate the OAuth token fetch itself failed.
# aiohttp.ClientResponseError: OAuth endpoint returned a non-2xx status (e.g. 503).
# aiohttp.ClientConnectionError: Unable to connect to the OAuth endpoint.
# ValueError: OAuth endpoint returned 200 but with no access_token in the body.
_OAUTH_FETCH_ERRORS = (
    aiohttp.ClientResponseError,
    aiohttp.ClientConnectionError,
    ValueError,
)


def _compute_wait(retry_state) -> float:
    """Use Retry-After from 429 responses; fall back to exponential backoff."""
    exc = retry_state.outcome.exception()
    if isinstance(exc, BrightcoveTooManyRequestsError) and exc.retry_after:
        return exc.retry_after
    return wait_exponential(multiplier=1, min=1, max=30)(retry_state)


brightcove_retry = retry(
    retry=retry_if_exception_type(
        (
            BrightcoveConnectionError,
            BrightcoveAuthError,
            BrightcoveTooManyRequestsError,
        ),
    ),
    wait=_compute_wait,
    stop=stop_after_attempt(2),
)


class Base(ABC):
    """Abstract base class all API wrapper classes have to inherit from.

    Attributes
    ----------
    base_url : str
        Base URL for API calls (must be implemented by subclass).

    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: float = 10,
    ) -> None:
        """Args:.

        oauth (OAuth): OAuth instance to use for the API calls.
        query (str, optional): Query string to be used for API calls.

        """
        self._oauth: OAuthClientProtocol = oauth
        self._session: aiohttp.ClientSession = session
        self._base_url: str = base_url
        self._limit: float = limit
        self._limiter: AsyncLimiter | None = None
        self._time_period: float = 1.0

    @property
    def limiter(self) -> AsyncLimiter:
        """AsyncLimiter instance to control the rate of API calls."""
        if self._limiter is None:
            self._limiter = AsyncLimiter(
                max_rate=self._limit, time_period=self._time_period
            )
        return self._limiter

    @property
    def time_period(self) -> float:
        """Time period in seconds for the rate limiter."""
        return self._time_period

    @time_period.setter
    def time_period(self, value: float) -> None:
        """Set the time period for the rate limiter and reset the limiter instance.

        Args:
            value (float): The new time period in seconds.

        """
        if value <= 0:
            raise ValueError("time_period must be greater than 0")
        self._time_period = value
        self._limiter = None  # Reset limiter to apply new time period on next access

    @property
    def max_requests(self) -> float:
        """Max requests allowed in the time period for the rate limiter."""
        return self._limit

    @max_requests.setter
    def max_requests(self, value: float) -> None:
        """Set the max requests for the rate limiter and reset the limiter instance.

        Args:
            value (float): The new max requests allowed in the time period.

        """
        if value <= 0:
            raise ValueError("max_requests must be greater than 0")
        self._limit = value
        self._limiter = None  # Reset limiter to apply new max requests on next access

    @property
    def base_url(self) -> str:
        """Property that must be defined in any subclass to indicate the base API URL."""
        return self._base_url

    async def _raise_for_status(
        self, response: aiohttp.ClientResponse, endpoint: str
    ) -> None:
        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            error_details: dict = {}
            try:
                error_body = await response.text()
                error_details = {"response_body": error_body}
            except Exception:
                pass
            exc_class: type[BrightcoveError] = map_status_code_to_exception(e.status)
            kwargs: dict = dict(
                message=str(e.message),
                status_code=e.status,
                endpoint=endpoint,
                details=error_details,
            )
            if exc_class is BrightcoveTooManyRequestsError:
                retry_after: float | None = None
                raw = response.headers.get("Retry-After")
                if raw:
                    with contextlib.suppress(ValueError):
                        retry_after = float(raw)
                kwargs["retry_after"] = retry_after
            raise exc_class(**kwargs) from e

    def _convert_oauth_error(self, e: Exception) -> BrightcoveError:
        """Convert a raw OAuth fetch error into a Brightcove exception and clear the token."""
        self._oauth.invalidate_token()
        if isinstance(e, aiohttp.ClientConnectionError):
            return BrightcoveConnectionError(message=str(e))
        if isinstance(e, aiohttp.ClientResponseError):
            return BrightcoveAuthError(message=str(e), status_code=e.status)
        return BrightcoveAuthError(message=str(e))

    async def _get_oauth_headers(self) -> dict:
        """Fetch OAuth headers, converting raw errors to Brightcove exceptions."""
        try:
            return await self._oauth.headers
        except _OAUTH_FETCH_ERRORS as e:
            raise self._convert_oauth_error(e) from e

    async def _send_request(
        self,
        method: str,
        endpoint: str,
        headers: dict,
        params: dict | None = None,
        json_body: dict | list | None = None,
        data: str | None = None,
        return_json: bool | None = True,
    ) -> dict | list | str | None:
        """Execute a rate-limited request and map errors.

        return_json=True  → parse and return JSON body
        return_json=False → return raw text body
        return_json=None  → no body (DELETE)
        """
        try:
            async with (
                self.limiter,
                self._session.request(
                    method,
                    endpoint,
                    params=params,
                    headers=headers,
                    json=json_body,
                    data=data,
                ) as response,
            ):
                await self._raise_for_status(response, endpoint)
                if return_json is None:
                    return None
                return await response.json() if return_json else await response.text()
        except BrightcoveAuthError:
            self._oauth.invalidate_token()
            raise
        except aiohttp.ClientConnectionError as e:
            raise BrightcoveConnectionError(message=str(e), endpoint=endpoint) from e

    @brightcove_retry
    async def fetch_data(
        self,
        endpoint: str,
        model: type[T],
        method: str = "GET",
        params: dict | None = None,
        headers: dict | None = None,
        payload: BaseModel | None = None,
    ) -> T:
        if headers is None:
            headers = await self._get_oauth_headers()

        body = (
            payload.model_dump(
                mode="json",
                exclude_none=True,
                exclude_unset=True,
                exclude_defaults=True,
            )
            if payload
            else None
        )

        json_data = await self._send_request(
            method, endpoint, headers, params=params, json_body=body
        )
        return model.model_validate(json_data, strict=False)

    @brightcove_retry
    async def _delete(self, endpoint: str) -> None:
        headers = await self._get_oauth_headers()
        await self._send_request("DELETE", endpoint, headers, return_json=None)

    @brightcove_retry
    async def _get_text(self, endpoint: str) -> str:
        headers = await self._get_oauth_headers()
        result = await self._send_request("GET", endpoint, headers, return_json=False)
        return result  # type: ignore[return-value]

    @brightcove_retry
    async def _put_text(self, endpoint: str, content: str) -> None:
        base_headers = await self._get_oauth_headers()
        headers = {**base_headers, "Content-Type": "text/plain"}
        await self._send_request(
            "PUT", endpoint, headers, data=content, return_json=None
        )

    @brightcove_retry
    async def _put_empty(self, endpoint: str) -> None:
        headers = await self._get_oauth_headers()
        await self._send_request("PUT", endpoint, headers, return_json=None)
