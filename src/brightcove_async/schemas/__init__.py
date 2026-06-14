"""
Public re-exports for brightcove_async schema models.

Import from the submodules directly for full IDE support, or use the
convenience imports here when you just need a handful of types:

    from brightcove_async.schemas import Video, CreateVideoRequestBodyFields
    from brightcove_async.schemas.cms_model import Playlist, PlaylistInputFields
    from brightcove_async.schemas.params import GetVideosQueryParams
"""

# ── CMS models ─────────────────────────────────────────────────────────────────
# ── Analytics models ───────────────────────────────────────────────────────────
from .analytics_model import (
    GetAlltimeVideoViewsResponse,
    GetAnalyticsReportResponse,
    GetAvailableDateRangeResponse,
    GetVideoEngagementResponse,
    Timeline,
    TimelineWithDuration,
)

# ── Audience models ────────────────────────────────────────────────────────────
from .audience_model import (
    GetLeadsResponse,
    GetViewEventsResponse,
)
from .cms_model import (
    AddAffiliate,
    ApproveContractFields,
    AudioTrack,
    AudioTracks,
    Channel,
    ChannelAffiliate,
    ChannelAffiliateList,
    ChannelList,
    Contract,
    ContractList,
    CreateVideoRequestBodyFields,
    CuePoint,
    CustomField,
    CustomFields,
    CustomFieldUpdate,
    DeliveryType,
    DigitalMaster,
    DynamicRendition,
    DynamicRenditionList,
    Economics,
    Event,
    Folder,
    FolderCreateFields,
    FolderList,
    FolderUpdateFields,
    ForensicWatermarking,
    Geo,
    Image,
    ImageAsset,
    ImageList,
    IngestJobs,
    IngestJobStatus,
    Kind,
    LabelPath,
    LabelsList,
    LabelUpdate,
    Link,
    Manifest,
    ManifestList,
    MediaType,
    Playlist,
    PlaylistArray,
    PlaylistCount,
    PlaylistInputFields,
    PlaylistReferences,
    PlaylistType,
    Projection,
    RemoteAssetBody,
    Schedule,
    SearchSyntax,
    ShareVideoRequest,
    Sharing,
    State,
    State1,
    State2,
    State3,
    Subscription,
    SubscriptionCreateFields,
    SubscriptionList,
    Tag,
    TextTrack,
    Transcript,
    Type,
    UpdateAudioTrackFields,
    UpdateChannelFields,
    UpdateVideoRequestBodyFields,
    User,
    UserType,
    Variant,
    Variant1,
    Video,
    VideoArray,
    VideoAsset,
    VideoAssetList,
    VideoAssets,
    VideoCount,
    VideoCountInPlaylist,
    VideoFields,
    VideoImages,
    VideoShare,
    VideoShareList,
    VideoSources,
    VideoSourcesList,
    VideoVariant,
    VideoVariants,
)

# ── Ingest Profiles models ─────────────────────────────────────────────────────
from .ingest_profiles_model import (
    IngestProfile,
    IngestProfileList,
)

# ── Params ─────────────────────────────────────────────────────────────────────
from .params import (
    GetAnalyticsReportParams,
    GetLeadsParams,
    GetLivestreamAnalyticsParams,
    GetVideoCountParams,
    GetVideosQueryParams,
    GetViewEventsParams,
)

# ── Syndication models ─────────────────────────────────────────────────────────
from .syndication_model import (
    Syndication,
    SyndicationList,
)

__all__ = [
    # Videos
    "Video",
    "VideoArray",
    "VideoCount",
    "VideoSourcesList",
    "VideoSources",
    "VideoImages",
    "ImageList",
    "Image",
    "ImageAsset",
    "CreateVideoRequestBodyFields",
    "UpdateVideoRequestBodyFields",
    # Video variants
    "VideoVariant",
    "VideoVariants",
    # Audio tracks
    "AudioTrack",
    "AudioTracks",
    "UpdateAudioTrackFields",
    # Digital master
    "DigitalMaster",
    # Ingest jobs
    "IngestJobStatus",
    "IngestJobs",
    # Playlists
    "Playlist",
    "PlaylistArray",
    "PlaylistCount",
    "PlaylistReferences",
    "PlaylistInputFields",
    "PlaylistType",
    "VideoCountInPlaylist",
    # Custom fields
    "VideoFields",
    "CustomField",
    "CustomFields",
    "CustomFieldUpdate",
    # Folders
    "Folder",
    "FolderList",
    "FolderCreateFields",
    "FolderUpdateFields",
    # Labels
    "LabelsList",
    "LabelPath",
    "LabelUpdate",
    # Channels
    "Channel",
    "ChannelList",
    "ChannelAffiliate",
    "ChannelAffiliateList",
    "UpdateChannelFields",
    "AddAffiliate",
    # Contracts
    "Contract",
    "ContractList",
    "ApproveContractFields",
    # Shares
    "VideoShare",
    "VideoShareList",
    "ShareVideoRequest",
    # Subscriptions
    "Subscription",
    "SubscriptionList",
    "SubscriptionCreateFields",
    "Event",
    # Assets
    "VideoAsset",
    "VideoAssetList",
    "VideoAssets",
    "DynamicRendition",
    "DynamicRenditionList",
    "Manifest",
    "ManifestList",
    "RemoteAssetBody",
    # Field-level / shared models
    "CuePoint",
    "TextTrack",
    "Transcript",
    "Geo",
    "Schedule",
    "Link",
    "Sharing",
    "Tag",
    "User",
    # Enums
    "Economics",
    "State",
    "State1",
    "State2",
    "State3",
    "DeliveryType",
    "ForensicWatermarking",
    "Projection",
    "Kind",
    "MediaType",
    "Type",
    "Variant",
    "Variant1",
    "SearchSyntax",
    "UserType",
    # Params
    "GetVideosQueryParams",
    "GetVideoCountParams",
    "GetAnalyticsReportParams",
    "GetLivestreamAnalyticsParams",
    "GetLeadsParams",
    "GetViewEventsParams",
    # Analytics
    "Timeline",
    "TimelineWithDuration",
    "GetVideoEngagementResponse",
    "GetAnalyticsReportResponse",
    "GetAvailableDateRangeResponse",
    "GetAlltimeVideoViewsResponse",
    # Audience
    "GetLeadsResponse",
    "GetViewEventsResponse",
    # Syndication
    "Syndication",
    "SyndicationList",
    # Ingest Profiles
    "IngestProfile",
    "IngestProfileList",
]
