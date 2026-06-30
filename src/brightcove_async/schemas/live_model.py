"""Pydantic models for the Brightcove NextGen Live API (v2).

Generated from ``brightcove_open_api_specs/live.yaml``. The spec namespaces its
schemas with prefixes (``endpoint.``, ``external.``, ``ssai.``, ``workflows.``,
etc.); those prefixes are dropped here and colliding names are disambiguated
(e.g. ``workflows.ClipRequest`` becomes :class:`WorkflowClipRequest`).

Request bodies honour the spec's ``required`` markers so invalid payloads fail
fast at construction time. Response models keep fields optional to tolerate the
API omitting values.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, RootModel

# ── Enums ────────────────────────────────────────────────────────────────────


class JobType(str, Enum):
    channel = "channel"
    event = "event"


class InputProtocol(str, Enum):
    rtmp = "rtmp"
    rtp = "rtp"
    srt = "srt"
    srt_caller = "srt-caller"


class InputLossBehaviourFillType(str, Enum):
    black_screen = "black_screen"
    repeat_frame = "repeat_frame"


class AudioCodec(str, Enum):
    aac = "aac"


class VideoCodec(str, Enum):
    h264 = "h264"


class VideoCodecProfile(str, Enum):
    baseline = "baseline"
    high = "high"
    main = "main"


class VideoCodecLevel(str, Enum):
    level_3 = "3"
    level_4 = "4"
    level_4_2 = "4.2"
    level_5 = "5"
    level_5_1 = "5.1"
    level_5_2 = "5.2"
    level_6 = "6"
    level_6_1 = "6.1"
    level_6_2 = "6.2"
    auto = "auto"


class CaptionDestinationType(str, Enum):
    embedded_closed_caption = "embedded_closed_caption"


class SegmentContainerFormat(str, Enum):
    cmaf = "cmaf"
    ts = "ts"


class SubscriptionType(str, Enum):
    state_change = "state_change"
    error = "error"


class JobIngestState(str, Enum):
    connected = "connected"
    disconnected = "disconnected"
    waiting = "waiting"


class JobProcessingState(str, Enum):
    configuring = "configuring"
    error = "error"
    off = "off"
    starting = "starting"
    on = "on"
    stopping = "stopping"
    finishing = "finishing"
    finished = "finished"


class AdServerResponseType(str, Enum):
    dfp = "dfp"
    vast = "vast"
    vmap = "vmap"
    playlist = "playlist"


class ClipOutputType(str, Enum):
    brightcove = "brightcove"
    s3 = "s3"


class VideoDataState(str, Enum):
    active = "ACTIVE"
    inactive = "INACTIVE"


class ManifestFormat(str, Enum):
    hls = "hls"
    dash = "dash"


# ── Shared input / output building blocks (external.*) ─────────────────────────


class BitrateRange(BaseModel):
    max: int | None = None
    min: int | None = None


class HeightRange(BaseModel):
    max: int | None = None
    min: int | None = None


class InputAudioPID(BaseModel):
    name: str
    pid: int


class InputLossBehaviour(BaseModel):
    fill_type: InputLossBehaviourFillType | None = None


class InputIngestPoint(BaseModel):
    name: str | None = None
    source_listener: str | None = None
    url: str | None = None


class SourceListener(BaseModel):
    address: str | None = None
    port: int | None = None
    stream_id: str | None = None


class SRTOptions(BaseModel):
    ingest_port: int | None = None
    min_latency: int | None = None
    passphrase: list[str] | None = None
    source_listeners: list[SourceListener] | None = None


class Input(BaseModel):
    audio_pids: list[InputAudioPID] | None = None
    fixed_ingest_ip: bool | None = None
    input_loss_behaviour: InputLossBehaviour | None = None
    protocol: InputProtocol
    reconnect_time: int | None = None
    srt_options: SRTOptions | None = None
    whitelist_cidr_blocks: list[str] | None = None


class Encryption(BaseModel):
    aes_key: str | None = None
    check_playback_rights: bool | None = None
    modes: list[str]


class DASHManifestOptions(BaseModel):
    pass


class DVRManifestOptions(BaseModel):
    playlist_window_seconds: int | None = None


class HLSManifestOptions(BaseModel):
    playlist_type: str | None = None


class LowLatencyManifestOptions(BaseModel):
    pass


class PlaylistGroup(BaseModel):
    audio_bitrate: BitrateRange | None = None
    audio_codec: list[str] | None = None
    language_code: list[str] | None = None
    name: str
    video_bitrate: BitrateRange | None = None
    video_codec: list[str] | None = None
    video_height: HeightRange | None = None


class ManifestOptions(BaseModel):
    dash: DASHManifestOptions | None = None
    dvr: DVRManifestOptions | None = None
    hls: HLSManifestOptions | None = None
    include_iframe_only_stream: bool | None = None
    low_latency: LowLatencyManifestOptions | None = None
    name: str | None = None
    playlist_groups: list[PlaylistGroup] | None = None
    playlist_window_seconds: int | None = None
    segment_container_format: SegmentContainerFormat | None = None
    segment_duration_seconds: int | None = Field(default=None, ge=1, le=30)


class MaintenancePreferences(BaseModel):
    day: str | None = None
    start_time: str | None = None


class Notification(BaseModel):
    """Webhook subscription configured on a job (external.Notification)."""

    subscription_type: SubscriptionType
    url: str


class RedundancyOptions(BaseModel):
    num_inputs: int


class SSAI(BaseModel):
    enabled: bool | None = None
    provider: str | None = None
    slate_asset_id: str | None = None


class VariantAudioInfo(BaseModel):
    bitrate: int
    codec: AudioCodec
    group_id: str | None = None
    input_selector_name: str | None = None
    label: str
    language_code: str | None = None
    sample_rate: int


class VariantCaptionInfo(BaseModel):
    passthrough: bool | None = None
    type: CaptionDestinationType | None = None
    language_code: str | None = None


class VariantRTMPInfo(BaseModel):
    audio_label: str | None = None
    label: str
    url: str
    video_label: str


class VideoCodecOptions(BaseModel):
    level: VideoCodecLevel | None = None
    profile: VideoCodecProfile | None = None


class VariantVideoInfo(BaseModel):
    bitrate: int
    codec: VideoCodec
    codec_options: VideoCodecOptions | None = None
    decoder_buffer_size: int | None = None
    embed_timecode: bool | None = None
    framerate: str
    height: int
    keyframe_rate: float | None = None
    keyframe_rate_units: str | None = None
    label: str
    max_bitrate: int | None = None
    num_b_frames: int | None = None
    num_reference_frames: int | None = None
    rate_control_mode: str | None = None
    sample_aspect_ratio: str | None = None
    width: int


class OutputVariants(BaseModel):
    audio: list[VariantAudioInfo] | None = None
    caption: list[VariantCaptionInfo] | None = Field(default=None, max_length=4)
    rtmp: list[VariantRTMPInfo] | None = None
    video: list[VariantVideoInfo] | None = None


class JobState(BaseModel):
    ingest_state: JobIngestState | None = None
    ingest_states: dict[str, JobIngestState] | None = None
    processing_state: JobProcessingState | None = None


class Job(BaseModel):
    # Response-only model: every field is optional so a response that omits a
    # field (the API may do so for partially-configured or audio-only jobs)
    # parses instead of raising. Request bodies use the strict ConfigureJobRequest
    # / JobConfig models, which keep input/outputs/region/type required.
    account_id: str | None = None
    audio_only: bool | None = None
    created_at: str | None = None
    encryption: Encryption | None = None
    id: str | None = None
    ingest_endpoints: list[InputIngestPoint] | None = None
    input: Input | None = None
    last_started_at: str | None = None
    live_to_vod: bool | None = None
    maintenance_preferences: MaintenancePreferences | None = None
    manifest: ManifestOptions | None = None
    notifications: list[Notification] | None = None
    outputs: OutputVariants | None = None
    redundancy: RedundancyOptions | None = None
    region: str | None = None
    ssai: SSAI | None = None
    state: JobState | None = None
    type: JobType | None = None


class JobConfig(BaseModel):
    audio_only: bool | None = None
    encryption: Encryption | None = None
    input: Input
    live_to_vod: bool | None = None
    maintenance_preferences: MaintenancePreferences | None = None
    manifest: ManifestOptions | None = None
    notifications: list[Notification] | None = None
    outputs: OutputVariants
    redundancy: RedundancyOptions | None = None
    region: str
    ssai: SSAI | None = None
    type: JobType


class Session(BaseModel):
    account_id: str | None = None
    end_time: int | None = None
    id: str | None = None
    resource_id: str | None = None
    start_time: int | None = None


class SessionEvent(BaseModel):
    event_type: str | None = None
    id: str | None = None
    session_id: str | None = None
    timestamp: int | None = None


class Error(BaseModel):
    error_code: str | None = None
    message: str | None = None
    status: int | None = None
    sub_code: str | None = None


# ── SSAI ad configuration (ssai.*) ─────────────────────────────────────────────


class AdServer(BaseModel):
    headers: dict[str, str] | None = None
    response_type: AdServerResponseType
    url: str


class CustomBeacon(BaseModel):
    event: str | None = None
    url: str | None = None


class AdConfiguration(BaseModel):
    account_id: str | None = None
    ad_server: AdServer
    custom_beacons: list[CustomBeacon] | None = None
    description: str
    id: str | None = None


# ── Scheduler workflow models (workflows.*) ────────────────────────────────────


class AutoStopTaskInfo(BaseModel):
    state: str | None = None
    time_utc: int | None = None


class JobStartStopTaskInfo(BaseModel):
    notification: int | None = None
    state: str | None = None
    time_utc: int | None = None


class WorkflowClipOutput(BaseModel):
    type: str | None = None
    url: str | None = None


class WorkflowClipVideoData(BaseModel):
    state: str | None = None


class WorkflowClipRequest(BaseModel):
    custom_fields: dict[str, str] | None = None
    description: str | None = None
    end: str | None = None
    ingest_profile: str | None = None
    name: str | None = None
    output: WorkflowClipOutput | None = None
    override_reference_id: bool | None = None
    reference_id: str | None = None
    remove_ads: bool | None = None
    start: str | None = None
    tags: list[str] | None = None
    video_data: WorkflowClipVideoData | None = None


class ClipTaskInfo(BaseModel):
    clip_request: WorkflowClipRequest | None = None
    notification: int | None = None
    state: str | None = None
    time_utc: int | None = None


class Clip(BaseModel):
    account_id: str | None = None
    clip: ClipTaskInfo | None = None
    description: str | None = None
    job_id: str | None = None
    metadata_passthrough: dict[str, Any] | None = None
    notification_url: str | None = None
    type: str | None = None
    workflow_id: str | None = None
    workflow_start_time_utc: int | None = None


# ── Misc supporting models ─────────────────────────────────────────────────────


class CDNTokenRecord(BaseModel):
    account_id: str | None = None
    expires_at: str | None = None
    hostname: str | None = None
    id: str | None = None
    issued_at: str | None = None
    ttl: int | None = None


class MetricDimension(BaseModel):
    inputSource: str | None = None


class MetricOutput(BaseModel):
    category: str | None = None
    label: str | None = None
    name: str | None = None
    statistic: str | None = None
    unit: str | None = None


class MetricResultValue(BaseModel):
    dimension: MetricDimension | None = None
    metric: MetricOutput | None = None
    values: list[list[Any]] | None = None


class MetricDataValue(BaseModel):
    result: list[MetricResultValue] | None = None


class HealthCheck(BaseModel):
    build_version: str | None = None
    git_sha: str | None = None


class NotificationMessage(BaseModel):
    """A delivered notification record (notifications-agent model)."""

    code: str | None = None
    message: str | None = None
    resource_id: str | None = None
    resource_type: str | None = None
    timestamp: int | None = None
    type: str | None = None


# ── Request bodies (endpoint.*) ────────────────────────────────────────────────


class ConfigureJobRequest(BaseModel):
    audio_only: bool | None = None
    custom_fields: dict[str, str] | None = None
    description: str | None = None
    encryption: Encryption | None = None
    input: Input
    live_to_vod: bool | None = None
    long_description: str | None = None
    maintenance_preferences: MaintenancePreferences | None = None
    manifest: ManifestOptions | None = None
    name: str | None = None
    notifications: list[Notification] | None = None
    outputs: OutputVariants
    playback_rights_id: str | None = None
    redundancy: RedundancyOptions | None = None
    reference_id: str | None = None
    region: str
    ssai: SSAI | None = None
    tags: list[str] | None = None
    type: JobType


class ClipOutput(BaseModel):
    type: ClipOutputType
    url: str | None = None


class VideoData(BaseModel):
    state: VideoDataState | None = None


class ClipRequest(BaseModel):
    custom_fields: dict[str, str] | None = None
    description: str | None = None
    end: str | None = None
    name: str | None = None
    output: ClipOutput | None = None
    override_reference_id: bool | None = None
    reference_id: str | None = None
    remove_ads: bool | None = None
    start: str
    ingest_profile: str | None = None
    video_data: VideoData | None = None
    tags: list[str] | None = None


class InsertCuePointRequest(BaseModel):
    account_id: str | None = None
    ad_server_data: list[int] | None = None
    ad_server_data_format: str | None = None
    duration_in_seconds: int | None = None
    job_id: str | None = None


class CreateTokenRequest(BaseModel):
    ad_config_id: str | None = None
    byocdn_id: str | None = None
    cenc: bool | None = None
    dvr: bool | None = None
    start_time: str | None = None
    end_time: str | None = None
    low_latency: bool | None = None
    manifest_format: ManifestFormat | None = None
    playlist_name: str | None = None
    ssai: bool | None = None


class BatchPlaybackRequest(BaseModel):
    playback: CreateTokenRequest | None = None


class BatchPlaybackRequestMap(RootModel[dict[str, BatchPlaybackRequest]]):
    """Map of arbitrary label -> playback config for batch source generation."""


class ForceFailoverRequest(BaseModel):
    pipeline_name: str


class JobStartStopCreateRequest(BaseModel):
    account_id: str | None = None
    description: str | None = None
    job_id: str | None = None
    metadata_passthrough: dict[str, Any] | None = None
    notification_url: str | None = None
    start_action: JobStartStopTaskInfo
    stop_action: JobStartStopTaskInfo
    type: str | None = None
    workflow_id: str | None = None
    workflow_start_time_utc: int | None = None


class JobStartStopUpdateRequest(BaseModel):
    account_id: str | None = None
    description: str | None = None
    job_id: str | None = None
    metadata_passthrough: dict[str, Any] | None = None
    notification_url: str | None = None
    start_action: JobStartStopTaskInfo | None = None
    stop_action: JobStartStopTaskInfo | None = None
    type: str | None = None
    workflow_id: str | None = None
    workflow_start_time_utc: int | None = None


class ClipScheduleRequest(BaseModel):
    """Request body for scheduling/updating a clip (endpoint.Clip*Request)."""

    account_id: str | None = None
    clip: ClipTaskInfo | None = None
    description: str | None = None
    job_id: str | None = None
    metadata_passthrough: dict[str, Any] | None = None
    notification_url: str | None = None
    type: str | None = None
    workflow_id: str | None = None
    workflow_start_time_utc: int | None = None


# ── Response bodies (endpoint.*) ───────────────────────────────────────────────


class ListJobsDetails(BaseModel):
    audio_only: bool | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    ingest_points: list[InputIngestPoint] | None = None
    labels: list[str] | None = None
    last_updated: str | None = None
    name: str | None = None
    protocol: str | None = None
    region: str | None = None
    state: JobState | None = None
    type: str | None = None


class ListJobsResponse(BaseModel):
    jobs: list[ListJobsDetails] | None = None


class JobResponse(BaseModel):
    account_id: str | None = None
    audio_only: bool | None = None
    created_at: str | None = None
    custom_fields: dict[str, str] | None = None
    description: str | None = None
    encryption: Encryption | None = None
    id: str | None = None
    ingest_endpoints: list[InputIngestPoint] | None = None
    input: Input | None = None
    labels: list[str] | None = None
    last_started_at: str | None = None
    live_to_vod: bool | None = None
    long_description: str | None = None
    maintenance_preferences: MaintenancePreferences | None = None
    manifest: ManifestOptions | None = None
    name: str | None = None
    notifications: list[Notification] | None = None
    outputs: OutputVariants | None = None
    playback_rights_id: str | None = None
    redundancy: RedundancyOptions | None = None
    reference_id: str | None = None
    region: str | None = None
    ssai: SSAI | None = None
    state: JobState | None = None
    tags: list[str] | None = None
    type: JobType | None = None


class UpdateJobResponse(BaseModel):
    old_config: JobConfig | None = None
    updated_job: JobResponse | None = None


class FinishJobResponse(BaseModel):
    id: str | None = None


class StartJobResponse(BaseModel):
    id: str | None = None


class StopJobResponse(BaseModel):
    id: str | None = None


class ClipResponse(BaseModel):
    id: str | None = None


class ForceFailoverResponse(BaseModel):
    pass


class ResetOriginResponse(BaseModel):
    status: str | None = None


class GeneratePlaybackURLResponse(BaseModel):
    url: str | None = None


class CreateTokenResponse(BaseModel):
    token: str | None = None


class AutoStopGetResponse(BaseModel):
    account_id: str | None = None
    action: AutoStopTaskInfo | None = None
    description: str | None = None
    job_id: str | None = None
    metadata_passthrough: dict[str, Any] | None = None
    notification_url: str | None = None
    type: str | None = None
    workflow_id: str | None = None
    workflow_start_time_utc: int | None = None


class JobStartStopResponse(BaseModel):
    """Shared shape for create/get/update/delete/list jobstartstop schedules."""

    account_id: str | None = None
    description: str | None = None
    job_id: str | None = None
    metadata_passthrough: dict[str, Any] | None = None
    notification_url: str | None = None
    start_action: JobStartStopTaskInfo | None = None
    stop_action: JobStartStopTaskInfo | None = None
    type: str | None = None
    workflow_id: str | None = None
    workflow_start_time_utc: int | None = None


class ClipWorkflowResponse(BaseModel):
    """Shared shape for create/get/update/delete scheduled-clip responses."""

    account_id: str | None = None
    clip: ClipTaskInfo | None = None
    description: str | None = None
    job_id: str | None = None
    metadata_passthrough: dict[str, Any] | None = None
    notification_url: str | None = None
    type: str | None = None
    workflow_id: str | None = None
    workflow_start_time_utc: int | None = None


class ClipListAccountResponse(BaseModel):
    next_token: str | None = None
    workflows: list[Clip] | None = None


class Thumbnail(BaseModel):
    body: str | None = None
    content_type: str | None = None
    thumbnail_type: str | None = None
    timestamp: str | None = None


class ThumbnailDetail(BaseModel):
    pipeline_id: str | None = None
    thumbnails: list[Thumbnail] | None = None


class GetThumbnailResponse(BaseModel):
    thumbnail_detail: ThumbnailDetail | None = None


class SupportedMetrics(BaseModel):
    category: str | None = None
    label: str | None = None
    name: str | None = None
    statistics: list[str] | None = None
    unit: str | None = None


class GetAllSupportedMetricsResponse(BaseModel):
    metrics: list[SupportedMetrics] | None = None


class GetJobMetricsResponse(BaseModel):
    data: MetricDataValue | None = None
    endTime: int | None = None
    isPartial: bool | None = None
    period: str | None = None
    startTime: int | None = None
    status: str | None = None


class NotificationsResponse(BaseModel):
    last_key: str | None = None
    notifications: list[NotificationMessage] | None = None


class GetSessionResponse(BaseModel):
    account_id: str | None = None
    end_time: int | None = None
    id: str | None = None
    resource_id: str | None = None
    start_time: int | None = None


class SessionEventList(RootModel[list[SessionEvent]]):
    pass


class GetResourceSessionsResponse(BaseModel):
    sessions: list[Session] | None = None


class GetBYOCDNTokensResponse(BaseModel):
    tokens: list[CDNTokenRecord] | None = None


class AdConfigResponse(BaseModel):
    """Shared shape for get/update ad-config responses."""

    account_id: str | None = None
    ad_server: AdServer | None = None
    custom_beacons: list[CustomBeacon] | None = None
    description: str | None = None
    id: str | None = None


class DeleteAdConfigResponse(BaseModel):
    ad_config_id: str | None = None


class ListAdConfigsResponse(BaseModel):
    ad_configs: list[AdConfiguration] | None = None


class BatchSource(BaseModel):
    codecs: str | None = None
    ext_x_version: str | None = None
    key_systems: dict[str, Any] | None = None
    src: str | None = None
    type: str | None = None
    uploaded_at: str | None = None


class BatchGenerateSourcesResponse(RootModel[dict[str, list[BatchSource]]]):
    """Map of the labels supplied in the request to their generated sources."""
