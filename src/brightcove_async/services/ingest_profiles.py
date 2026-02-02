import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.ingest_profiles_model import IngestProfile
from brightcove_async.services.base import Base


class IngestProfiles(Base):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 4,
    ) -> None:
        super().__init__(session, oauth, base_url, limit)

    async def get_ingest_profiles(self, account_id: str) -> IngestProfile:
        return await self.fetch_data(
            endpoint=f"{self.base_url}accounts/{account_id}/profiles",
            model=IngestProfile,
        )
