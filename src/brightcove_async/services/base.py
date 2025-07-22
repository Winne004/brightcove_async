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

from brightcove_async.exceptions import BrightcoveAuthError
from brightcove_async.protocols import OAuthClientProtocol

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


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

    @retry(
        retry=retry_if_exception_type(
            (aiohttp.ClientConnectionError, BrightcoveAuthError),
        ),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        stop=stop_after_attempt(5),
    )
    async def fetch_data(
        self,
        endpoint: str,
        model: type[T],
        method: str = "GET",
        params: dict | None = None,
        headers: dict | None = None,
        json: BaseModel | None = None,
    ) -> T:
        if headers is None:
            headers = await self._oauth.headers

        body = (
            json.model_dump(
                exclude_none=True,
                exclude_unset=True,
                exclude_defaults=True,
            )
            if json
            else None
        )

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
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                if HTTPStatus(e.status) == HTTPStatus.UNAUTHORIZED:
                    raise BrightcoveAuthError(
                        "Authentication failed. Please check your credentials.",
                    ) from e

            json_data = await response.json()
            return model.model_validate(json_data, strict=False)
