import time

import aiohttp
from aiohttp import BasicAuth
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from brightcove_async.exceptions import BrightcoveAuthError


class OAuthClient:
    base_url = "https://oauth.brightcove.com/v4/access_token"

    def __init__(
        self, client_id: str, client_secret: str, session: aiohttp.ClientSession
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: str | None = None
        self._request_time = 0.0
        self._token_life = 240.0  # Token expires after 4 minutes
        self._session: aiohttp.ClientSession = session

    def invalidate_token(self) -> None:
        self._access_token = None

    @retry(
        retry=retry_if_exception_type(
            (aiohttp.ClientConnectionError, BrightcoveAuthError),
        ),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _get_access_token(self) -> None:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials"}

        try:
            async with (
                self._session.post(
                    url=self.base_url,
                    headers=headers,
                    data=data,
                    auth=BasicAuth(self.client_id, self.client_secret),
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response,
            ):
                response.raise_for_status()
                json_data = await response.json()
                access_token = json_data.get("access_token")
                if not access_token:
                    raise BrightcoveAuthError(
                        message="OAuth server returned no access_token",
                        status_code=200,
                    )
                self._access_token = access_token
                self._request_time = time.time()
        except aiohttp.ClientResponseError as e:
            raise BrightcoveAuthError(
                message=str(e.message), status_code=e.status
            ) from e

    async def get_access_token(self) -> str:
        if (
            not self._access_token
            or time.time() - self._request_time > self._token_life
        ):
            await self._get_access_token()

        if not self._access_token:
            raise BrightcoveAuthError(message="Failed to fetch access token.")

        return self._access_token

    @property
    async def headers(self) -> dict[str, str]:
        access_token = await self.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
