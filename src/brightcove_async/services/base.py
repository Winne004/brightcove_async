import logging
from abc import ABC
from http import HTTPStatus
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
    map_status_code_to_exception,
)
from brightcove_async.protocols import OAuthClientProtocol

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

brightcove_retry = retry(
    retry=retry_if_exception_type(
        (BrightcoveConnectionError, BrightcoveAuthError),
    ),
    wait=wait_exponential(multiplier=1, min=1, max=3),
    stop=stop_after_attempt(5),
)


class Base(ABC):
    """Abstract base class all API wrapper classes have to inherit from.

    Attributes
    ----------
    base_url : str
        Base URL for API calls (must be implemented by subclass).

    """

    _limit: int = 10

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 10,
    ) -> None:
        """Args:.

        oauth (OAuth): OAuth instance to use for the API calls.
        query (str, optional): Query string to be used for API calls.

        """
        self._oauth: OAuthClientProtocol = oauth
        self._session: aiohttp.ClientSession = session
        self._base_url: str = base_url
        self._limit = limit
        self._limiter: AsyncLimiter | None = None

    @property
    def limiter(self) -> AsyncLimiter:
        """AsyncLimiter instance to control the rate of API calls."""
        if self._limiter is None:
            self._limiter = AsyncLimiter(max_rate=self._limit, time_period=1)
        return self._limiter

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
            raise exc_class(
                message=str(e.message),
                status_code=e.status,
                endpoint=endpoint,
                details=error_details,
            ) from e

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
            headers = await self._oauth.headers

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

        try:
            async with (
                self.limiter,
                self._session.request(
                    method,
                    endpoint,
                    params=params,
                    headers=headers,
                    json=body,
                ) as response,
            ):
                await self._raise_for_status(response, endpoint)
                json_data = await response.json()
                return model.model_validate(json_data, strict=False)
        except aiohttp.ClientConnectionError as e:
            raise BrightcoveConnectionError(message=str(e), endpoint=endpoint) from e

    @brightcove_retry
    async def _delete(self, endpoint: str) -> None:
        try:
            headers = await self._oauth.headers
            async with (
                self.limiter,
                self._session.request("DELETE", endpoint, headers=headers) as response,
            ):
                await self._raise_for_status(response, endpoint)
        except aiohttp.ClientConnectionError as e:
            raise BrightcoveConnectionError(message=str(e), endpoint=endpoint) from e

    @brightcove_retry
    async def _get_text(self, endpoint: str) -> str:
        try:
            headers = await self._oauth.headers
            async with (
                self.limiter,
                self._session.request("GET", endpoint, headers=headers) as response,
            ):
                await self._raise_for_status(response, endpoint)
                return await response.text()
        except aiohttp.ClientConnectionError as e:
            raise BrightcoveConnectionError(message=str(e), endpoint=endpoint) from e

    @brightcove_retry
    async def _put_text(self, endpoint: str, content: str) -> None:
        try:
            headers = {**await self._oauth.headers, "Content-Type": "text/plain"}
            async with (
                self.limiter,
                self._session.request(
                    "PUT", endpoint, headers=headers, data=content
                ) as response,
            ):
                await self._raise_for_status(response, endpoint)
        except aiohttp.ClientConnectionError as e:
            raise BrightcoveConnectionError(message=str(e), endpoint=endpoint) from e
