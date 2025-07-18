import asyncio

import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.cms_model import (
    AudioTrack,
    AudioTracks,
    Channel,
    ChannelAffiliateList,
    ChannelList,
    ContractList,
    CreateVideoRequestBodyFields,
    CustomFields,
    DigitalMaster,
    ImageList,
    IngestJobs,
    IngestJobStatus,
    Playlist,
    Video,
    VideoArray,
    VideoAssets,
    VideoCount,
    VideoShareList,
    VideoSourcesList,
    VideoVariant,
    VideoVariants,
)
from brightcove_async.services.base import Base


class CMS(Base):
    _page_limit = 100

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 4,
    ) -> None:
        super().__init__(session=session, oauth=oauth, base_url=base_url, limit=limit)

    async def get_videos(
        self,
        account_id: str,
        params: dict[str, str] | None = None,
    ) -> VideoArray:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos",
            model=VideoArray,
            params=params,
        )

    async def create_video(
        self, account_id: str, video_data: CreateVideoRequestBodyFields
    ) -> Video:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos",
            model=Video,
            method="POST",
            json=video_data,
        )

    async def get_videos_for_account(
        self,
        account_id: str,
        page_size: int = 25,
        number_of_pages: int | None = None,
    ) -> VideoArray:
        results = VideoArray(root=[])

        if page_size > self._page_limit:
            raise ValueError("page_size must be less than or equal to 100")

        count = await self.get_video_count(account_id)

        if count.count is None or count.count == 0:
            return results

        total_pages = (
            (count.count + page_size - 1) // page_size
            if number_of_pages is None
            else number_of_pages
        )

        tasks = [
            self.fetch_data(
                endpoint=f"{self.base_url}{account_id}/videos",
                model=VideoArray,
                params={"limit": page_size, "offset": i * page_size},
            )
            for i in range(total_pages)
        ]

        pages = await asyncio.gather(*tasks)

        for page in pages:
            results.root.extend(page.root)

        return results

    async def get_video_count(self, account_id: str) -> VideoCount:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/counts/videos",
            model=VideoCount,
        )

    async def get_video_fields(self, account_id: str) -> CustomFields:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/video_fields/custom_fields",
            model=CustomFields,
        )

    async def get_video_by_id(
        self,
        account_id: str,
        video_ids: list[str],
    ) -> VideoAssets:
        if len(video_ids) > 10:
            raise ValueError("video_ids must contain 10 or fewer IDs")
        video_ids_str = ",".join(video_ids)
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_ids_str}",
            model=VideoAssets,
        )

    async def get_video_sources(
        self,
        account_id: str,
        video_id: str,
    ) -> VideoSourcesList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/sources",
            model=VideoSourcesList,
        )

    async def get_video_images(
        self,
        account_id: str,
        video_id: str,
    ) -> ImageList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/images",
            model=ImageList,
        )

    async def get_video_variants(
        self,
        account_id: str,
        video_id: str,
    ) -> VideoVariants:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/variants",
            model=VideoVariants,
        )

    async def get_video_variant(
        self,
        account_id: str,
        video_id: str,
        variant_id: str,
    ) -> VideoVariant:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/variants/{variant_id}",
            model=VideoVariant,
        )

    async def get_video_audio_tracks(
        self,
        account_id: str,
        video_id: str,
    ) -> AudioTracks:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/audio_tracks",
            model=AudioTracks,
        )

    async def get_video_audio_track(
        self,
        account_id: str,
        video_id: str,
        audio_track_id: str,
    ) -> AudioTrack:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/audio_tracks/{audio_track_id}",
            model=AudioTrack,
        )

    async def get_digital_master_info(
        self,
        account_id: str,
        video_id: str,
    ) -> DigitalMaster:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/digital_master",
            model=DigitalMaster,
        )

    async def get_playlists_for_video(
        self,
        account_id: str,
        video_id: str,
    ) -> Playlist:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/references",
            model=Playlist,
        )

    async def get_status_of_ingest_jobs(
        self, account_id: str, video_id: str
    ) -> IngestJobs:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/ingest_jobs",
            model=IngestJobs,
        )

    async def get_ingest_job_status(
        self, account_id: str, video_id: str, job_id: str
    ) -> IngestJobStatus:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/ingest_jobs/{job_id}",
            model=IngestJobStatus,
        )

    async def list_channels(
        self,
        account_id: str,
        params: dict[str, str] | None = None,
    ) -> ChannelList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/channels",
            model=ChannelList,
            params=params,
        )

    async def get_channel_details(
        self,
        account_id: str,
        channel_id: str,
    ) -> Channel:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/channels/{channel_id}",
            model=Channel,
        )

    async def list_channel_affiliates(
        self,
        account_id: str,
        channel_id: str,
    ) -> ChannelAffiliateList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/channels/{channel_id}/members",
            model=ChannelAffiliateList,
        )

    async def list_contracts(
        self,
        account_id: str,
        channel_id: str,
    ) -> ContractList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/channels/{channel_id}/contracts",
            model=ContractList,
        )

    async def get_contract(
        self,
        account_id: str,
        channel_id: str,
        contract_id: str,
    ) -> ContractList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/channels/{channel_id}/contracts/{contract_id}",
            model=ContractList,
        )

    async def list_shares(
        self,
        account_id: str,
        video_id: str,
    ) -> VideoShareList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/shares",
            model=VideoShareList,
        )
