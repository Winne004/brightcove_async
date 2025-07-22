from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel

from brightcove_async.schemas.dynamic_ingest_model.IngestMediaAssetbody import (
    audioTracks,
)


class GetS3UrlsResponse(BaseModel):
    bucket: str = Field(..., description="the S3 bucket name")
    object_key: str = Field(
        ...,
        description="the access key used for authenticating the upload request (used for multipart uploads)",
    )
    access_key_id: str = Field(
        ...,
        description="the access key used for authenticating the upload request (used for multipart uploads)",
    )
    secret_access_key: str = Field(
        ...,
        description="the secret access key used for authenticating the upload request (used for multipart uploads)",
    )
    session_token: str = Field(
        ...,
        description="the secret access key used for authenticating the upload request (used for multipart uploads)",
    )
    SignedUrl: str = Field(
        ...,
        description="this is a shorthand S3 url that you can PUT your source file(s) to if you have relatively small videos and are not implementing multipart upload",
    )
    ApiRequestUrl: str = Field(
        ...,
        description="this is the URL you will include in your Dynamic Ingest POST request for the Master url or url for the image/text_tracks assets",
    )


class Priority(Enum):
    low = "low"
    normal = "normal"


class IngestMediaAssetResponse(BaseModel):
    id: str = Field(..., description="job id for the request")


class IngestMediaAssetbody(BaseModel):
    master: Optional[Master] = None
    forensic_watermarking: Optional[bool] = Field(
        default=False,
        description="Whether forensic watermarks should be added to video renditions - if you set it to `true` the account must be enabled for forensic watermarking, or the field will be ignored - see **[Overview: Forensic Watermarking](/general/overview-forensic-watermarking.html) for more details**",
        examples=[True],
    )
    forensic_watermarking_stub_mode: Optional[bool] = Field(
        default=False,
        description="Whether **visible** forensic watermarks should be added to video renditions - if you set it to `true` the account must be enabled for forensic watermarking, and the `forensic_watermarking` field must also be set to `true` - see **[Overview: Forensic Watermarking](/general/overview-forensic-watermarking.html) for more details**\n\nVisible watermarks should be used only for testing integrations, to ensure that forensic watermarks have been successfully added to the video (use a video at least 10 minutes long). Once verification is complete, they must be removed by submitting a new ingest request to retranscode the video - `forensic_watermarking_stub_mode` must be set to `false` on the retranscode request.",
        examples=[True],
    )
    profile: Optional[str] = Field(
        default=None,
        description="ingest profile to use for transcoding; if absent, account default profile will be used",
        examples=["multi-platform-standard-static"],
    )
    priority: Optional[Priority] = Field(
        default=None,
        description="Priority queueing allows the user to add a `priority` flag to an ingest request. The allowable values for `priority` are `low` and `normal` . Any other value will cause the request to be rejected with a 422 error code. When the user doesn't specify any priority, the default value of `normal` is used. Priority queuing is available for Dynamic Delivery ingest only. Here is a brief description of how Priority Queueing changes how jobs are processed from the queue:\n\n1. If there are no queued jobs and there is capacity to run a job, then the job is run immediately. This applies to both low and normal priority jobs.\n2. If there is is no capacity for another job to run, the job is queued.\n3. If there are jobs in the queue, then any new jobs are also queued. This means that a new job can't start before queued jobs.\n4. When there is capacity to run another job and there are queued jobs, a job is taken from the queue:\n  - If there are ANY normal priority jobs in the queue, the oldest normal priority job will be picked.\n  - If there are NO normal priority jobs in the queue, then the oldest low priority job will be picked.\n5. Normal and Low priority jobs are treated the same for how many running jobs there can be. The total number of jobs processing, whatever their priority, is limited to 100 per account.\n6. There are separate quotas for how many normal and low priority jobs can be queued.",
    )
    text_tracks: Optional[List[TextTracks]] = Field(
        default=None, description="array of text_track maps"
    )
    transcriptions: Optional[List[Transcripts]] = Field(
        default=None, description="array of auto captions to be generated"
    )
    audio_tracks: Optional[AudioTracks] = None
    images: Optional[List[Image]] = Field(
        default=None, description="array of images (Dynamic Delivery Only)"
    )
    poster: Optional[Poster] = None
    thumbnail: Optional[Thumbnail] = None
    capture_images: Optional[bool] = Field(
        default=None,
        alias="capture-images",
        description="whether poster and thumbnail should be captured during transcoding; defaults to `true` if the the profile has image renditions, `false` if it does not",
    )
    callbacks: Optional[List[str]] = Field(
        default=None,
        description="array of URLs that notifications should be sent to",
        examples=[["https://solutions.brightcove.com/bcls/di-api/di-callbacks.php"]],
    )


