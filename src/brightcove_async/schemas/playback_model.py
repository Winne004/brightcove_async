"""Pydantic models for the Brightcove Playback API.

Generated from ``brightcove_open_api_specs/playback.yaml``. The Playback API is
read-only and client-facing, so every field is optional: the API freely omits
values and the response shape evolves over time. Models use
``extra="allow"`` so newly added response fields are preserved rather than
dropped.

Note: the raw Playback API response is not directly consumable by the
Brightcove player. Use the player's ``catalog.transformVideoResponse()`` helper
client-side to adapt these objects for playback.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, RootModel


class _PlaybackModel(BaseModel):
    """Base config shared by all Playback response models."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class PosterSource(_PlaybackModel):
    src: str | None = Field(default=None, description="URL for a poster source image")


class ThumbnailSource(_PlaybackModel):
    src: str | None = Field(
        default=None, description="URL for a thumbnail source image"
    )


class CuePoint(_PlaybackModel):
    name: str | None = Field(default=None, description="cue point name")
    type: str | None = Field(default=None, description="cue point type")
    time: float | None = Field(
        default=None, description="time of the cue point in seconds"
    )
    metadata: str | None = Field(
        default=None, description="optional metadata string (max 128 single-byte chars)"
    )
    force_stop: bool | None = Field(
        default=None,
        alias="force-stop",
        description="whether the video is force-stopped at the cue point",
    )


class Link(_PlaybackModel):
    text: str | None = Field(default=None, description="text for the link")
    url: str | None = Field(default=None, description="URL for the link")


class Source(_PlaybackModel):
    """A video source / rendition (HLS, DASH or MP4)."""

    src: str | None = Field(default=None, description="URL for the rendition")
    type: str | None = Field(default=None, description="MIME type for HLS/DASH streams")
    codec: str | None = Field(default=None, description="the video codec")
    codecs: str | None = Field(default=None, description="codecs string for the source")
    container: str | None = Field(default=None, description="the video container")
    avg_bitrate: float | None = Field(default=None, description="average bitrate")
    width: float | None = Field(default=None, description="frame width in pixels")
    height: float | None = Field(default=None, description="frame height in pixels")
    size: float | None = Field(default=None, description="size in bytes")
    duration: float | None = Field(default=None, description="duration in milliseconds")
    asset_id: str | None = Field(
        default=None, description="the asset id for the source"
    )
    stream_name: str | None = Field(
        default=None, description="the stream name for the source"
    )
    app_name: str | None = Field(
        default=None, description="the address for rtmp streams"
    )
    ext_x_version: str | None = Field(default=None, description="HLS EXT-X-VERSION")
    profiles: str | None = Field(default=None, description="DASH profiles string")


class TextTrackSource(_PlaybackModel):
    src: str | None = Field(default=None, description="URL for the .vtt file")


class TextTrack(_PlaybackModel):
    id: str | None = None
    account_id: str | None = None
    src: str | None = Field(default=None, description="URL for the .vtt file")
    sources: list[TextTrackSource] | None = Field(
        default=None, description="array of sources for .vtt files"
    )
    kind: str | None = Field(default=None, description="kind of text track")
    srclang: str | None = Field(
        default=None, description='2-letter language code, e.g. "en"'
    )
    label: str | None = Field(default=None, description="label for the track")
    mime_type: str | None = Field(default=None, description="mime_type for the track")
    default: bool | None = Field(
        default=None, description="whether this is the default track"
    )
    in_band_metadata_track_dispatch_type: str | None = Field(
        default=None,
        description="present when references are available in the video's manifest",
    )


class Transcript(_PlaybackModel):
    id: str | None = Field(default=None, description="system id for the text track")
    account_id: str | None = None
    label: str | None = Field(default=None, description="label for the track")
    mime_type: str | None = Field(
        default=None, description="mime-type for the track, e.g. text/plain"
    )
    src: str | None = Field(default=None, description="URL for the transcription file")
    src_lang: str | None = Field(
        default=None, description='2-letter language code, e.g. "en"'
    )
    status: str | None = None
    default: bool | None = None
    sources: list[str] | None = None


