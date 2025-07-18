from typing import Protocol, runtime_checkable

import aiohttp


@runtime_checkable
class OAuthClientProtocol(Protocol):
    def __init__(
        self, client_id: str, client_secret: str, session: aiohttp.ClientSession
    ) -> None: ...

    async def get_access_token(self) -> str: ...

    @property
    async def headers(self) -> dict[str, str]: ...
