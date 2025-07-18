import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.syndication_model import (
    SyndicationList,
    Syndication as SyndicationModel,
)
from brightcove_async.services.base import Base


class Syndication(Base):
    @property
    def base_url(self) -> str:
        return "https://edge.social.api.brightcove.com/v1/accounts/"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 10,
    ) -> None:
        super().__init__(session=session, oauth=oauth, base_url=base_url, limit=limit)

    async def get_all_syndications(self, account_id: str) -> SyndicationList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/mrss/syndications",
            model=SyndicationList,
        )

    async def get_syndication(
        self,
        account_id: str,
        syndication_id: str,
    ) -> SyndicationModel:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/mrss/syndications/{syndication_id}",
            model=SyndicationModel,
        )
