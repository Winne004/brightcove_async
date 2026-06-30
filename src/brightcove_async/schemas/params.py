from pydantic import BaseModel, Field


class ParamsBase(BaseModel):
    def serialize_params(self) -> dict:
        raw = self.model_dump(exclude_none=True, by_alias=True)
        # aiohttp/yarl reject bool query values; serialize them to the
        # lowercase string form the Brightcove APIs expect.
        return {
            key: ("true" if value else "false") if isinstance(value, bool) else value
            for key, value in raw.items()
        }


class GetVideosQueryParams(ParamsBase):
    limit: int | None = None
    offset: int | None = None
    sort: str | None = None
    q: str | None = None
    query: str | None = None


class GetVideoCountParams(ParamsBase):
    q: str | None = None


class GetAnalyticsReportParams(ParamsBase):
    accounts: str
    dimensions: str
    where: str | None = None
    limit: int | None = None
    sort: str | None = None
    offset: int | None = None
    fields: str | None = None
    from_: str | int | None = Field(default=None, serialization_alias="from")
    to: str | int | None = None
    format_: str | None = Field(default=None, serialization_alias="format")
    reconciled: bool | None = None


class GetLivestreamAnalyticsParams(ParamsBase):
    dimensions: str
    metrics: str
    where: str
    bucket_limit: int | None = None
    bucket_duration: str | None = None
    from_: str | int | None = Field(default=None, serialization_alias="from")
    to: str | int | None = None


class GetLiveEventsParams(ParamsBase):
    dimensions: str
    metrics: str
    where: str


class GetLeadsParams(ParamsBase):
    limit: int | None = None
    offset: int | None = None
    sort: str | None = None
    fields: str | None = None
    where: str | None = None
    from_: str | int | None = Field(default=None, serialization_alias="from")
    to: str | int | None = None


class GetViewEventsParams(GetLeadsParams):
    pass


class ListLiveJobsParams(ParamsBase):
    """Query parameters for listing Live jobs.

    ``regions`` accepts a comma-separated string of region names. The timestamp
    filters (``modified_at``/``created_at``) use the API's ``<op>:<unixmillis>``
    format, and ``processing_state`` uses ``<op>:<state>`` (e.g. ``eq:on``).
    """

    regions: str | None = None
    modified_at: str | None = None
    created_at: str | None = None
    processing_state: str | None = None
    ingest_state: str | None = None
    type: str | None = None


class LiveSchedulerListParams(ParamsBase):
    """Query parameters for listing job schedules or scheduled clips."""

    page_size: int | None = None
    start_token: str | None = None
    state: str | None = None
    start: int | None = None
    end: int | None = None


class GetLiveJobMetricsParams(ParamsBase):
    """Query parameters for the Live job metrics endpoint.

    ``name`` is a comma-separated list of metric names (required). ``period``
    and ``range`` use the API's unit suffixes (e.g. ``30s``, ``1h``).
    """

    name: str
    period: str | None = None
    range_: str | None = Field(default=None, serialization_alias="range")
    start: str | None = None
    end: str | None = None


class LiveResourceSessionsParams(ParamsBase):
    """Query parameters for listing sessions for a resource (job)."""

    start: float | None = None
    end: float | None = None


class GeneratePlaybackURLParams(ParamsBase):
    """Query parameters for generating a playback URL from a token."""

    account_id: str
    pt: str


class PlaybackVideosParams(ParamsBase):
    """Query parameters for the Playback API Get Videos endpoint.

    ``q`` triggers a search and requires a search-enabled policy key.
    """

    q: str | None = None
    limit: int | None = None
    offset: int | None = None
    sort: str | None = None
    ad_config_id: str | None = None
    config_id: str | None = None


class PlaybackListParams(ParamsBase):
    """Query parameters shared by Related Videos and Playlist endpoints."""

    limit: int | None = None
    offset: int | None = None
    ad_config_id: str | None = None
    config_id: str | None = None


class PlaybackVideoParams(ParamsBase):
    """Query parameters for the Playback API single-video endpoint."""

    ad_config_id: str | None = None
    config_id: str | None = None


class PlaybackManifestParams(ParamsBase):
    """Query parameters for the Playback API static-URL (manifest) endpoints.

    ``bcov_auth`` is a JWT used for static URL delivery (see Brightcove's
    Static URL Delivery guide). ``config_id`` applies delivery rules.
    """

    bcov_auth: str | None = None
    config_id: str | None = None


class ImageTransformParams(ParamsBase):
    """Query parameters for the Image API transformation endpoint.

    Any combination of parameters may be used together. Booleans are
    serialized to their lowercase string form (``true``/``false``) by
    :meth:`ParamsBase.serialize_params`, as expected by the Image API.
    """

    resize: str | None = None
    crop: str | None = None
    rotate: str | None = None
    fallback: bool | None = None
    fill_area: bool | None = Field(default=None, serialization_alias="fillArea")
    watermark: bool | None = None
    nocache: bool | None = None

    def serialize_params(self) -> dict:
        params = super().serialize_params()
        # The Image API requires `nocache` to follow another parameter, so it
        # must never be the only param and must always be emitted last.
        if "nocache" in params:
            nocache = params.pop("nocache")
            if not params:
                raise ValueError(
                    "`nocache` must be combined with at least one other image "
                    "transformation parameter.",
                )
            params["nocache"] = nocache
        return params
