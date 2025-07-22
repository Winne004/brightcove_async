from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, RootModel

from brightcove_async.schemas.dynamic_ingest_model.IngestMediaAssetbody import (
    audioTracks,
)


class Variant(Enum):
    main = "main"
    alternate = "alternate"
    commentary = "commentary"
    dub = "dub"
    descriptive = "descriptive"


class AudioTrack(BaseModel):
    language: str | None = Field(
        None,
        description="Language code for the muxed in audio from the subtags in (https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry) (default can be set for the account by contacting Brightcove Support) **Dynamic Delivery only**",
    )
    variant: Variant | None = Field(
        None,
        description="the type of audio track for the muxed in audio - generally `main` **Dynamic Delivery only**",
    )


class Master(BaseModel):
    url: str | None = Field(
        None,
        description="URL for the video source; required except for re-transcoding where a digital master has been archived, or you are adding images or text tracks to an existing video",
        examples=[
            "https://support.brightcove.com/test-assets/audio/celtic_lullaby.m4a",
        ],
    )
    use_archived_master: bool | None = Field(
        False,
        description="For retranscode requests, will use the archived master if set to true; if set to false, you must also include the url for the source video",
    )
    late_binding_type: str | None = Field(
        None,
        description="The process of associating progressive MP4 renditions with a video after it has been ingested, Late binding allows you to add or modify MP4 renditions to a video without having to entirely retranscode the video (https://apis.support.brightcove.com/dynamic-ingest/ingest-guides/requesting-late-binding.html#use_cases)",
    )
    audio_tracks: list[AudioTrack] | None = Field(
        None,
        description="Language code for the **muxed in** audio from the subtags in (https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry) (default can be set for the account by contacting Brightcove Support) **Dynamic Delivery only**",
        examples=[[{"language": "en", "variant": "main"}]],
    )


class Kind(Enum):
    captions = "captions"
    subtitles = "subtitles"
    chapters = "chapters"
    metadata = "metadata"
    transcripts = "transcripts"


class Status(Enum):
    published = "published"
    draft = "draft"


class TextTracks(BaseModel):
    url: str = Field(..., description="URL for a WebVTT file")
    srclang: str = Field(
        ...,
        description="BCP 47 language code for the text tracks. Both two letter language codes like `es` (Spanish) and language+region codes like `es-MX` (Mexican Spanish) are valid",
    )
    kind: Kind | None = Field(
        Kind.captions,
        description="how the vtt file is meant to be used",
    )
    label: str | None = Field(None, description="user-readable title")
    default: bool | None = Field(
        False,
        description="sets the default language for captions/subtitles",
    )
    status: Status | None = Field(
        None,
        description="The status of the text tracks - `published` or `draft` (use `draft` if you want the text tracks added but not yet available to users - `status` can be updated using the CMS API if you need to)",
    )
    embed_closed_caption: bool | None = Field(
        False,
        description="whether to embed the text tracks in MP4 renditions as 608 embedded captions",
    )


class Language(Enum):
    af_ZA = "af-ZA"
    ar_AE = "ar-AE"
    ar_SA = "ar-SA"
    cy_GB = "cy-GB"
    da_DK = "da-DK"
    de_CH = "de-CH"
    de_DE = "de-DE"
    en_AB = "en-AB"
    en_AU = "en-AU"
    en_GB = "en-GB"
    en_IE = "en-IE"
    en_IN = "en-IN"
    en_NZ = "en-NZ"
    en_US = "en-US"
    en_WL = "en-WL"
    en_ZA = "en-ZA"
    es_ES = "es-ES"
    es_US = "es-US"
    fa_IR = "fa-IR"
    fr_CA = "fr-CA"
    fr_FR = "fr-FR"
    ga_IE = "ga-IE"
    gd_GB = "gd-GB"
    he_IL = "he-IL"
    hi_IN = "hi-IN"
    id_ID = "id-ID"
    it_IT = "it-IT"
    ja_JP = "ja-JP"
    ko_KR = "ko-KR"
    ms_MY = "ms-MY"
    nl_NL = "nl-NL"
    pt_BR = "pt-BR"
    pt_PT = "pt-PT"
    ru_RU = "ru-RU"
    ta_IN = "ta-IN"
    te_IN = "te-IN"
    th_TH = "th-TH"
    tr_TR = "tr-TR"
    zh_CN = "zh-CN"
    zh_TW = "zh-TW"


class VariantModel(Enum):
    main = "main"
    alternate = "alternate"
    dub = "dub"
    commentary = "commentary"
    descriptive = "descriptive"


class InputAudioTrack(BaseModel):
    language: Language | None = Field(
        None,
        description="BCP-47 style language code for the text tracks (en-US, fr-FR, es-ES, etc.)",
    )
    variant: VariantModel | None = Field(
        None,
        description="Specifies the variant to use.",
    )


class KindModel(Enum):
    captions = "captions"
    transcripts = "transcripts"