class Variant(_PlaybackModel):
    """Language-specific metadata for a video."""

    language: str | None = Field(
        default=None, description="language-country code, e.g. en-US"
    )
    name: str | None = Field(default=None, description="the title in this language")
    description: str | None = Field(
        default=None, description="the short description in this language"
    )
    long_description: str | None = Field(
        default=None, description="the long description in this language"
    )
    custom_fields: dict | None = None
    poster_sources: list[PosterSource] | None = None
    poster: str | None = None
    thumbnail_sources: list[ThumbnailSource] | None = None
    thumbnail: str | None = None


class PlaybackVideo(_PlaybackModel):
    """A video object as returned by the Playback API."""

    id: str | None = Field(default=None, description="video id")
    name: str | None = Field(default=None, description="video title")
    reference_id: str | None = Field(default=None, description="video reference id")
    account_id: str | None = Field(default=None, description="Video Cloud account id")
    description: str | None = Field(default=None, description="video short description")
    long_description: str | None = Field(
        default=None, description="video long description"
    )
    created_at: str | None = Field(
        default=None, description="when the video was created"
    )
    updated_at: str | None = Field(
        default=None, description="when the video was last modified"
    )
    published_at: str | None = Field(
        default=None, description="when the video was published"
    )
    duration: float | None = Field(
        default=None, description="video duration in milliseconds"
    )
    economics: str | None = Field(
        default=None, description="whether the video is AD_SUPPORTED or FREE"
    )
    labels: list[str] | None = Field(default=None, description="array of labels")
    tags: list[str] | None = Field(default=None, description="array of tags")
    custom_fields: dict | None = Field(
        default=None, description="map of fieldname-value pairs"
    )
    cue_points: list[CuePoint] | None = Field(
        default=None, description="array of cue points"
    )
    poster: str | None = Field(
        default=None, description="URL for the default poster source image"
    )
    poster_sources: list[PosterSource] | None = None
    thumbnail: str | None = Field(
        default=None, description="URL for the default thumbnail source image"
    )
    thumbnail_sources: list[ThumbnailSource] | None = None
    sources: list[Source] | None = Field(
        default=None, description="array of video sources (renditions)"
    )
    text_tracks: list[TextTrack] | None = None
    transcripts: list[Transcript] | None = None
    variants: list[Variant] | None = None
    link: Link | None = Field(default=None, description="map of scheduling properties")
    offline_enabled: bool | None = Field(
        default=None, description="whether the video is enabled for offline viewing"
    )
    projection: str | None = Field(
        default=None,
        description='mapping projection for 360 videos, e.g. "equirectangular"',
    )
    playback_rights_id: str | None = Field(
        default=None, description="associated EPA playback rights id"
    )
    ad_keys: dict | None = Field(
        default=None, description="map of key/value pairs for ad requests"
    )


class GetVideosResponse(RootModel[list[PlaybackVideo]]):
    """The Get Videos / Get Related Videos endpoints return a bare JSON array.

    The list of videos is available on the ``root`` attribute and the model is
    directly iterable / indexable for convenience.
    """

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, index):
        return self.root[index]

    def __len__(self) -> int:
        return len(self.root)


class PlaylistResponse(_PlaybackModel):
    """A playlist object as returned by the Playback API."""

    id: str | None = Field(default=None, description="the playlist id")
    account_id: str | None = Field(default=None, description="Video Cloud account id")
    name: str | None = Field(default=None, description="the playlist name")
    description: str | None = Field(default=None, description="playlist description")
    reference_id: str | None = Field(
        default=None, description="the playlist reference id"
    )
    type: str | None = Field(
        default=None, description="EXPLICIT or smart playlist type"
    )
    created_at: str | None = Field(default=None, description="date/time created")
    updated_at: str | None = Field(default=None, description="date/time last modified")
    video_ids: list[str] | None = Field(
        default=None, description="array of video ids (EXPLICIT playlists only)"
    )
    search: str | None = Field(
        default=None, description="search string (smart playlists only)"
    )
    videos: list[PlaybackVideo] | None = Field(
        default=None, description="array of video objects"
    )
