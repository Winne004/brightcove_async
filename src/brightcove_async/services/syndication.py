import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.syndication_model import (
    Syndication as SyndicationModel,
)
from brightcove_async.schemas.syndication_model import SyndicationList
from brightcove_async.services.base import Base


class Syndication(Base):
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
            endpoint=f"{self.base_url}/accounts/{account_id}/mrss/syndications",
            model=SyndicationList,
        )

    async def get_syndication(
        self,
        account_id: str,
        syndication_id: str,
    ) -> SyndicationModel:
        return await self.fetch_data(
            endpoint=f"{self.base_url}/accounts/{account_id}/mrss/syndications/{syndication_id}",
            model=SyndicationModel,
        )

    async def create_syndication(
        self,
        account_id: str,
        syndication: SyndicationModel,
    ) -> SyndicationModel:
        return await self.fetch_data(
            endpoint=f"{self.base_url}/accounts/{account_id}/mrss/syndications",
            model=SyndicationModel,
            method="POST",
            payload=syndication,
        )

    async def update_syndication(
        self,
        account_id: str,
        syndication_id: str,
        syndication: SyndicationModel,
    ) -> SyndicationModel:
        return await self.fetch_data(
            endpoint=f"{self.base_url}/accounts/{account_id}/mrss/syndications/{syndication_id}",
            model=SyndicationModel,
            method="PUT",
            payload=syndication,
        )

    async def patch_syndication(
        self,
        account_id: str,
        syndication_id: str,
        syndication: SyndicationModel,
    ) -> SyndicationModel:
        return await self.fetch_data(
            endpoint=f"{self.base_url}/accounts/{account_id}/mrss/syndications/{syndication_id}",
            model=SyndicationModel,
            method="PATCH",
            payload=syndication,
        )

    async def delete_syndication(
        self,
        account_id: str,
        syndication_id: str,
    ) -> None:
        await self._delete(
            f"{self.base_url}/accounts/{account_id}/mrss/syndications/{syndication_id}"
        )

    async def get_template(
        self,
        account_id: str,
        syndication_id: str,
    ) -> str:
        return await self._get_text(
            f"{self.base_url}/accounts/{account_id}/mrss/syndications/{syndication_id}/template"
        )

    async def upload_template(
        self,
        account_id: str,
        syndication_id: str,
        content: str,
    ) -> None:
        await self._put_text(
            f"{self.base_url}/accounts/{account_id}/mrss/syndications/{syndication_id}/template",
            content,
        )
