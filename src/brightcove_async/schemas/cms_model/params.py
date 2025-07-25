from typing import TypedDict


class GetVideosQueryParams(TypedDict, total=False):
    limit: int
    offset: int
    sort: str
    q: str
    query: str


class GetVideoCountParams(TypedDict, total=False):
    q: str