class Variant(Enum):
    main = "main"
    alternate = "alternate"
    commentary = "commentary"
    dub = "dub"
    descriptive = "descriptive"


class AudioTrack(BaseModel):
    language: str | None = Field(
        default=None,
        description="Language code for the muxed in audio from the subtags in (https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry) (default can be set for the account by contacting Brightcove Support) **Dynamic Delivery only**",
    )
    variant: Variant | None = Field(
        default=None,
        description="the type of audio track for the muxed in audio - generally `main` **Dynamic Delivery only**",
    )


class Master(BaseModel):
    url: str | None = Field(
        default=None,
        description="URL for the video source; required except for re-transcoding where a digital master has been archived, or you are adding images or text tracks to an existing video",
        examples=[
            "https://support.brightcove.com/test-assets/audio/celtic_lullaby.m4a",
        ],
    )
    use_archived_master: bool | None = Field(
        default=False,
        description="For retranscode requests, will use the archived master if set to true; if set to false, you must also include the url for the source video",
    )
    late_binding_type: str | None = Field(
        default=None,
        description="The process of associating progressive MP4 renditions with a video after it has been ingested, Late binding allows you to add or modify MP4 renditions to a video without having to entirely retranscode the video (https://apis.support.brightcove.com/dynamic-ingest/ingest-guides/requesting-late-binding.html#use_cases)",
    )
    audio_tracks: list[AudioTrack] | None = Field(
        default=None,
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
    label: str | None = Field(default=None, description="user-readable title")
    default: bool | None = Field(
        default=False,
        description="sets the default language for captions/subtitles",
    )
    status: Status | None = Field(
        default=None,
        description="The status of the text tracks - `published` or `draft` (use `draft` if you want the text tracks added but not yet available to users - `status` can be updated using the CMS API if you need to)",
    )
    embed_closed_caption: bool | None = Field(
        default=False,
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
        default=None,
        description="BCP-47 style language code for the text tracks (en-US, fr-FR, es-ES, etc.)",
    )
    variant: VariantModel | None = Field(
        default=None,
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
        default=None,
        description="`true` to auto-detect language from audio source.\n`false`  to use srclang specifying the audio language.\n\n**Note:**\n  - If `autodetect` is set to `true`, `srclang` must **not** be present\n  - If `autodetect` is set to `false`, and `srclang` is not present, the request will fail",
    )
    default: bool | None = Field(
        default=False,
        description="If true, srclang should be ignored and we will get captions for main audio, and the language will be determined from audio.",
    )
    input_audio_track: InputAudioTrack | None = Field(
        default=None,
        description="Defines the audio to extract the captions. Composed by language and variant (both required).",
    )
    kind: KindModel | None = Field(
        KindModel.captions,
        description="The kind of output to generate - for auto captions requests, if `kind` is `transcripts`, both captions and a transcript will be generated. For ingestion requests (including a `url`) the transcript will be ingested.",
    )
    label: str | None = Field(
        default=None,
        description="user-readable title - defaults to the BCP-47 style language code",
    )
    srclang: Srclang | None = Field(
        default=None,
        description="BCP-47 style language code for the text tracks (en-US, fr-FR, es-ES, etc.)",
    )
    status: Status | None = Field(
        default=None,
        description="The status of the text tracks - `published` or `draft` (use `draft` if you want the text tracks added but not yet available to users - `status` can be updated using the CMS API if you need to)",
    )
    url: str | None = Field(
        default=None,
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
    height: float | None = Field(default=None, description="pixel height of the image")
    width: float | None = Field(default=None, description="pixel width of the image")


class Thumbnail(BaseModel):
    url: str = Field(..., description="URL for the video thumbnail image")
    height: float | None = Field(default=None, description="pixel height of the image")
    width: float | None = Field(default=None, description="pixel width of the image")


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
        default=None,
        description="Language code for the image from the subtags in https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry (default can be set for the account by contacting Brightcove Support)",
    )
    variant: VariantModel1 = Field(..., description="the type of image")
    label: Label | None = None
    height: float | None = Field(default=None, description="pixel height of the image")
    width: float | None = Field(default=None, description="pixel width of the image")


class AudioTracks(BaseModel):
    merge_with_existing: bool | None = Field(
        True,
        description="whether to replace existing audio tracks or add the new ones",
    )
    masters: list[audioTracks.Masters] | None = Field(
        default=None,
        description="array of audio track objects **Dynamic Delivery only**",
    )