class Srclang(Enum):
    af_ZA = "af-ZA"
    ar_AE = "ar-AE"
    ar_SA = "ar-SA"
    cy_GB = "cy-GB"
    da_DK = "da-DK"
    de_CH = "de-CH"
    de_DE = "de-DE"
    en_AB = "en-AB"
    en_AU = "en-AU"
    en_GB = "en-GB"
    en_IE = "en-IE"
    en_IN = "en-IN"
    en_US = "en-US"
    en_WL = "en-WL"
    es_ES = "es-ES"
    es_US = "es-US"
    fa_IR = "fa-IR"
    fr_CA = "fr-CA"
    fr_FR = "fr-FR"
    ga_IE = "ga-IE"
    gd_GB = "gd-GB"
    he_IL = "he-IL"
    hi_IN = "hi-IN"
    id_ID = "id-ID"
    it_IT = "it-IT"
    ja_JP = "ja-JP"
    ko_KR = "ko-KR"
    ms_MY = "ms-MY"
    nl_NL = "nl-NL"
    pt_BR = "pt-BR"
    pt_PT = "pt-PT"
    ru_RU = "ru-RU"
    ta_IN = "ta-IN"
    te_IN = "te-IN"
    tr_TR = "tr-TR"
    zh_CN = "zh-CN"


class Transcript(BaseModel):
    autodetect: bool | None = Field(
        None,
        description="`true` to auto-detect language from audio source.\n`false`  to use srclang specifying the audio language.\n\n**Note:**\n  - If `autodetect` is set to `true`, `srclang` must **not** be present\n  - If `autodetect` is set to `false`, and `srclang` is not present, the request will fail",
    )
    default: bool | None = Field(
        False,
        description="If true, srclang should be ignored and we will get captions for main audio, and the language will be determined from audio.",
    )
    input_audio_track: InputAudioTrack | None = Field(
        None,
        description="Defines the audio to extract the captions. Composed by language and variant (both required).",
    )
    kind: KindModel | None = Field(
        KindModel.captions,
        description="The kind of output to generate - for auto captions requests, if `kind` is `transcripts`, both captions and a transcript will be generated. For ingestion requests (including a `url`) the transcript will be ingested.",
    )
    label: str | None = Field(
        None,
        description="user-readable title - defaults to the BCP-47 style language code",
    )
    srclang: Srclang | None = Field(
        None,
        description="BCP-47 style language code for the text tracks (en-US, fr-FR, es-ES, etc.)",
    )
    status: Status | None = Field(
        None,
        description="The status of the text tracks - `published` or `draft` (use `draft` if you want the text tracks added but not yet available to users - `status` can be updated using the CMS API if you need to)",
    )
    url: str | None = Field(
        None,
        description="The URL where a transcript file is located. Must be included in the `kind` is `transcripts`. Must <strong>not</strong> be included if the `kind` is `captions`.",
    )


class Transcripts(RootModel[list[Transcript]]):
    root: list[Transcript] = Field(
        ...,
        description="array of auto captions/transcripts to be generated - see [Requesting Auto Captions](/dynamic-ingest/ingest-guides/requesting-auto-captions.html), or an array of transcript files to be ingested - see [Ingesting Transcript Files](/dynamic-ingest/ingest-guides/ingesting-transcriptions.html)",
        examples=[
            [
                {
                    "srclang": "en-US",
                    "kind": "transcripts",
                    "label": "en-US",
                    "status": "published",
                    "default": True,
                },
            ],
        ],
        title="Ingest Media Asset Body.transcripts",
    )


class Poster(BaseModel):
    url: str = Field(..., description="URL for the video poster image")
    height: float | None = Field(None, description="pixel height of the image")
    width: float | None = Field(None, description="pixel width of the image")


class Thumbnail(BaseModel):
    url: str = Field(..., description="URL for the video thumbnail image")
    height: float | None = Field(None, description="pixel height of the image")
    width: float | None = Field(None, description="pixel width of the image")


class VariantModel1(Enum):
    poster = "poster"
    thumbnail = "thumbnail"
    portrait = "portrait"
    square = "square"
    wide = "wide"
    ultra_wide = "ultra-wide"


class Label(Enum):
    poster = "poster"
    thumbnail = "thumbnail"


class Image(BaseModel):
    url: str = Field(..., description="URL for the image")
    language: str | None = Field(
        None,
        description="Language code for the image from the subtags in https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry (default can be set for the account by contacting Brightcove Support)",
    )
    variant: VariantModel1 = Field(..., description="the type of image")
    label: Label | None = None
    height: float | None = Field(None, description="pixel height of the image")
    width: float | None = Field(None, description="pixel width of the image")


class AudioTracks(BaseModel):
    merge_with_existing: bool | None = Field(
        True,
        description="whether to replace existing audio tracks or add the new ones",
    )
    masters: list[audioTracks.Masters] | None = Field(
        None,
        description="array of audio track objects **Dynamic Delivery only**",
    )
