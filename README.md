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
from brightcove_async.schemas import CreateVideoRequestBodyFields, State


async def main() -> None:
    client = brightcove_async.initialise_brightcove_client()
    async with client as bc:
        video = await bc.cms.create_video(
            account_id="12345",
            video_data=CreateVideoRequestBodyFields(
                name="My Video",
                state=State.ACTIVE,
            ),
        )
        print(video.model_dump())


if __name__ == "__main__":
    asyncio.run(main())
```

Services are exposed as properties on the client (`bc.cms`, `bc.analytics`, `bc.audience`, `bc.syndication`, `bc.dynamic_ingest`, `bc.ingest_profiles`) and are created lazily on first access.

Schema models can be imported from the top-level `brightcove_async.schemas` namespace or directly from the submodule:

```python
# Top-level convenience (any model from any service)
from brightcove_async.schemas import Video, Playlist, GetVideosQueryParams

# Direct submodule import (preferred when using many CMS types)
from brightcove_async.schemas.cms_model import VideoVariant, FolderCreateFields
from brightcove_async.schemas.params import GetVideosQueryParams
```

## Usage

### CMS

```python
from brightcove_async.schemas import (
    CreateVideoRequestBodyFields,
    UpdateVideoRequestBodyFields,
    GetVideosQueryParams,
    PlaylistInputFields,
    FolderCreateFields,
    RemoteAssetBody,
)

async with client as bc:
    ACCOUNT = "12345"

    # ── Videos ────────────────────────────────────────────────────────────────

    # Single page
    videos = await bc.cms.get_videos(
        account_id=ACCOUNT,
        params=GetVideosQueryParams(limit=20, sort="-created_at"),
    )

    # All videos, fetched concurrently page by page
    all_videos = await bc.cms.get_videos_for_account(account_id=ACCOUNT, page_size=100)

    # Create / update / delete
    video = await bc.cms.create_video(
        account_id=ACCOUNT,
        video_data=CreateVideoRequestBodyFields(name="My Video"),
    )
    await bc.cms.update_video(
        account_id=ACCOUNT,
        video_id=video.id,
        video_data=UpdateVideoRequestBodyFields(tags=["tutorial"]),
    )
    await bc.cms.delete_video(account_id=ACCOUNT, video_ids=[video.id])

    # ── Playlists ──────────────────────────────────────────────────────────────

    playlist = await bc.cms.create_playlist(
        account_id=ACCOUNT,
        playlist_data=PlaylistInputFields(name="My Playlist", type="EXPLICIT"),
    )
    await bc.cms.update_playlist(
        account_id=ACCOUNT,
        playlist_id=playlist.id,
        playlist_data=PlaylistInputFields(name="Renamed"),
    )
    await bc.cms.delete_playlist(account_id=ACCOUNT, playlist_id=playlist.id)

    # ── Folders ────────────────────────────────────────────────────────────────

    folder = await bc.cms.create_folder(
        account_id=ACCOUNT,
        folder_data=FolderCreateFields(name="Archive"),
    )
    await bc.cms.add_video_to_folder(
        account_id=ACCOUNT, folder_id=folder.id, video_id="6789"
    )

    # ── Remote assets (manifests / renditions) ─────────────────────────────────

    manifest = await bc.cms.add_hls_manifest(
        account_id=ACCOUNT,
        video_id="6789",
        body=RemoteAssetBody(remote_url="https://cdn.example.com/master.m3u8"),
    )
    await bc.cms.delete_hls_manifest(
        account_id=ACCOUNT, video_id="6789", asset_id=manifest.id
    )

    # ── Subscriptions ──────────────────────────────────────────────────────────

    from brightcove_async.schemas import SubscriptionCreateFields, Event

    sub = await bc.cms.create_subscription(
        account_id=ACCOUNT,
        subscription_data=SubscriptionCreateFields(
            endpoint="https://my.app/webhook",
            events=[Event.video_change],
        ),
    )
    await bc.cms.delete_subscription(account_id=ACCOUNT, subscription_id=sub.id)
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

### CMS (`bc.cms`)

| Resource | Methods |
| --- | --- |
| Videos | `get_videos`, `create_video`, `update_video`, `delete_video`, `get_videos_for_account`*, `get_video_count`, `get_video_by_id` |
| Video sources / images | `get_video_sources`, `get_video_images`, `delete_video_image`, `get_clear_video`, `get_video_clear_sources` |
| Video variants | `get_video_variants`, `create_video_variant`, `get_video_variant`, `update_video_variant`, `delete_video_variant` |
| Audio tracks | `get_video_audio_tracks`, `get_video_audio_track`, `update_video_audio_track`, `delete_video_audio_track` |
| Digital master | `get_digital_master_info`, `delete_digital_master` |
| Ingest jobs | `get_status_of_ingest_jobs`, `get_ingest_job_status` |
| Playlist references | `get_playlists_for_video`, `remove_video_from_all_playlists` |
| Playlists | `get_playlists`, `create_playlist`, `get_playlist_count`, `get_playlist`, `update_playlist`, `delete_playlist`, `get_videos_in_playlist`, `get_video_count_in_playlist` |
| Custom fields | `get_all_video_fields`, `get_video_fields`, `create_custom_field`, `get_custom_field`, `update_custom_field`, `delete_custom_field` |
| Folders | `get_folders`, `create_folder`, `get_folder`, `update_folder`, `delete_folder`, `get_videos_in_folder`, `add_video_to_folder`, `remove_video_from_folder` |
| Labels | `get_labels`, `create_label`, `update_label`, `delete_label` |
| Channels | `list_channels`, `get_channel_details`, `update_channel`, `list_channel_affiliates`, `add_affiliate`, `remove_affiliate` |
| Contracts | `list_contracts`, `get_contract`, `approve_contract` |
| Video shares | `list_shares`, `share_video`, `get_share`, `unshare_video` |
| Subscriptions | `get_subscriptions`, `create_subscription`, `get_subscription`, `delete_subscription` |
| Assets | `get_assets`, `get_dynamic_renditions` |
| HLS manifests | `get_hls_manifests`, `add_hls_manifest`, `get_hls_manifest`, `update_hls_manifest`, `delete_hls_manifest` |
| DASH manifests | `get_dash_manifests`, `add_dash_manifest`, `get_dash_manifest`, `update_dash_manifest`, `delete_dash_manifest` |
| HDS manifests | `get_hds_manifests`, `add_hds_manifest`, `get_hds_manifest`, `update_hds_manifest`, `delete_hds_manifest` |
| ISM manifests | `get_ism_manifests`, `add_ism_manifest`, `get_ism_manifest`, `update_ism_manifest`, `delete_ism_manifest` |
| ISMC manifests | `get_ismc_manifests`, `add_ismc_manifest`, `get_ismc_manifest`, `update_ismc_manifest`, `delete_ismc_manifest` |
| Renditions | `add_rendition`, `get_rendition`, `update_rendition`, `delete_rendition` |

\* Paginated helper that fetches all pages concurrently.

### Other services

| Service | Methods |
| --- | --- |
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
