from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.live_model import (
    AdConfiguration,
    AdServer,
    AdServerResponseType,
    AudioCodec,
    BatchGenerateSourcesResponse,
    BatchPlaybackRequest,
    BatchPlaybackRequestMap,
    ClipRequest,
    ClipScheduleRequest,
    ConfigureJobRequest,
    CreateTokenRequest,
    FinishJobResponse,
    ForceFailoverRequest,
    Input,
    InputProtocol,
    InsertCuePointRequest,
    Job,
    JobConfig,
    JobStartStopCreateRequest,
    JobStartStopTaskInfo,
    JobType,
    ListJobsResponse,
    ManifestFormat,
    OutputVariants,
    VariantAudioInfo,
    VariantVideoInfo,
    VideoCodec,
)
from brightcove_async.schemas.params import (
    GeneratePlaybackURLParams,
    GetLiveJobMetricsParams,
    ListLiveJobsParams,
    LiveResourceSessionsParams,
    LiveSchedulerListParams,
)
from brightcove_async.services.live import Live

BASE_URL = "https://api.live.brightcove.com"


class DummyOAuth:
    async def get_access_token(self):
        return "test_token"

    @property
    async def headers(self):
        return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_session():
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture
def dummy_oauth():
    return DummyOAuth()


@pytest.fixture
def live_service(mock_session, dummy_oauth):
    return Live(
        session=mock_session,
        oauth=dummy_oauth,
        base_url=BASE_URL,
        limit=10,
    )


def _sample_job_request() -> ConfigureJobRequest:
    return ConfigureJobRequest(
        type=JobType.channel,
        region="us-east-1",
        input=Input(protocol=InputProtocol.rtmp),
        outputs=OutputVariants(
            video=[
                VariantVideoInfo(
                    label="1080p",
                    height=1080,
                    width=1920,
                    bitrate=6000000,
                    codec=VideoCodec.h264,
                    framerate="30/1",
                ),
            ],
            audio=[
                VariantAudioInfo(
                    label="english",
                    codec=AudioCodec.aac,
                    bitrate=128000,
                    sample_rate=48000,
                ),
            ],
        ),
    )


def test_live_initialization(live_service):
    assert live_service._limit == 10
    assert live_service.base_url == BASE_URL


@pytest.mark.asyncio
async def test_list_jobs(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=ListJobsResponse)

        params = ListLiveJobsParams(processing_state="eq:on", type="channel")
        await live_service.list_jobs("acc1", params)

        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/jobs"
        assert call.kwargs["model"] == ListJobsResponse
        assert call.kwargs["params"] == {
            "processing_state": "eq:on",
            "type": "channel",
        }


@pytest.mark.asyncio
async def test_create_job(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=Job)

        job = _sample_job_request()
        await live_service.create_job("acc1", job)

        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/jobs"
        assert call.kwargs["model"] == Job
        assert call.kwargs["method"] == "POST"
        assert call.kwargs["payload"] is job


@pytest.mark.asyncio
async def test_get_job(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=Job)

        await live_service.get_job("acc1", "job1")

        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/jobs/job1"
        assert call.kwargs["model"] == Job


