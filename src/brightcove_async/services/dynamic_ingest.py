import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.dynamic_ingest_model import (
    IngestMediaAssetbody,
    IngestMediaAssetResponse,
)
from brightcove_async.services.base import Base


class DynamicIngest(Base):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 10,
    ) -> None:
        super().__init__(session=session, oauth=oauth, base_url=base_url, limit=limit)

    async def ingest_videos_and_assets(
        self,
        account_id: str,
        video_or_asset_data: IngestMediaAssetbody,
    ) -> IngestMediaAssetResponse:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos",
            model=IngestMediaAssetResponse,
            method="POST",
            json=video_or_asset_data,
        )
