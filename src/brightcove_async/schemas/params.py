from dataclasses import dataclass


@dataclass
class GetVideosQueryParams:
    limit: int | None = None
    offset: int | None = None
    sort: str | None = None
    q: str | None = None
    query: str | None = None


@dataclass
class GetVideoCountParams:
    q: str | None = None


@dataclass
class GetAnalyticsReportParams:
    accounts: str
    dimensions: str
    where: str | None = None
    limit: int | None = None
    sort: str | None = None
    offset: int | None = None
    fields: str | None = None
    from_: str | int | None = None
    to: str | int | None = None
    format_: str | None = None
    reconciled: bool | None = None


@dataclass
class GetLivestreamAnalyticsParams:
    dimensions: str
    metrics: str
    where: str
    bucket_limit: int | None = None
    bucket_duration: str | None = None
    from_: str | int | None = None
    to: str | int | None = None
