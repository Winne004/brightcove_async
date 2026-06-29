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
