import asyncio

import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.cms_model import (
    ApproveContractFields,
    AudioTrack,
    AudioTracks,
    Channel,
    ChannelAffiliateList,
    ChannelList,
    Contract,
    ContractList,
    CreateVideoRequestBodyFields,
    CustomField,
    CustomFields,
    CustomFieldUpdate,
    DigitalMaster,
    DynamicRenditionList,
    Folder,
    FolderCreateFields,
    FolderList,
    FolderUpdateFields,
    ImageList,
    IngestJobs,
    IngestJobStatus,
    LabelPath,
    LabelsList,
    LabelUpdate,
    Manifest,
    ManifestList,
    Playlist,
    PlaylistArray,
    PlaylistCount,
    PlaylistInputFields,
    RemoteAssetBody,
    ShareVideoRequest,
    Subscription,
    SubscriptionCreateFields,
    SubscriptionList,
    UpdateAudioTrackFields,
    UpdateChannelFields,
    UpdateVideoRequestBodyFields,
    Video,
    VideoArray,
    VideoAsset,
    VideoAssetList,
    VideoCount,
    VideoCountInPlaylist,
    VideoFields,
    VideoShare,
    VideoShareList,
    VideoSourcesList,
    VideoVariant,
    VideoVariants,
)
from brightcove_async.schemas.params import (
    GetVideoCountParams,
    GetVideosQueryParams,
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

    # ── Videos ────────────────────────────────────────────────────────────────

    async def get_videos(
        self,
        account_id: str,
        params: GetVideosQueryParams | None = None,
    ) -> VideoArray:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos",
            model=VideoArray,
            params=params.serialize_params() if params else None,
        )

    async def create_video(
        self, account_id: str, video_data: CreateVideoRequestBodyFields
    ) -> Video:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos",
            model=Video,
            method="POST",
            payload=video_data,
        )

    async def update_video(
        self, account_id: str, video_id: str, video_data: UpdateVideoRequestBodyFields
    ) -> Video:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}",
            model=Video,
            method="PATCH",
            payload=video_data,
        )

    async def delete_video(self, account_id: str, video_ids: list[str]) -> None:
        if len(video_ids) == 0:
            raise ValueError("video_ids must contain at least one ID")
        video_ids_str = ",".join(video_ids)
        await self._delete(f"{self.base_url}{account_id}/videos/{video_ids_str}")

    async def get_videos_for_account(
        self,
        account_id: str,
        page_size: int = 25,
        number_of_pages: int | None = None,
        params: GetVideosQueryParams | None = None,
    ) -> VideoArray:
        results = VideoArray(root=[])

        if page_size > self._page_limit:
            raise ValueError("page_size must be less than or equal to 100")

        if number_of_pages is not None:
            total_pages = number_of_pages
        else:
            video_count_params = GetVideoCountParams(q=params.q) if params else None
            count = await self.get_video_count(account_id, params=video_count_params)
            if count.count is None or count.count == 0:
                return results
            total_pages = (count.count + page_size - 1) // page_size

        tasks = [
            self.fetch_data(
                endpoint=f"{self.base_url}{account_id}/videos",
                model=VideoArray,
                params={
                    **(params.serialize_params() if params else {}),
                    "limit": page_size,
                    "offset": i * page_size,
                },
            )
            for i in range(total_pages)
        ]

        pages = await asyncio.gather(*tasks)

        for page in pages:
            results.root.extend(page.root)

        return results

    async def get_video_count(
        self, account_id: str, params: GetVideoCountParams | None = None
    ) -> VideoCount:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/counts/videos",
            model=VideoCount,
            params=params.serialize_params() if params else None,
        )

    async def get_video_by_id(
        self,
        account_id: str,
        video_ids: list[str],
    ) -> VideoArray:
        if len(video_ids) > 10:
            raise ValueError("video_ids must contain 10 or fewer IDs")
        if len(video_ids) == 0:
            raise ValueError("video_ids must contain at least one ID")

        video_ids_str = ",".join(video_ids)

        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_ids_str}",
            model=VideoArray,
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

    async def delete_video_image(
        self, account_id: str, video_id: str, label: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/image_sources/{label}"
        )

    async def get_clear_video(self, account_id: str, video_id: str) -> Video:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/clear_videos/{video_id}",
            model=Video,
        )

    async def get_video_clear_sources(
        self, account_id: str, video_id: str
    ) -> VideoSourcesList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/clear_sources",
            model=VideoSourcesList,
        )

    # ── Video Variants ─────────────────────────────────────────────────────────

    async def get_video_variants(
        self,
        account_id: str,
        video_id: str,
    ) -> VideoVariants:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/variants",
            model=VideoVariants,
        )

    async def create_video_variant(
        self, account_id: str, video_id: str, variant_data: VideoVariant
    ) -> VideoVariant:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/variants",
            model=VideoVariant,
            method="POST",
            payload=variant_data,
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

    async def update_video_variant(
        self,
        account_id: str,
        video_id: str,
        language: str,
        variant_data: VideoVariant,
    ) -> VideoVariant:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/variants/{language}",
            model=VideoVariant,
            method="PATCH",
            payload=variant_data,
        )

    async def delete_video_variant(
        self, account_id: str, video_id: str, language: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/variants/{language}"
        )

    # ── Audio Tracks ───────────────────────────────────────────────────────────

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

    async def update_video_audio_track(
        self,
        account_id: str,
        video_id: str,
        audio_track_id: str,
        track_data: UpdateAudioTrackFields,
    ) -> AudioTrack:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/audio_tracks/{audio_track_id}",
            model=AudioTrack,
            method="PATCH",
            payload=track_data,
        )

    async def delete_video_audio_track(
        self, account_id: str, video_id: str, audio_track_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/audio_tracks/{audio_track_id}"
        )

    # ── Digital Master ─────────────────────────────────────────────────────────

    async def get_digital_master_info(
        self,
        account_id: str,
        video_id: str,
    ) -> DigitalMaster:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/digital_master",
            model=DigitalMaster,
        )

    async def delete_digital_master(self, account_id: str, video_id: str) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/digital_master"
        )

    # ── Ingest Jobs ────────────────────────────────────────────────────────────

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

    # ── Playlist References ────────────────────────────────────────────────────

    async def get_playlists_for_video(
        self,
        account_id: str,
        video_id: str,
    ) -> Playlist:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/references",
            model=Playlist,
        )

    async def remove_video_from_all_playlists(
        self, account_id: str, video_id: str
    ) -> None:
        await self._delete(f"{self.base_url}{account_id}/videos/{video_id}/references")

    # ── Playlists ──────────────────────────────────────────────────────────────

    async def get_playlists(
        self, account_id: str, params: dict | None = None
    ) -> PlaylistArray:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/playlists",
            model=PlaylistArray,
            params=params,
        )

    async def create_playlist(
        self, account_id: str, playlist_data: PlaylistInputFields
    ) -> Playlist:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/playlists",
            model=Playlist,
            method="POST",
            payload=playlist_data,
        )

    async def get_playlist_count(self, account_id: str) -> PlaylistCount:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/counts/playlists",
            model=PlaylistCount,
        )

    async def get_playlist(self, account_id: str, playlist_id: str) -> Playlist:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/playlists/{playlist_id}",
            model=Playlist,
        )

    async def update_playlist(
        self,
        account_id: str,
        playlist_id: str,
        playlist_data: PlaylistInputFields,
    ) -> Playlist:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/playlists/{playlist_id}",
            model=Playlist,
            method="PATCH",
            payload=playlist_data,
        )

    async def delete_playlist(self, account_id: str, playlist_id: str) -> None:
        await self._delete(f"{self.base_url}{account_id}/playlists/{playlist_id}")

    async def get_videos_in_playlist(
        self, account_id: str, playlist_id: str
    ) -> VideoArray:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/playlists/{playlist_id}/videos",
            model=VideoArray,
        )

    async def get_video_count_in_playlist(
        self, account_id: str, playlist_id: str
    ) -> VideoCountInPlaylist:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/counts/playlists/{playlist_id}/videos",
            model=VideoCountInPlaylist,
        )

    # ── Custom Fields ──────────────────────────────────────────────────────────

    async def get_all_video_fields(self, account_id: str) -> VideoFields:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/video_fields",
            model=VideoFields,
        )

    async def get_video_fields(self, account_id: str) -> CustomFields:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/video_fields/custom_fields",
            model=CustomFields,
        )

    async def create_custom_field(
        self, account_id: str, field_data: CustomField
    ) -> CustomField:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/video_fields/custom_fields",
            model=CustomField,
            method="POST",
            payload=field_data,
        )

    async def get_custom_field(
        self, account_id: str, custom_field_id: str
    ) -> CustomField:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/video_fields/custom_fields/{custom_field_id}",
            model=CustomField,
        )

    async def update_custom_field(
        self,
        account_id: str,
        custom_field_id: str,
        field_data: CustomFieldUpdate,
    ) -> CustomField:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/video_fields/custom_fields/{custom_field_id}",
            model=CustomField,
            method="PATCH",
            payload=field_data,
        )

    async def delete_custom_field(self, account_id: str, custom_field_id: str) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/video_fields/custom_fields/{custom_field_id}"
        )

    # ── Folders ────────────────────────────────────────────────────────────────

    async def get_folders(self, account_id: str) -> FolderList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/folders",
            model=FolderList,
        )

    async def create_folder(
        self, account_id: str, folder_data: FolderCreateFields
    ) -> Folder:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/folders",
            model=Folder,
            method="POST",
            payload=folder_data,
        )

    async def get_folder(self, account_id: str, folder_id: str) -> Folder:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/folders/{folder_id}",
            model=Folder,
        )

    async def update_folder(
        self, account_id: str, folder_id: str, folder_data: FolderUpdateFields
    ) -> Folder:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/folders/{folder_id}",
            model=Folder,
            method="PATCH",
            payload=folder_data,
        )

    async def delete_folder(self, account_id: str, folder_id: str) -> None:
        await self._delete(f"{self.base_url}{account_id}/folders/{folder_id}")

    async def get_videos_in_folder(self, account_id: str, folder_id: str) -> VideoArray:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/folders/{folder_id}/videos",
            model=VideoArray,
        )

    async def add_video_to_folder(
        self, account_id: str, folder_id: str, video_id: str
    ) -> None:
        await self._put_empty(
            f"{self.base_url}{account_id}/folders/{folder_id}/videos/{video_id}"
        )

    async def remove_video_from_folder(
        self, account_id: str, folder_id: str, video_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/folders/{folder_id}/videos/{video_id}"
        )

    # ── Labels ─────────────────────────────────────────────────────────────────

    async def get_labels(self, account_id: str) -> LabelsList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/labels",
            model=LabelsList,
        )

    async def create_label(self, account_id: str, label_data: LabelPath) -> LabelsList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/labels",
            model=LabelsList,
            method="POST",
            payload=label_data,
        )

    async def update_label(
        self, account_id: str, label_path: str, label_data: LabelUpdate
    ) -> LabelsList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/labels/by_path/{label_path}",
            model=LabelsList,
            method="PATCH",
            payload=label_data,
        )

    async def delete_label(self, account_id: str, label_path: str) -> None:
        await self._delete(f"{self.base_url}{account_id}/labels/by_path/{label_path}")

    # ── Channels ───────────────────────────────────────────────────────────────

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

    async def update_channel(
        self,
        account_id: str,
        channel_name: str,
        channel_data: UpdateChannelFields,
    ) -> Channel:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/channels/{channel_name}",
            model=Channel,
            method="PATCH",
            payload=channel_data,
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

    async def add_affiliate(
        self, account_id: str, channel_name: str, affiliate_account_id: str
    ) -> None:
        await self._put_empty(
            f"{self.base_url}{account_id}/channels/{channel_name}/members/{affiliate_account_id}"
        )

    async def remove_affiliate(
        self, account_id: str, channel_name: str, affiliate_account_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/channels/{channel_name}/members/{affiliate_account_id}"
        )

    # ── Contracts ──────────────────────────────────────────────────────────────

    async def list_contracts(self, account_id: str) -> ContractList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/contracts",
            model=ContractList,
        )

    async def get_contract(self, account_id: str, master_account_id: str) -> Contract:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/contracts/{master_account_id}",
            model=Contract,
        )

    async def approve_contract(
        self,
        account_id: str,
        master_account_id: str,
        contract_data: ApproveContractFields,
    ) -> Contract:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/contracts/{master_account_id}",
            model=Contract,
            method="PATCH",
            payload=contract_data,
        )

    # ── Video Shares ───────────────────────────────────────────────────────────

    async def list_shares(
        self,
        account_id: str,
        video_id: str,
    ) -> VideoShareList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/shares",
            model=VideoShareList,
        )

    async def share_video(
        self,
        account_id: str,
        video_id: str,
        share_data: ShareVideoRequest,
    ) -> VideoShareList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/shares",
            model=VideoShareList,
            method="POST",
            payload=share_data,
        )

    async def get_share(
        self, account_id: str, video_id: str, affiliate_account_id: str
    ) -> VideoShare:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/shares/{affiliate_account_id}",
            model=VideoShare,
        )

    async def unshare_video(
        self, account_id: str, video_id: str, affiliate_account_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/shares/{affiliate_account_id}"
        )

    # ── Subscriptions ──────────────────────────────────────────────────────────

    async def get_subscriptions(self, account_id: str) -> SubscriptionList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/subscriptions",
            model=SubscriptionList,
        )

    async def create_subscription(
        self, account_id: str, subscription_data: SubscriptionCreateFields
    ) -> Subscription:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/subscriptions",
            model=Subscription,
            method="POST",
            payload=subscription_data,
        )

    async def get_subscription(
        self, account_id: str, subscription_id: str
    ) -> Subscription:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/subscriptions/{subscription_id}",
            model=Subscription,
        )

    async def delete_subscription(self, account_id: str, subscription_id: str) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/subscriptions/{subscription_id}"
        )

    # ── Assets ─────────────────────────────────────────────────────────────────

    async def get_assets(self, account_id: str, video_id: str) -> VideoAssetList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets",
            model=VideoAssetList,
        )

    async def get_dynamic_renditions(
        self, account_id: str, video_id: str
    ) -> DynamicRenditionList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/dynamic_renditions",
            model=DynamicRenditionList,
        )

    # ── HLS Manifests ──────────────────────────────────────────────────────────

    async def get_hls_manifests(self, account_id: str, video_id: str) -> ManifestList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/hls_manifest",
            model=ManifestList,
        )

    async def add_hls_manifest(
        self, account_id: str, video_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/hls_manifest",
            model=Manifest,
            method="POST",
            payload=body,
        )

    async def get_hls_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/hls_manifest/{asset_id}",
            model=Manifest,
        )

    async def update_hls_manifest(
        self, account_id: str, video_id: str, asset_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/hls_manifest/{asset_id}",
            model=Manifest,
            method="PATCH",
            payload=body,
        )

    async def delete_hls_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/assets/hls_manifest/{asset_id}"
        )

    # ── DASH Manifests ─────────────────────────────────────────────────────────

    async def get_dash_manifests(self, account_id: str, video_id: str) -> ManifestList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/dash_manifests",
            model=ManifestList,
        )

    async def add_dash_manifest(
        self, account_id: str, video_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/dash_manifests",
            model=Manifest,
            method="POST",
            payload=body,
        )

    async def get_dash_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/dash_manifests/{asset_id}",
            model=Manifest,
        )

    async def update_dash_manifest(
        self, account_id: str, video_id: str, asset_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/dash_manifests/{asset_id}",
            model=Manifest,
            method="PATCH",
            payload=body,
        )

    async def delete_dash_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/assets/dash_manifests/{asset_id}"
        )

    # ── HDS Manifests ──────────────────────────────────────────────────────────

    async def get_hds_manifests(self, account_id: str, video_id: str) -> ManifestList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/hds_manifest",
            model=ManifestList,
        )

    async def add_hds_manifest(
        self, account_id: str, video_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/hds_manifest",
            model=Manifest,
            method="POST",
            payload=body,
        )

    async def get_hds_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/hds_manifest/{asset_id}",
            model=Manifest,
        )

    async def update_hds_manifest(
        self, account_id: str, video_id: str, asset_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/hds_manifest/{asset_id}",
            model=Manifest,
            method="PATCH",
            payload=body,
        )

    async def delete_hds_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/assets/hds_manifest/{asset_id}"
        )

    # ── ISM Manifests ──────────────────────────────────────────────────────────

    async def get_ism_manifests(self, account_id: str, video_id: str) -> ManifestList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/ism_manifest",
            model=ManifestList,
        )

    async def add_ism_manifest(
        self, account_id: str, video_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/ism_manifest",
            model=Manifest,
            method="POST",
            payload=body,
        )

    async def get_ism_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/ism_manifest/{asset_id}",
            model=Manifest,
        )

    async def update_ism_manifest(
        self, account_id: str, video_id: str, asset_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/ism_manifest/{asset_id}",
            model=Manifest,
            method="PATCH",
            payload=body,
        )

    async def delete_ism_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/assets/ism_manifest/{asset_id}"
        )

    # ── ISMC Manifests ─────────────────────────────────────────────────────────

    async def get_ismc_manifests(self, account_id: str, video_id: str) -> ManifestList:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/ismc_manifest",
            model=ManifestList,
        )

    async def add_ismc_manifest(
        self, account_id: str, video_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/ismc_manifest",
            model=Manifest,
            method="POST",
            payload=body,
        )

    async def get_ismc_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/ismc_manifest/{asset_id}",
            model=Manifest,
        )

    async def update_ismc_manifest(
        self, account_id: str, video_id: str, asset_id: str, body: RemoteAssetBody
    ) -> Manifest:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/ismc_manifest/{asset_id}",
            model=Manifest,
            method="PATCH",
            payload=body,
        )

    async def delete_ismc_manifest(
        self, account_id: str, video_id: str, asset_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/assets/ismc_manifest/{asset_id}"
        )

    # ── Renditions ─────────────────────────────────────────────────────────────

    async def add_rendition(
        self, account_id: str, video_id: str, body: RemoteAssetBody
    ) -> VideoAsset:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/renditions",
            model=VideoAsset,
            method="POST",
            payload=body,
        )

    async def get_rendition(
        self, account_id: str, video_id: str, asset_id: str
    ) -> VideoAsset:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/renditions/{asset_id}",
            model=VideoAsset,
        )

    async def update_rendition(
        self, account_id: str, video_id: str, asset_id: str, body: RemoteAssetBody
    ) -> VideoAsset:
        return await self.fetch_data(
            endpoint=f"{self.base_url}{account_id}/videos/{video_id}/assets/renditions/{asset_id}",
            model=VideoAsset,
            method="PATCH",
            payload=body,
        )

    async def delete_rendition(
        self, account_id: str, video_id: str, asset_id: str
    ) -> None:
        await self._delete(
            f"{self.base_url}{account_id}/videos/{video_id}/assets/renditions/{asset_id}"
        )
