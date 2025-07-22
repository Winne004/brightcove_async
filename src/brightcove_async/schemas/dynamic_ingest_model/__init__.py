from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from . import IngestMediaAssetbody as IngestMediaAssetbody_1


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
    master: Optional[IngestMediaAssetbody_1.Master] = None
    forensic_watermarking: Optional[bool] = Field(
        False,
        description="Whether forensic watermarks should be added to video renditions - if you set it to `true` the account must be enabled for forensic watermarking, or the field will be ignored - see **[Overview: Forensic Watermarking](/general/overview-forensic-watermarking.html) for more details**",
        examples=[True],
    )
    forensic_watermarking_stub_mode: Optional[bool] = Field(
        False,
        description="Whether **visible** forensic watermarks should be added to video renditions - if you set it to `true` the account must be enabled for forensic watermarking, and the `forensic_watermarking` field must also be set to `true` - see **[Overview: Forensic Watermarking](/general/overview-forensic-watermarking.html) for more details**\n\nVisible watermarks should be used only for testing integrations, to ensure that forensic watermarks have been successfully added to the video (use a video at least 10 minutes long). Once verification is complete, they must be removed by submitting a new ingest request to retranscode the video - `forensic_watermarking_stub_mode` must be set to `false` on the retranscode request.",
        examples=[True],
    )
    profile: Optional[str] = Field(
        None,
        description="ingest profile to use for transcoding; if absent, account default profile will be used",
        examples=["multi-platform-standard-static"],
    )
    priority: Optional[Priority] = Field(
        None,
        description="Priority queueing allows the user to add a `priority` flag to an ingest request. The allowable values for `priority` are `low` and `normal` . Any other value will cause the request to be rejected with a 422 error code. When the user doesn't specify any priority, the default value of `normal` is used. Priority queuing is available for Dynamic Delivery ingest only. Here is a brief description of how Priority Queueing changes how jobs are processed from the queue:\n\n1. If there are no queued jobs and there is capacity to run a job, then the job is run immediately. This applies to both low and normal priority jobs.\n2. If there is is no capacity for another job to run, the job is queued.\n3. If there are jobs in the queue, then any new jobs are also queued. This means that a new job can't start before queued jobs.\n4. When there is capacity to run another job and there are queued jobs, a job is taken from the queue:\n  - If there are ANY normal priority jobs in the queue, the oldest normal priority job will be picked.\n  - If there are NO normal priority jobs in the queue, then the oldest low priority job will be picked.\n5. Normal and Low priority jobs are treated the same for how many running jobs there can be. The total number of jobs processing, whatever their priority, is limited to 100 per account.\n6. There are separate quotas for how many normal and low priority jobs can be queued.",
    )
    text_tracks: Optional[List[IngestMediaAssetbody_1.TextTracks]] = Field(
        None, description="array of text_track maps"
    )
    transcriptions: Optional[List[IngestMediaAssetbody_1.Transcripts]] = Field(
        None, description="array of auto captions to be generated"
    )
    audio_tracks: Optional[IngestMediaAssetbody_1.AudioTracks] = None
    images: Optional[List[IngestMediaAssetbody_1.Image]] = Field(
        None, description="array of images (Dynamic Delivery Only)"
    )
    poster: Optional[IngestMediaAssetbody_1.Poster] = None
    thumbnail: Optional[IngestMediaAssetbody_1.Thumbnail] = None
    capture_images: Optional[bool] = Field(
        None,
        alias="capture-images",
        description="whether poster and thumbnail should be captured during transcoding; defaults to `true` if the the profile has image renditions, `false` if it does not",
    )
    callbacks: Optional[List[str]] = Field(
        None,
        description="array of URLs that notifications should be sent to",
        examples=[["https://solutions.brightcove.com/bcls/di-api/di-callbacks.php"]],
    )
