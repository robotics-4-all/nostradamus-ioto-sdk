# Nostradamus IoTO Python SDK

**Generated:** 2026-02-13 | **Commit:** 30c57d9 | **Branch:** main

## OVERVIEW

Python SDK for Nostradamus IoT Observatory API. Provides sync/async clients, Pydantic models, CLI (`nioto`), auto-retry, rate limiting, and dual auth (OAuth2 + API Key). Built on httpx + Pydantic v2.

## STRUCTURE

```
nostradamus-ioto-sdk/
├── nostradamus_ioto_sdk/        # SDK package (see subdir AGENTS.md)
│   ├── models/                  # Pydantic models (see subdir AGENTS.md)
│   ├── resources/               # API resource classes (see subdir AGENTS.md)
│   ├── utils/                   # Pagination, caching, batch, validators
│   ├── cli/                     # Click CLI (nioto command)
│   ├── client.py                # Sync client entry point
│   ├── async_client.py          # Async client entry point
│   ├── auth.py                  # OAuth2Handler, APIKeyHandler
│   ├── _base_client.py          # Retry logic, response handling
│   ├── _http.py                 # ResponseCache, RateLimiter, should_retry
│   ├── _logging.py              # SDKLogger with credential masking
│   ├── config.py                # ClientConfig, RetryConfig dataclasses
│   └── exceptions.py            # Exception hierarchy
├── tests/
│   ├── unit/                    # 8 test modules (~1700 lines)
│   ├── integration/             # Empty (placeholder)
│   └── mocks/                   # fixtures.py, responses.py (both empty)
├── examples/                    # Runnable examples (basic, async, data ingestion)
├── scripts/                     # Dev utilities (diagnose, generate_models, test scripts)
├── docs/                        # MkDocs documentation
└── .github/workflows/           # CI: test.yml, publish.yml
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new API endpoint | `resources/` + `models/` | Create resource class + Pydantic models |
| Add CLI command | `cli/main.py` | Click groups: org, projects, collections, data, keys |
| Change auth behavior | `auth.py` | OAuth2Handler (token refresh), APIKeyHandler |
| Modify retry/error handling | `_base_client.py` | `handle_response()` maps status codes to exceptions |
| Add HTTP-level feature | `_http.py` | ResponseCache (LRU+TTL), RateLimiter (token bucket) |
| Add/modify data models | `models/` | Inherit from `models._base.BaseModel` |
| Configure SDK behavior | `config.py` | `ClientConfig.from_env()` reads NOSTRADAMUS_* env vars |
| Run tests | `make test` | Also: `make test-unit`, `make test-integration` |
| Format + lint | `make format && make lint` | black + isort + ruff + mypy |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `NostradamusClient` | class | `client.py` | Sync client — main SDK entry point |
| `AsyncNostradamusClient` | class | `async_client.py` | Async client — mirrors sync API with `a` prefix |
| `BaseResource` | class | `resources/_base.py` | Base for all resource classes |
| `BaseModel` | class | `models/_base.py` | Pydantic base with UUID/datetime serialization |
| `NostradamusError` | class | `exceptions.py` | Root exception — all SDK errors inherit from this |
| `ClientConfig` | dataclass | `config.py` | SDK configuration with env var support |
| `RetryConfig` | dataclass | `config.py` | Retry behavior (backoff, retryable status codes) |
| `OAuth2Handler` | class | `auth.py` | Thread-safe token management with auto-refresh |
| `APIKeyHandler` | class | `auth.py` | Simple X-API-Key header injection |
| `SDKLogger` | class | `_logging.py` | Structured logging with credential masking |
| `ResponseCache` | class | `_http.py` | LRU + TTL cache for GET responses |
| `RateLimiter` | class | `_http.py` | Token bucket rate limiter (sync + async) |
| `handle_response` | func | `_base_client.py` | Maps HTTP status codes to typed exceptions |
| `make_request_with_retry` | func | `_base_client.py` | Sync retry loop with exponential backoff |
| `make_async_request_with_retry` | func | `async_client.py` | Async retry loop (duplicated from _base_client) |
| `cli` | func | `cli/main.py` | Click CLI entry point (`nioto` command) |

## CONVENTIONS

- **Python >= 3.9** required (pyproject.toml)
- **Line length**: 88 (Black default)
- **Imports**: isort black-compatible profile. Standard -> Third-party -> Local
- **Docstrings**: Google style. Required on all public API
- **Type hints**: Required on public functions. mypy configured lenient (not strict)
- **Async methods**: Prefix with `a` (e.g., `list()` / `alist()`, `get()` / `aget()`)
- **Private modules**: Prefixed with `_` (e.g., `_base_client.py`, `_http.py`, `_logging.py`)
- **Resource pattern**: Each resource class inherits `BaseResource`, takes client in `__init__`, builds paths via `_build_path()`
- **Model pattern**: Inherit from `models._base.BaseModel` (wraps Pydantic with UUID/datetime encoders)
- **Error pattern**: `raise SpecificError(...) from err` — always preserve context
- **Logging**: `_logging.get_logger()` — never `print()`. Credentials auto-masked
- **Commits**: `<type>: <description>` (feat, fix, docs, test, refactor, chore)
- **Testing**: pytest with class-based grouping. `test_<what>_<condition>_<expected>`. Mock HTTP with `unittest.mock` + `respx`

## ANTI-PATTERNS (THIS PROJECT)

- **NEVER** use `print()` for output — use `_logging.SDKLogger`
- **NEVER** suppress exceptions with bare `except:` or `except Exception: pass`
- **NEVER** expose credentials in logs — `SDKLogger` masks automatically but verify
- **NEVER** retry on 401/403/422 — these are non-retryable (enforced in `_base_client.py`)
- **NEVER** import client types at module level in resources — use `TYPE_CHECKING` guard to avoid circular imports
- **DO NOT** modify `models/_generated.py` by hand — it's auto-generated via `scripts/generate_models.py`

## MYPY QUIRKS

- Resources module has `union-attr`, `misc`, `return-value` errors disabled (sync/async method coexistence)
- CLI module has `check_untyped_defs = false`
- Global config is lenient: `disallow_untyped_defs = false`

## COVERAGE OMISSIONS

These files are excluded from coverage (by design, not oversight):
`_generated.py`, `validators.py`, `_logging.py`, `async_client.py`, `_base_client.py`, `collections.py`, `data.py`, `project_keys.py`, `projects.py`

## COMMANDS

```bash
make install-dev          # Install with dev+cli+docs deps
make test                 # pytest with coverage
make test-unit            # Unit tests only
make lint                 # black --check + isort --check + ruff + mypy
make format               # black + isort
make typecheck            # mypy only
make docs                 # mkdocs serve
make build                # python -m build
make clean                # Remove all artifacts
make ci                   # lint + typecheck + test (CI pipeline)
```

## NOTES

- **Dual client architecture**: Sync and async clients share resource classes. Resources detect client type at runtime. Async methods duplicated (not DRY) in `async_client.py` — intentional for clarity
- **Create endpoints**: `projects.create()` handles APIs that return just an ID or a message containing a UUID — it re-fetches the full object. This is a workaround for inconsistent API responses
- **conftest.py is empty**: Shared test fixtures live in test classes, not conftest
- **mocks/ directory is empty**: `fixtures.py` and `responses.py` are placeholder files
- **integration/ is empty**: No integration tests exist yet
- **API base URL**: `https://nostradamus-ioto.issel.ee.auth.gr` (hardcoded default)
- **CLI command name**: `nioto` (not `nostradamus`)