@pytest.mark.asyncio
async def test_update_job(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        config = JobConfig(
            type=JobType.channel,
            region="us-east-1",
            input=Input(protocol=InputProtocol.rtmp),
            outputs=OutputVariants(),
        )
        await live_service.update_job("acc1", "job1", config)

        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/jobs/job1"
        assert call.kwargs["method"] == "PUT"
        assert call.kwargs["payload"] is config


@pytest.mark.asyncio
async def test_finish_job_uses_delete(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=FinishJobResponse)

        await live_service.finish_job("acc1", "job1")

        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/jobs/job1"
        assert call.kwargs["model"] == FinishJobResponse
        assert call.kwargs["method"] == "DELETE"


@pytest.mark.asyncio
async def test_clip_job(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        clip = ClipRequest(start="1710504000", end="1710511200", name="highlight")
        await live_service.clip_job("acc1", "job1", clip)

        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/jobs/job1/clip"
        assert call.kwargs["method"] == "POST"
        assert call.kwargs["payload"] is clip


@pytest.mark.asyncio
async def test_force_failover(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        request = ForceFailoverRequest(pipeline_name="primary")
        await live_service.force_failover("acc1", "job1", request)

        call = mock_fetch.call_args
        assert (
            call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/jobs/job1/failover"
        )
        assert call.kwargs["method"] == "PUT"
        assert call.kwargs["payload"] is request


@pytest.mark.asyncio
async def test_start_and_stop_job(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.start_job("acc1", "job1")
        start_call = mock_fetch.call_args
        assert (
            start_call.kwargs["endpoint"]
            == f"{BASE_URL}/v2/accounts/acc1/jobs/job1/start"
        )
        assert start_call.kwargs["method"] == "PUT"

        await live_service.stop_job("acc1", "job1")
        stop_call = mock_fetch.call_args
        assert (
            stop_call.kwargs["endpoint"]
            == f"{BASE_URL}/v2/accounts/acc1/jobs/job1/stop"
        )
        assert stop_call.kwargs["method"] == "PUT"


@pytest.mark.asyncio
async def test_reset_origin(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.reset_origin("acc1", "job1")
        call = mock_fetch.call_args
        assert (
            call.kwargs["endpoint"]
            == f"{BASE_URL}/v2/accounts/acc1/jobs/job1/reset_origin"
        )
        assert call.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_thumbnail_with_pipeline(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.get_thumbnail("acc1", "job1", pipeline_id="p1")
        call = mock_fetch.call_args
        assert (
            call.kwargs["endpoint"]
            == f"{BASE_URL}/v2/accounts/acc1/jobs/job1/thumbnail"
        )
        assert call.kwargs["params"] == {"pipeline_id": "p1"}


@pytest.mark.asyncio
async def test_get_thumbnail_without_pipeline(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.get_thumbnail("acc1", "job1")
        assert mock_fetch.call_args.kwargs["params"] is None


@pytest.mark.asyncio
async def test_insert_cuepoint(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=Job)
        request = InsertCuePointRequest(duration_in_seconds=30)
        await live_service.insert_cuepoint("acc1", "job1", request)

        call = mock_fetch.call_args
        assert (
            call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/jobs/job1/cuepoint"
        )
        assert call.kwargs["model"] == Job
        assert call.kwargs["method"] == "POST"


@pytest.mark.asyncio
async def test_get_job_metrics(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        params = GetLiveJobMetricsParams(
            name="input_bitrate,output_bitrate",
            period="30s",
            range_="1h",
        )
        await live_service.get_job_metrics("acc1", "job1", params)

        call = mock_fetch.call_args
        assert (
            call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/jobs/job1/metrics"
        )
        serialized = call.kwargs["params"]
        assert serialized["name"] == "input_bitrate,output_bitrate"
        assert serialized["period"] == "30s"
        assert serialized["range"] == "1h"
        assert "range_" not in serialized


@pytest.mark.asyncio
async def test_get_account_notifications(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.get_account_notifications("acc1", last_key="abc")
        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == f"{BASE_URL}/v2/accounts/acc1/notifications"
        assert call.kwargs["params"] == {"last_key": "abc"}


@pytest.mark.asyncio
async def test_scheduler_list_and_create(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        params = LiveSchedulerListParams(page_size=10, state="scheduled")
        await live_service.list_schedules("acc1", "job1", params)
        call = mock_fetch.call_args
        assert (
            call.kwargs["endpoint"]
            == f"{BASE_URL}/v2/accounts/acc1/jobs/job1/scheduler"
        )
        assert call.kwargs["params"] == {"page_size": 10, "state": "scheduled"}

        request = JobStartStopCreateRequest(
            start_action=JobStartStopTaskInfo(time_utc=1710504000),
            stop_action=JobStartStopTaskInfo(time_utc=1710511200),
        )
        await live_service.create_jobstartstop_schedule("acc1", "job1", request)
        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/jobs/job1/scheduler/jobstartstop"
        )
        assert call.kwargs["method"] == "POST"
        assert call.kwargs["payload"] is request


@pytest.mark.asyncio
async def test_jobstartstop_workflow_endpoints(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.get_jobstartstop_schedule("acc1", "job1", "wf1")
        expected = f"{BASE_URL}/v2/accounts/acc1/jobs/job1/scheduler/jobstartstop/wf1"
        assert mock_fetch.call_args.kwargs["endpoint"] == expected

        await live_service.delete_jobstartstop_schedule("acc1", "job1", "wf1")
        assert mock_fetch.call_args.kwargs["endpoint"] == expected
        assert mock_fetch.call_args.kwargs["method"] == "DELETE"


@pytest.mark.asyncio
async def test_scheduled_clip_patch(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        request = ClipScheduleRequest(description="update")
        await live_service.update_scheduled_clip("acc1", "job1", "wf1", request)
        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/jobs/job1/scheduler/clips/wf1"
        )
        assert call.kwargs["method"] == "PATCH"
        assert call.kwargs["payload"] is request


@pytest.mark.asyncio
async def test_create_playback_token(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        request = CreateTokenRequest(dvr=True, manifest_format=ManifestFormat.hls)
        await live_service.create_playback_token("acc1", "job1", request)
        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/playback/job1/token"
        )
        assert call.kwargs["method"] == "POST"
        assert call.kwargs["payload"] is request


@pytest.mark.asyncio
async def test_generate_batch_sources(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = MagicMock(spec=BatchGenerateSourcesResponse)
        sources = BatchPlaybackRequestMap(
            {
                "dvr": BatchPlaybackRequest(
                    playback=CreateTokenRequest(
                        dvr=True, manifest_format=ManifestFormat.hls
                    )
                ),
                "non-dvr": BatchPlaybackRequest(
                    playback=CreateTokenRequest(manifest_format=ManifestFormat.hls)
                ),
            }
        )
        await live_service.generate_batch_sources("acc1", "job1", sources)
        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/playback/job1/sources/batch"
        )
        assert call.kwargs["method"] == "POST"
        assert call.kwargs["payload"] is sources


@pytest.mark.asyncio
async def test_generate_playback_url_is_unauthenticated(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        params = GeneratePlaybackURLParams(account_id="acc1", pt="tok")
        await live_service.generate_playback_url("job1", params)
        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == f"{BASE_URL}/v2/playback/job1"
        assert call.kwargs["params"] == {"account_id": "acc1", "pt": "tok"}
        # No-auth endpoint: empty headers prevent an OAuth token fetch.
        assert call.kwargs["headers"] == {}


@pytest.mark.asyncio
async def test_session_endpoints(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.get_session("acc1", "sess1")
        assert mock_fetch.call_args.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/sessions/sess1"
        )

        await live_service.get_session_events("acc1", "sess1")
        assert mock_fetch.call_args.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/sessions/sess1/events"
        )

        params = LiveResourceSessionsParams(start=1.0, end=2.0)
        await live_service.get_resource_sessions("acc1", "job1", params)
        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/sessions/resource/job1"
        )
        assert call.kwargs["params"] == {"start": 1.0, "end": 2.0}


@pytest.mark.asyncio
async def test_list_cdn_tokens(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.list_cdn_tokens("acc1")
        assert mock_fetch.call_args.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/settings/cdns/tokens"
        )


@pytest.mark.asyncio
async def test_ad_config_crud(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.list_ad_configs("acc1")
        assert mock_fetch.call_args.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/ssai/ad-configs"
        )

        config = AdConfiguration(
            description="my ads",
            ad_server=AdServer(
                url="https://ads.example.com/vast",
                response_type=AdServerResponseType.vast,
            ),
        )
        await live_service.create_ad_config("acc1", config)
        call = mock_fetch.call_args
        assert call.kwargs["model"] == AdConfiguration
        assert call.kwargs["method"] == "POST"
        assert call.kwargs["payload"] is config

        await live_service.delete_ad_config("acc1", "ad1")
        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == (
            f"{BASE_URL}/v2/accounts/acc1/ssai/ad-configs/ad1"
        )
        assert call.kwargs["method"] == "DELETE"


@pytest.mark.asyncio
async def test_healthcheck_is_unauthenticated(live_service):
    with patch.object(live_service, "fetch_data", new_callable=AsyncMock) as mock_fetch:
        await live_service.healthcheck()
        call = mock_fetch.call_args
        assert call.kwargs["endpoint"] == f"{BASE_URL}/v2/healthcheck"
        assert call.kwargs["headers"] == {}


# ── Model / serialization behaviour ────────────────────────────────────────────


def test_configure_job_request_serializes_enums_to_values():
    job = _sample_job_request()
    dumped = job.model_dump(mode="json", exclude_none=True)
    assert dumped["type"] == "channel"
    assert dumped["input"]["protocol"] == "rtmp"
    assert dumped["outputs"]["video"][0]["codec"] == "h264"
    assert dumped["outputs"]["audio"][0]["codec"] == "aac"


def test_clip_request_requires_start():
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        ClipRequest.model_validate({"name": "missing start"})


def test_batch_request_map_round_trips():
    sources = BatchPlaybackRequestMap(
        {"dvr": BatchPlaybackRequest(playback=CreateTokenRequest(dvr=True))}
    )
    dumped = sources.model_dump(mode="json", exclude_none=True)
    assert dumped["dvr"]["playback"]["dvr"] is True


def test_list_jobs_response_parses():
    response = ListJobsResponse.model_validate(
        {
            "jobs": [
                {
                    "id": "job1",
                    "name": "Test",
                    "region": "us-east-1",
                    "type": "channel",
                    "state": {"processing_state": "on", "ingest_state": "connected"},
                }
            ]
        }
    )
    assert response.jobs is not None
    job0 = response.jobs[0]
    assert job0.id == "job1"
    assert job0.state is not None
    assert job0.state.processing_state is not None
    assert job0.state.processing_state.value == "on"
