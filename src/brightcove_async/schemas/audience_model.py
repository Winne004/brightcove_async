from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class SortLeads(StrEnum):
    video_id = "video_id"
    video_name = "video_name"
    player_id = "player_id"
    created_at = "created_at"


class Sort(StrEnum):
    video_id = "video_id"
    video_name = "video_name"
    tracking_id = "tracking_id"
    external_id = "external_id"
    player_id = "player_id"
    page_url = "page_url"
    watched = "watched"
    time_watched = "time_watched"
    created_at = "created_at"
    updated_at = "updated_at"
    is_synced = "is_synced"
    utm_source = "utm_source"
    utm_medium = "utm_medium"
    utm_campaign = "utm_campaign"
    utm_term = "utm_term"
    utm_content = "utm_content"


class FieldsLeads(StrEnum):
    video_id = "video_id"
    video_name = "video_name"
    external_id = "external_id"
    first_name = "first_name"
    last_name = "last_name"
    email_address = "email_address"
    business_phone = "business_phone"
    country = "country"
    company_name = "company_name"
    industry = "industry"
    player_id = "player_id"
    page_url = "page_url"
    created_at = "created_at"


class Fields(StrEnum):
    video_id = "video_id"
    video_name = "video_name"
    tracking_id = "tracking_id"
    external_id = "external_id"
    player_id = "player_id"
    page_url = "page_url"
    watched = "watched"
    time_watched = "time_watched"
    created_at = "created_at"
    updated_at = "updated_at"
    is_synced = "is_synced"
    utm_source = "utm_source"
    utm_medium = "utm_medium"
    utm_campaign = "utm_campaign"
    utm_term = "utm_term"
    utm_content = "utm_content"


class LeadsResult(BaseModel):
    created_at: str | None = None
    email_address: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    business_phone: str | None = None
    country: str | None = None
    company_name: str | None = None
    industry: str | None = None
    page_url: str | None = None
    player_id: str | None = None
    video_id: str | None = None
    video_name: str | None = None
    external_id: str | None = None


class GetLeadsResponse(BaseModel):
    count: float | None = Field(None, description="the total number of items")
    limit: float | None = Field(None, description="the limit for items in this request")
    offset: float | None = Field(
        None, description="the offset for items in this request"
    )
    result: list[LeadsResult] | None = Field(None, description="array of result items")


class EventResult(BaseModel):
    created_at: str | None = Field(None, description="Creation date")
    is_synched: bool | None = Field(
        None, description="Whether the view event has been synchronized"
    )
    page_url: str | None = Field(None, description="Page URL where the event occurred")
    player_id: str | None = Field(None, description="The Brightcove player ID")
    time_watched: int | None = Field(None, description="Seconds of the video watched")
    tracking_id: str | None = Field(None, description="A custom tracking id")
    external_id: str | None = Field(
        None, description="ID from the Marketing Automation Platform or a custom GUID"
    )
    updated_at: str | None = Field(None, description="Last updated date")
    video_id: str | None = Field(None, description="The Brightcove video ID")
    video_name: str | None = Field(None, description="The Brightcove video title")
    watched: int | None = Field(None, description="Percent of the video watched")


class GetViewEventsResponse(BaseModel):
    count: float | None = Field(None, description="the total number of items")
    limit: float | None = Field(None, description="the limit for items in this request")
    offset: float | None = Field(
        None, description="the offset for items in this request"
    )
    result: list[EventResult] | None = Field(None, description="array of result items")
