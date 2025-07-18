import time

import aiohttp
from aiohttp import BasicAuth
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


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

    @retry(
        retry=retry_if_exception_type(
            (aiohttp.ClientConnectionError),
        ),
        wait=wait_exponential(multiplier=1, min=1, max=3),  # exponential backoff
        stop=stop_after_attempt(3),  # up to 5 retries
    )
    async def _get_access_token(self) -> None:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials"}

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
            self._access_token = json_data.get("access_token")
            self._request_time = time.time()

    async def get_access_token(self) -> str:
        if (
            not self._access_token
            or time.time() - self._request_time > self._token_life
        ):
            await self._get_access_token()

        if not self._access_token:
            raise ValueError("Failed to fetch access token.")

        return self._access_token

    @property
    async def headers(self) -> dict[str, str]:
        access_token = await self.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
