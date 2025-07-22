from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Variant(Enum):
    main = "main"
    alternate = "alternate"
    commentary = "commentary"
    dub = "dub"
    descriptive = "descriptive"


class Masters(BaseModel):
    url: Optional[str] = Field(
        default=None, description="URL for the audio file **Dynamic Delivery only**"
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code for the audio track from the subtags in https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry (default can be set for the account by contacting Brightcove Support) **Dynamic Delivery only**",
    )
    variant: Optional[Variant] = Field(
        default=None,
        description="the type of audio track (default can be set for the account by contacting Brightcove Support) **Dynamic Delivery only**",
    )
