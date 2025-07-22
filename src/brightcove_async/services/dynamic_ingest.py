import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.dynamic_ingest_model import (
    GetS3UrlsResponse,
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
        video_id: str,
        video_or_asset_data: IngestMediaAssetbody,
    ) -> IngestMediaAssetResponse:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/ingest-requests",
            model=IngestMediaAssetResponse,
            method="POST",
            json=video_or_asset_data,
        )

    async def get_temporary_s3_urls(
        self,
        account_id: str,
        source_name: str,
    ) -> GetS3UrlsResponse:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{{video_id}}/upload-urls/{source_name}",
            model=GetS3UrlsResponse,
            method="GET",
            params={"source_name": source_name},
        )
