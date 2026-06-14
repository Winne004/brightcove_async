# brightcove_async

`brightcove_async` is an asynchronous Python client for the [Brightcove](https://www.brightcove.com/) video platform APIs. It wraps Brightcove's REST endpoints in `asyncio`-friendly service classes, handles OAuth2 token management for you, and validates every request and response against Pydantic models.

## Features

- Async-first API built on `aiohttp`.
- OAuth2 client-credentials auth with automatic token caching and refresh.
- Pydantic models for request bodies, query parameters, and responses, giving you validation and editor autocompletion.
- Per-service rate limiting via `aiolimiter`.
- Automatic retries for transient failures (connection drops, `401`, `429`) with `tenacity`, including `Retry-After` support on rate-limited responses.
- Brightcove HTTP errors mapped to a typed exception hierarchy.
- Coverage for the CMS, Analytics, Audience, Syndication, Dynamic Ingest, and Ingest Profiles APIs.

## Installation

```bash
pip install brightcove_async
```

Requires Python 3.13 or newer.

## Authentication

The client authenticates with OAuth2 client credentials. Create an API authentication credential in Brightcove Studio, then provide the client ID and secret through environment variables:

```bash
export CLIENT_ID="your_client_id"
export CLIENT_SECRET="your_client_secret"
```

`initialise_brightcove_client()` reads these by default. To pass credentials explicitly instead, construct a `BrightcoveOAuthCreds`:

```python
import brightcove_async
from brightcove_async.settings import BrightcoveOAuthCreds

client = brightcove_async.initialise_brightcove_client(
    oauth_creds=BrightcoveOAuthCreds(
        client_id="your_client_id",
        client_secret="your_client_secret",
    ),
)
```

Tokens are fetched on first use and reused until they expire, so you don't manage them yourself.

## Quick start

Always use the client as an async context manager. The HTTP session and OAuth client are created on entry and cleaned up on exit.

```python
import asyncio

import brightcove_async
from brightcove_async.schemas.cms_model import (
    CreateVideoRequestBodyFields,
    State,
)


async def main() -> None:
    client = brightcove_async.initialise_brightcove_client()
    async with client as bc:
        video = await bc.cms.create_video(
            account_id="12345",
            video_data=CreateVideoRequestBodyFields(
                name="test",
                State=State.ACTIVE,
            ),
        )
        print(video.model_dump())


if __name__ == "__main__":
    asyncio.run(main())
```

Services are exposed as properties on the client (`bc.cms`, `bc.analytics`, `bc.audience`, `bc.syndication`, `bc.dynamic_ingest`, `bc.ingest_profiles`) and are created lazily on first access.

## Usage

### CMS

```python
from brightcove_async.schemas.params import GetVideosQueryParams

async with client as bc:
    # A single page of videos
    videos = await bc.cms.get_videos(
        account_id="12345",
        params=GetVideosQueryParams(limit=20, sort="-created_at"),
    )

    # Every video for an account, fetched page by page concurrently
    all_videos = await bc.cms.get_videos_for_account(
        account_id="12345",
        page_size=100,
    )

    video = await bc.cms.get_video_by_id(account_id="12345", video_id="6789")
    sources = await bc.cms.get_video_sources(account_id="12345", video_id="6789")
```

### Analytics

```python
from brightcove_async.schemas.params import GetAnalyticsReportParams

async with client as bc:
    report = await bc.analytics.get_analytics_report(
        params=GetAnalyticsReportParams(
            accounts="12345",
            dimensions="video",
            from_="2026-01-01",
            to="2026-01-31",
        ),
    )
    print(report.model_dump())
```

### Audience

```python
from brightcove_async.schemas.params import GetLeadsParams, GetViewEventsParams

async with client as bc:
    leads = await bc.audience.get_leads(
        account_id="12345",
        params=GetLeadsParams(limit=10, sort="created_at"),
    )
    view_events = await bc.audience.get_view_events(
        account_id="12345",
        params=GetViewEventsParams(limit=10),
    )
```

### Dynamic Ingest

```python
from brightcove_async.schemas.dynamic_ingest_model import IngestMediaAssetbody

async with client as bc:
    result = await bc.dynamic_ingest.ingest_videos_and_assets(
        account_id="12345",
        video_id="6789",
        video_or_asset_data=IngestMediaAssetbody(
            master={"url": "https://example.com/master.mp4"},
        ),
    )
```

### Bringing your own session

By default the client opens and closes its own `aiohttp.ClientSession`. To share a session you manage elsewhere, pass it to `BrightcoveClient` directly; in that case the client leaves the session open when the context manager exits.

```python
import aiohttp
from brightcove_async.client import BrightcoveClient
from brightcove_async.oauth.oauth import OAuthClient
from brightcove_async.registry import build_service_registry
from brightcove_async.settings import BrightcoveBaseAPIConfig

async with aiohttp.ClientSession() as session:
    client = BrightcoveClient(
        services_registry=build_service_registry(BrightcoveBaseAPIConfig()),
        client_id="your_client_id",
        client_secret="your_client_secret",
        oauth_cls=OAuthClient,
        session=session,
    )
    async with client as bc:
        videos = await bc.cms.get_videos(account_id="12345")
```

## Error handling

HTTP errors are translated into a typed exception hierarchy rooted at `BrightcoveError`. Catch the base class to handle any API failure, or a specific subclass for finer control.

```python
from brightcove_async.exceptions import (
    BrightcoveError,
    BrightcoveResourceNotFoundError,
    BrightcoveTooManyRequestsError,
)

async with client as bc:
    try:
        video = await bc.cms.get_video_by_id(account_id="12345", video_id="000")
    except BrightcoveResourceNotFoundError:
        ...  # 404
    except BrightcoveTooManyRequestsError as exc:
        print(exc.retry_after)  # seconds, when the server sends Retry-After
    except BrightcoveError as exc:
        print(exc.status_code, exc.endpoint, exc.details)
```

Status codes map to exceptions as follows:

| Status | Exception |
| --- | --- |
| 400 | `BrightcoveBadValueError` |
| 401 | `BrightcoveAuthError` |
| 403 | `BrightcoveForbiddenError` |
| 404 | `BrightcoveResourceNotFoundError` |
| 405 | `BrightcoveMethodNotAllowedError` |
| 409 | `BrightcoveConflictError` |
| 429 | `BrightcoveTooManyRequestsError` |
| 5xx / unknown | `BrightcoveUnknownError` |

Connection failures raise `BrightcoveConnectionError`. Transient errors (`BrightcoveConnectionError`, `BrightcoveAuthError`, `BrightcoveTooManyRequestsError`) are retried automatically before propagating.

## Rate limiting

Each service has its own request-per-second budget enforced by an `AsyncLimiter`. The CMS and Ingest Profiles services default to 4 requests per second; the rest default to 10. The limits live in [`registry.py`](src/brightcove_async/registry.py) and can be tuned per service.

## API coverage

| Service | Methods |
| --- | --- |
| `cms` | `get_videos`, `create_video`, `get_videos_for_account`, `get_video_count`, `get_video_fields`, `get_video_by_id`, `get_video_sources`, `get_video_images`, `get_video_variants`, `get_video_variant`, `get_video_audio_tracks`, `get_video_audio_track`, `get_digital_master_info`, `get_playlists_for_video`, `get_status_of_ingest_jobs`, `get_ingest_job_status`, `list_channels`, `get_channel_details`, `list_channel_affiliates`, `list_contracts`, `get_contract`, `list_shares` |
| `analytics` | `get_account_engagement`, `get_player_engagement`, `get_video_engagement`, `get_analytics_report`, `get_available_date_range`, `get_alltime_video_views` |
| `audience` | `get_leads`, `get_view_events` |
| `syndication` | `get_all_syndications`, `get_syndication`, `create_syndication`, `update_syndication`, `patch_syndication`, `delete_syndication`, `get_template`, `upload_template` |
| `dynamic_ingest` | `ingest_videos_and_assets`, `get_temporary_s3_urls` |
| `ingest_profiles` | `get_ingest_profiles` |

## Development

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management and task running.

```bash
uv sync                       # create the environment
uv run pytest                 # run the test suite
uv run ruff check --fix       # lint
uv run ruff format            # format
uv run ty check               # type check
uv run pre-commit run --all-files
```

## Documentation

- [Brightcove API reference](https://apis.support.brightcove.com/)

## Contributing

Pull requests are welcome. Please open an issue to discuss a feature or bug fix before submitting a PR, and include tests for any behavior change.

## License

MIT License. See [LICENSE.txt](LICENSE.txt).

## Disclaimer

This project is not affiliated with or endorsed by Brightcove Inc.
</content>
</invoke>
