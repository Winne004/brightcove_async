import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.live_model import (
    AdConfigResponse,
    AdConfiguration,
    AutoStopGetResponse,
    BatchGenerateSourcesResponse,
    BatchPlaybackRequestMap,
    ClipListAccountResponse,
    ClipRequest,
    ClipResponse,
    ClipScheduleRequest,
    ClipWorkflowResponse,
    ConfigureJobRequest,
    CreateTokenRequest,
    CreateTokenResponse,
    DeleteAdConfigResponse,
    FinishJobResponse,
    ForceFailoverRequest,
    ForceFailoverResponse,
    GeneratePlaybackURLResponse,
    GetAllSupportedMetricsResponse,
    GetBYOCDNTokensResponse,
    GetJobMetricsResponse,
    GetResourceSessionsResponse,
    GetSessionResponse,
    GetThumbnailResponse,
    HealthCheck,
    InsertCuePointRequest,
    Job,
    JobConfig,
    JobStartStopCreateRequest,
    JobStartStopResponse,
    JobStartStopUpdateRequest,
    ListAdConfigsResponse,
    ListJobsResponse,
    NotificationsResponse,
    ResetOriginResponse,
    SessionEventList,
    StartJobResponse,
    StopJobResponse,
    UpdateJobResponse,
)
from brightcove_async.schemas.params import (
    GeneratePlaybackURLParams,
    GetLiveJobMetricsParams,
    ListLiveJobsParams,
    LiveResourceSessionsParams,
    LiveSchedulerListParams,
)
from brightcove_async.services.base import Base


