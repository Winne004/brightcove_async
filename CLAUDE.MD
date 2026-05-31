# CLAUDE.MD

Repository guidance for AI coding agents and contributors working on `brightcove_async`.

## Project Summary

- Package: `brightcove_async`
- Purpose: async Python client for Brightcove APIs (CMS, Analytics, Audience, Syndication, Dynamic Ingest, Ingest Profiles)
- Python: `>=3.13`
- Package manager: `uv` only
- Core stack: `aiohttp`, `pydantic`, `pydantic-settings`, `aiolimiter`, `tenacity`

## Mandatory Tooling Rules

- Use `uv` exclusively for dependency management and command execution.
- Never use `pip`, `poetry`, or `conda` directly in this repo.

Common commands:

- Install/sync env: `uv sync`
- Add runtime dependency: `uv add <package>`
- Add dev dependency: `uv add --group dev <package>`
- Remove dependency: `uv remove <package>`
- Re-lock dependencies: `uv lock`

Run tools with `uv run`:

- Tests: `uv run pytest`
- Lint: `uv run ruff check --fix`
- Format: `uv run ruff format`
- Type check: `uv run ty check`
- Pre-commit (all files): `uv run pre-commit run --all-files`

## Local Development

1. Sync environment:
	 - `uv sync`
2. Set OAuth credentials for local integration use:
	 - `export CLIENT_ID="..."`
	 - `export CLIENT_SECRET="..."`
3. Run tests and quality checks before finishing changes:
	 - `uv run pytest`
	 - `uv run ruff check --fix`
	 - `uv run ruff format`
	 - `uv run ty check`

## Repository Layout

- `src/brightcove_async/client.py`: main async client/context manager, lazy service initialization.
- `src/brightcove_async/initialise.py`: factory `initialise_brightcove_client`.
- `src/brightcove_async/settings.py`: env-backed settings and API base URL config.
- `src/brightcove_async/oauth/oauth.py`: OAuth token retrieval and caching.
- `src/brightcove_async/services/`: API service wrappers.
- `src/brightcove_async/schemas/`: Pydantic models and request/query schemas.
- `src/brightcove_async/registry.py`: service registration and per-service rate limits.
- `tests/`: pytest suite for client, services, schemas, oauth, registry.
- `brightcove_open_api_specs/` and `openapi.yaml`: API spec inputs/reference files.

## Architecture Notes

### Client lifecycle

- Construct with `initialise_brightcove_client()`.
- Always use the client as an async context manager:
	- `async with client as c: ...`
- Internally, session and OAuth client are lazy-initialized.
- Services are lazy-loaded and cached by name on first access (`c.cms`, `c.analytics`, etc.).

### Request pipeline

- Service methods call `Base.fetch_data(...)`.
- `Base.fetch_data` responsibilities:
	- obtains OAuth headers (unless custom headers provided)
	- applies per-service rate limiting via `AsyncLimiter`
	- performs request with `aiohttp`
	- maps HTTP errors to custom Brightcove exceptions
	- retries transient failures via `tenacity`
	- validates/parses response with Pydantic models

### Service registry and limits

- `build_service_registry()` in `registry.py` defines service class, base URL, and request rate.
- If adding a new service, update:
	- `registry.py`
	- `client.py` service property
	- tests for registry/client behavior

## Change Patterns

### Adding a new endpoint to an existing service

1. Add or update schema models in `src/brightcove_async/schemas/`.
2. Add query/body params model in `schemas/params.py` when needed.
3. Add async method to the relevant service in `src/brightcove_async/services/`.
4. Use `fetch_data` with an explicit Pydantic model for all JSON endpoints — `fetch_data` is strictly for JSON request/response pairs where the response is validated against the model.
5. For non-JSON endpoints (e.g. DELETE with no response body, or `text/plain` responses), do **not** use `fetch_data`. Instead, call `self._session.request(...)` directly using `self.limiter` and `await self._oauth.headers`, and handle HTTP errors via a `_raise_for_status` helper that maps `aiohttp.ClientResponseError` to Brightcove exceptions. See `Syndication` service for the established pattern.
6. Add/extend tests in `tests/test_<service>_service.py`.

### Adding a new service

1. Create service class in `src/brightcove_async/services/` inheriting `Base`.
2. Register it in `src/brightcove_async/registry.py` with suitable RPS limit.
3. Expose it as a property on `BrightcoveClient` in `src/brightcove_async/client.py`.
4. Add unit tests for lazy initialization and service methods.

## Testing Expectations

- Use `pytest` with `pytest-asyncio` for async methods.
- Prefer mocking `fetch_data` in service tests unless explicitly testing shared request behavior.
- For request/exception behavior, add tests in `test_base_service.py`.
- Keep tests deterministic and offline by default.

## Style and Quality

- Keep code fully typed and async-first.
- Reuse existing patterns for service methods and model validation.
- Avoid introducing blocking I/O in async paths.
- Keep public API changes intentional and reflected in tests.

## Notes for Agents

- Before editing, inspect related service + tests to preserve project patterns.
- Prefer minimal, focused changes over broad refactors.
- If changing behavior, update or add tests in the same PR.
- Run quality checks with `uv run` commands before concluding work.