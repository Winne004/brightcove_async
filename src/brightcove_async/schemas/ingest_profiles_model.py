"""Pydantic models for Brightcove Ingest Profiles API."""

from pydantic import BaseModel, Field
class DigitalMaster(BaseModel):
    """Digital master configuration for an ingest profile."""

    rendition: str
    distribute: bool


class DynamicOriginImage(BaseModel):
    """Image configuration for dynamic origin."""

    label: str
    height: int
    width: int


class DynamicOrigin(BaseModel):
    """Dynamic origin configuration for an ingest profile."""

    renditions: list[str]
    images: list[DynamicOriginImage]


class IngestProfile(BaseModel):
    """Brightcove Ingest Profile model."""

    version: int
    name: str
    display_name: str
    description: str
    account_id: int
    brightcove_standard: bool
    date_created: int
    date_last_modified: int
    digital_master: DigitalMaster
    renditions: list[dict] = Field(default_factory=list)
    packages: list[dict] = Field(default_factory=list)
    dynamic_origin: DynamicOrigin | None = None
    id: str
