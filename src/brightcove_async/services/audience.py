import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.audience_model import (
    GetLeadsResponse,
    GetViewEventsResponse,
)
from brightcove_async.schemas.params import GetLeadsParams, GetViewEventsParams
from brightcove_async.services.base import Base


class Audience(Base):
    @property
    def base_url(self) -> str:
        return "https://audience.api.brightcove.com/v1"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 10,
    ) -> None:
        super().__init__(session=session, oauth=oauth, base_url=base_url, limit=limit)

    async def get_leads(
        self,
        account_id: str,
        params: GetLeadsParams | None = None,
    ) -> GetLeadsResponse:
        """Fetches leads for an account."""
        return await self.fetch_data(
            endpoint=f"{self.base_url}/accounts/{account_id}/leads",
            model=GetLeadsResponse,
            params=params.serialize_params() if params else None,
        )

    async def get_view_events(
        self,
        account_id: str,
        params: GetViewEventsParams | None = None,
    ) -> GetViewEventsResponse:
        """Fetches view events for an account."""
        return await self.fetch_data(
            endpoint=f"{self.base_url}/accounts/{account_id}/view_events",
            model=GetViewEventsResponse,
            params=params.serialize_params() if params else None,
        )