class Live(Base):
    """Brightcove NextGen Live API (v2) service.

    Wraps the live streaming platform at ``https://api.live.brightcove.com``,
    covering job lifecycle (configure/start/stop/finish), live clipping,
    scheduling, SSAI ad configuration, playback tokens, sessions, metrics, and
    notifications. All authenticated endpoints use the shared OAuth flow via
    ``Base.fetch_data``.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 10,
    ) -> None:
        super().__init__(session=session, oauth=oauth, base_url=base_url, limit=limit)

    def _jobs_url(self, account_id: str) -> str:
        return f"{self.base_url}/v2/accounts/{account_id}/jobs"

    # ── Jobs ──────────────────────────────────────────────────────────────────

    async def list_jobs(
        self,
        account_id: str,
        params: ListLiveJobsParams | None = None,
    ) -> ListJobsResponse:
        """List all live jobs in an account, with optional filtering."""
        return await self.fetch_data(
            endpoint=self._jobs_url(account_id),
            model=ListJobsResponse,
            params=params.serialize_params() if params else None,
        )

    async def create_job(
        self,
        account_id: str,
        job: ConfigureJobRequest,
    ) -> Job:
        """Configure (create) a new live job."""
        return await self.fetch_data(
            endpoint=self._jobs_url(account_id),
            model=Job,
            method="POST",
            payload=job,
        )

    async def get_job(self, account_id: str, job_id: str) -> Job:
        """Retrieve full details and current state of a live job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}",
            model=Job,
        )

    async def update_job(
        self,
        account_id: str,
        job_id: str,
        config: JobConfig,
    ) -> UpdateJobResponse:
        """Update an existing live job (job must be in the ``off`` state)."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}",
            model=UpdateJobResponse,
            method="PUT",
            payload=config,
        )

    async def finish_job(self, account_id: str, job_id: str) -> FinishJobResponse:
        """Permanently archive (finish) a live job. This cannot be undone."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}",
            model=FinishJobResponse,
            method="DELETE",
        )

    async def clip_job(
        self,
        account_id: str,
        job_id: str,
        clip: ClipRequest,
    ) -> ClipResponse:
        """Create a VOD clip from a live stream time range."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/clip",
            model=ClipResponse,
            method="POST",
            payload=clip,
        )

    async def force_failover(
        self,
        account_id: str,
        job_id: str,
        request: ForceFailoverRequest,
    ) -> ForceFailoverResponse:
        """Manually fail over to a different encoding pipeline (redundant jobs)."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/failover",
            model=ForceFailoverResponse,
            method="PUT",
            payload=request,
        )

    async def reset_origin(self, account_id: str, job_id: str) -> ResetOriginResponse:
        """Flush the DVR and timeshift/startover buffer for a job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/reset_origin",
            model=ResetOriginResponse,
            method="POST",
        )

    async def start_job(self, account_id: str, job_id: str) -> StartJobResponse:
        """Start a previously configured live job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/start",
            model=StartJobResponse,
            method="PUT",
        )

    async def stop_job(self, account_id: str, job_id: str) -> StopJobResponse:
        """Gracefully stop a running live job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/stop",
            model=StopJobResponse,
            method="PUT",
        )

    async def get_thumbnail(
        self,
        account_id: str,
        job_id: str,
        pipeline_id: str | None = None,
    ) -> GetThumbnailResponse:
        """Retrieve thumbnail images generated from a processing job."""
        params = {"pipeline_id": pipeline_id} if pipeline_id else None
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/thumbnail",
            model=GetThumbnailResponse,
            params=params,
        )

    async def insert_cuepoint(
        self,
        account_id: str,
        job_id: str,
        request: InsertCuePointRequest,
    ) -> Job:
        """Insert an SSAI ad-break cue point into a running stream."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/cuepoint",
            model=Job,
            method="POST",
            payload=request,
        )

    async def get_job_metrics(
        self,
        account_id: str,
        job_id: str,
        params: GetLiveJobMetricsParams,
    ) -> GetJobMetricsResponse:
        """Retrieve performance metrics for a live job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/metrics",
            model=GetJobMetricsResponse,
            params=params.serialize_params(),
        )

    async def get_supported_metrics(
        self,
        account_id: str,
        job_id: str,
    ) -> GetAllSupportedMetricsResponse:
        """List all metrics available for monitoring a live job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/supported-metrics",
            model=GetAllSupportedMetricsResponse,
        )

    async def get_job_notifications(
        self,
        account_id: str,
        job_id: str,
        last_key: str | None = None,
    ) -> NotificationsResponse:
        """List notifications generated for a specific job."""
        params = {"last_key": last_key} if last_key else None
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/notifications",
            model=NotificationsResponse,
            params=params,
        )

    async def get_account_notifications(
        self,
        account_id: str,
        last_key: str | None = None,
    ) -> NotificationsResponse:
        """List notifications across all jobs in an account."""
        params = {"last_key": last_key} if last_key else None
        return await self.fetch_data(
            endpoint=f"{self.base_url}/v2/accounts/{account_id}/notifications",
            model=NotificationsResponse,
            params=params,
        )

    # ── Scheduler ───────────────────────────────────────────────────────────────

    async def list_schedules(
        self,
        account_id: str,
        job_id: str,
        params: LiveSchedulerListParams | None = None,
    ) -> JobStartStopResponse:
        """List all start/stop schedules for a job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/scheduler",
            model=JobStartStopResponse,
            params=params.serialize_params() if params else None,
        )

    async def get_autostop_schedule(
        self,
        account_id: str,
        job_id: str,
    ) -> AutoStopGetResponse:
        """Retrieve the auto-stop schedule configured for a job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/scheduler/autostop",
            model=AutoStopGetResponse,
        )

    async def create_jobstartstop_schedule(
        self,
        account_id: str,
        job_id: str,
        request: JobStartStopCreateRequest,
    ) -> JobStartStopResponse:
        """Schedule automatic start/stop times for a job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/scheduler/jobstartstop",
            model=JobStartStopResponse,
            method="POST",
            payload=request,
        )

    async def get_jobstartstop_schedule(
        self,
        account_id: str,
        job_id: str,
        workflow_id: str,
    ) -> JobStartStopResponse:
        """Retrieve a specific start/stop schedule for a job."""
        return await self.fetch_data(
            endpoint=(
                f"{self._jobs_url(account_id)}/{job_id}"
                f"/scheduler/jobstartstop/{workflow_id}"
            ),
            model=JobStartStopResponse,
        )

    async def update_jobstartstop_schedule(
        self,
        account_id: str,
        job_id: str,
        workflow_id: str,
        request: JobStartStopUpdateRequest,
    ) -> JobStartStopResponse:
        """Update an existing start/stop schedule for a job."""
        return await self.fetch_data(
            endpoint=(
                f"{self._jobs_url(account_id)}/{job_id}"
                f"/scheduler/jobstartstop/{workflow_id}"
            ),
            model=JobStartStopResponse,
            method="PUT",
            payload=request,
        )

    async def delete_jobstartstop_schedule(
        self,
        account_id: str,
        job_id: str,
        workflow_id: str,
    ) -> JobStartStopResponse:
        """Delete a scheduled start/stop workflow for a job."""
        return await self.fetch_data(
            endpoint=(
                f"{self._jobs_url(account_id)}/{job_id}"
                f"/scheduler/jobstartstop/{workflow_id}"
            ),
            model=JobStartStopResponse,
            method="DELETE",
        )

    async def list_scheduled_clips(
        self,
        account_id: str,
        job_id: str,
        params: LiveSchedulerListParams | None = None,
    ) -> ClipListAccountResponse:
        """List scheduled clips for a job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/scheduler/clips",
            model=ClipListAccountResponse,
            params=params.serialize_params() if params else None,
        )

    async def create_scheduled_clip(
        self,
        account_id: str,
        job_id: str,
        request: ClipScheduleRequest,
    ) -> ClipWorkflowResponse:
        """Create a scheduled clip for a job."""
        return await self.fetch_data(
            endpoint=f"{self._jobs_url(account_id)}/{job_id}/scheduler/clips",
            model=ClipWorkflowResponse,
            method="POST",
            payload=request,
        )

    async def get_scheduled_clip(
        self,
        account_id: str,
        job_id: str,
        workflow_id: str,
    ) -> ClipWorkflowResponse:
        """Retrieve a specific scheduled clip for a job."""
        return await self.fetch_data(
            endpoint=(
                f"{self._jobs_url(account_id)}/{job_id}/scheduler/clips/{workflow_id}"
            ),
            model=ClipWorkflowResponse,
        )

    async def update_scheduled_clip(
        self,
        account_id: str,
        job_id: str,
        workflow_id: str,
        request: ClipScheduleRequest,
    ) -> ClipWorkflowResponse:
        """Update a scheduled clip for a job."""
        return await self.fetch_data(
            endpoint=(
                f"{self._jobs_url(account_id)}/{job_id}/scheduler/clips/{workflow_id}"
            ),
            model=ClipWorkflowResponse,
            method="PATCH",
            payload=request,
        )

    async def delete_scheduled_clip(
        self,
        account_id: str,
        job_id: str,
        workflow_id: str,
    ) -> ClipWorkflowResponse:
        """Cancel (delete) a scheduled clip for a job."""
        return await self.fetch_data(
            endpoint=(
                f"{self._jobs_url(account_id)}/{job_id}/scheduler/clips/{workflow_id}"
            ),
            model=ClipWorkflowResponse,
            method="DELETE",
        )

    # ── Playback ────────────────────────────────────────────────────────────────

    async def create_playback_token(
        self,
        account_id: str,
        job_id: str,
        request: CreateTokenRequest,
    ) -> CreateTokenResponse:
        """Create a playback token for a job."""
        return await self.fetch_data(
            endpoint=f"{self.base_url}/v2/accounts/{account_id}/playback/{job_id}/token",
            model=CreateTokenResponse,
            method="POST",
            payload=request,
        )

    async def generate_batch_sources(
        self,
        account_id: str,
        job_id: str,
        sources: BatchPlaybackRequestMap,
    ) -> BatchGenerateSourcesResponse:
        """Generate multiple labelled playback source configurations at once."""
        return await self.fetch_data(
            endpoint=(
                f"{self.base_url}/v2/accounts/{account_id}"
                f"/playback/{job_id}/sources/batch"
            ),
            model=BatchGenerateSourcesResponse,
            method="POST",
            payload=sources,
        )

    async def generate_playback_url(
        self,
        job_id: str,
        params: GeneratePlaybackURLParams,
    ) -> GeneratePlaybackURLResponse:
        """Generate a playback URL from a previously created playback token.

        This endpoint is unauthenticated; the account ID and playback token are
        supplied as query parameters.
        """
        return await self.fetch_data(
            endpoint=f"{self.base_url}/v2/playback/{job_id}",
            model=GeneratePlaybackURLResponse,
            params=params.serialize_params(),
            headers={},
        )

    # ── Sessions ──────────────────────────────────────────────────────────────

    async def get_session(
        self,
        account_id: str,
        session_id: str,
    ) -> GetSessionResponse:
        """Retrieve details about a specific playback session."""
        return await self.fetch_data(
            endpoint=f"{self.base_url}/v2/accounts/{account_id}/sessions/{session_id}",
            model=GetSessionResponse,
        )

    async def get_session_events(
        self,
        account_id: str,
        session_id: str,
    ) -> SessionEventList:
        """Retrieve all events for a specific playback session."""
        return await self.fetch_data(
            endpoint=(
                f"{self.base_url}/v2/accounts/{account_id}/sessions/{session_id}/events"
            ),
            model=SessionEventList,
        )

    async def get_resource_sessions(
        self,
        account_id: str,
        resource_id: str,
        params: LiveResourceSessionsParams | None = None,
    ) -> GetResourceSessionsResponse:
        """Retrieve all playback sessions for a resource (job)."""
        return await self.fetch_data(
            endpoint=(
                f"{self.base_url}/v2/accounts/{account_id}"
                f"/sessions/resource/{resource_id}"
            ),
            model=GetResourceSessionsResponse,
            params=params.serialize_params() if params else None,
        )

    # ── Settings ──────────────────────────────────────────────────────────────

    async def list_cdn_tokens(self, account_id: str) -> GetBYOCDNTokensResponse:
        """List BYO CDN tokens registered to an account."""
        return await self.fetch_data(
            endpoint=f"{self.base_url}/v2/accounts/{account_id}/settings/cdns/tokens",
            model=GetBYOCDNTokensResponse,
        )

    # ── SSAI ──────────────────────────────────────────────────────────────────

    async def list_ad_configs(self, account_id: str) -> ListAdConfigsResponse:
        """List all SSAI ad configurations for an account."""
        return await self.fetch_data(
            endpoint=f"{self.base_url}/v2/accounts/{account_id}/ssai/ad-configs",
            model=ListAdConfigsResponse,
        )

    async def create_ad_config(
        self,
        account_id: str,
        config: AdConfiguration,
    ) -> AdConfiguration:
        """Create a new SSAI ad configuration."""
        return await self.fetch_data(
            endpoint=f"{self.base_url}/v2/accounts/{account_id}/ssai/ad-configs",
            model=AdConfiguration,
            method="POST",
            payload=config,
        )

    async def get_ad_config(
        self,
        account_id: str,
        ad_config_id: str,
    ) -> AdConfigResponse:
        """Retrieve a specific SSAI ad configuration."""
        return await self.fetch_data(
            endpoint=(
                f"{self.base_url}/v2/accounts/{account_id}"
                f"/ssai/ad-configs/{ad_config_id}"
            ),
            model=AdConfigResponse,
        )

    async def update_ad_config(
        self,
        account_id: str,
        ad_config_id: str,
        config: AdConfiguration,
    ) -> AdConfigResponse:
        """Update an existing SSAI ad configuration."""
        return await self.fetch_data(
            endpoint=(
                f"{self.base_url}/v2/accounts/{account_id}"
                f"/ssai/ad-configs/{ad_config_id}"
            ),
            model=AdConfigResponse,
            method="PUT",
            payload=config,
        )

    async def delete_ad_config(
        self,
        account_id: str,
        ad_config_id: str,
    ) -> DeleteAdConfigResponse:
        """Delete an SSAI ad configuration. This cannot be undone."""
        return await self.fetch_data(
            endpoint=(
                f"{self.base_url}/v2/accounts/{account_id}"
                f"/ssai/ad-configs/{ad_config_id}"
            ),
            model=DeleteAdConfigResponse,
            method="DELETE",
        )

    # ── Misc ──────────────────────────────────────────────────────────────────

    async def healthcheck(self) -> HealthCheck:
        """Check the health and availability of the Live API (unauthenticated)."""
        return await self.fetch_data(
            endpoint=f"{self.base_url}/v2/healthcheck",
            model=HealthCheck,
            headers={},
        )
