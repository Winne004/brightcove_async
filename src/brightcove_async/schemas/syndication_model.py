from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, RootModel


class Type(Enum):
    advanced = "advanced"
    google = "google"
    iphone = "iphone"
    ipad = "ipad"
    mp4 = "mp4"
    itunes = "itunes"
    roku = "roku"
    source = "source"
    universal = "universal"


class Explicit(Enum):
    yes = "yes"
    no = "no"


class Syndication(BaseModel):
    id: str | None = Field(default=None, description="Id of this syndication")
    name: str = Field(..., description="Name of this syndication")
    type: Type = Field(
        ...,
        description="The syndication type.  Valid values are [advanced, google, iphone, "
        "ipad, mp4, itunes, roku, source, universal].  Cannot be changed after "
        "syndication creation time.",
    )
    include_all_content: bool | None = Field(
        default=None,
        description="If true, all content is included in this syndication.  If false, "
        "a valid include_filter property must be specified for the syndication.",
    )
    include_filter: str | None = Field(
        default=None,
        description="A CMS video search filter string used to select the subset of "
        "content included in this syndication.  The include_all_content field must be "
        "set to false if a value is specified for this property.",
    )
    sort: str | None = Field(
        default=None,
        description="A CMS video sorting specifier indicating the desired feed results "
        'return order.  CMS-supported values like "name", "reference_id", "created_at", '
        '"published_at", "updated_at", "schedule.starts_at", "schedule.ends_at", "state", '
        '"plays_total", and "plays_trailing_week" can be specified.  To sort in descending '
        'order, preface the value with a minus (-) sign, i.e. "-created_at".  '
        "If no value is specified, the feed will be sorted by "
        "most recent updated_at date by default.",
    )
    title: str | None = Field(
        default=None,
        description="The title of this feed. Will be included inside of the "
        "<channel> tag for some syndication types.",
    )
    description: str | None = Field(
        default=None,
        description="The description of this feed. Will be included inside of the "
        "<channel> tag for some syndication types.",
    )
    syndication_url: str | None = Field(
        default=None,
        description="The URL of this syndication's feed.  Read-only.",
    )
    destination_url: str | None = Field(
        default=None,
        description="The URL to be included inside of the <channel> tag in the feed.",
    )
    keywords: str | None = Field(
        default=None,
        description="A comma-separated list of keywords for iTunes",
    )
    author: str | None = Field(default=None, description="iTunes author specification")
    category: str | None = Field(
        default=None, description="iTunes category specification"
    )
    album_art_url: str | None = Field(default=None, description="iTunes album art url.")
    explicit: Explicit | None = Field(
        default=None,
        description='iTunes explicit content indicator, accepts "yes" or "no" values.',
    )
    owner_name: str | None = Field(default=None, description="iTunes owner name.")
    owner_email: str | None = Field(default=None, description="iTunes owner email.")
    language: str | None = Field(
        default=None,
        description="iTunes or Roku feed language field.",
    )
    fetch_sources: bool | None = Field(
        default=None,
        description="For universal feeds, specifies whether the feed service should "
        "fetch video source metadata and make it available to the template.  "
        "The default value is true.  If source metadata is not needed by the template, "
        "setting this to false can improve feed generation performance.",
    )
    fetch_digital_master: bool | None = Field(
        default=None,
        description="For universal feeds, specifies whether the feed service should fetch"
        " digital master metadata and make it available to the template.  The default "
        "value is false.  If digital master metadata is not needed by the template, "
        "keeping this setting as false can improve feed generation performance.",
    )
    fetch_dynamic_renditions: bool | None = Field(
        default=None,
        description="For universal feeds, specifies whether the feed service should "
        "fetch dynamic rendition metadata and make it available to the template.  "
        "The default value is false.  If dynamic rendition metadata is not needed by "
        "the template, keeping this setting as false can improve feed "
        "generation performance.",
    )
    content_type_header: str | None = Field(
        default=None,
        description=(
            "If set, overrides the Content-Type header returned by the feed server "
            "for this syndication's feed. Otherwise, the feed defaults to a "
            "syndication type-specific header value."
        ),
        json_schema_extra={"example": "application/xml"},
    )


class SyndicationList(RootModel[list[Syndication]]):
    pass


class ResponseError(BaseModel):
    error_code: Optional[str] = Field(
        default=None, description="Application error code"
    )
    message: Optional[str] = Field(
        default=None, description="Application error message"
    )


class ResponseErrorList(RootModel[list[ResponseError]]):
    pass
