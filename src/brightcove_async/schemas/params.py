from pydantic import BaseModel, Field


class ParamsBase(BaseModel):
    def serialize_params(self) -> dict:
        return self.model_dump(exclude_none=True, by_alias=True)


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
