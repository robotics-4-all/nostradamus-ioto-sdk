# nostradamus_ioto_sdk — SDK Package

## OVERVIEW

Core SDK package. Dual sync/async clients, auth, HTTP infrastructure, exception hierarchy.

## DEPENDENCY LAYERS

```
Layer 1 (Foundation — no internal deps):
  exceptions.py, config.py, _logging.py

Layer 2 (Core utilities):
  _http.py → config
  auth.py  → exceptions

Layer 3 (Client infrastructure):
  _base_client.py → _http, config, exceptions

Layer 4 (Public clients):
  client.py       → auth, _base_client, _logging, config, exceptions, resources/*
  async_client.py → auth, _base_client, _logging, config, exceptions, resources/*

Layer 5 (CLI):
  cli/main.py → client, exceptions, models.enums
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Add auth method | `auth.py` | Implement `get_headers() -> Dict[str,str]` |
| Add exception type | `exceptions.py` | Inherit `APIError` (with status) or `NostradamusError` (without) |
| Change retry logic | `_base_client.py` | `make_request_with_retry()` — sync only |
| Change async retry | `async_client.py` | `make_async_request_with_retry()` — duplicated intentionally |
| Add config option | `config.py` | Add field to `ClientConfig`, update `from_env()` |
| Wire new resource | `client.py` + `async_client.py` | Add `self.foo = FooResource(self)` in both `__init__` |

## EXCEPTION HIERARCHY

```
NostradamusError
├── ConfigurationError          (SDK misconfiguration, no status code)
├── AuthenticationError         (401/403)
└── APIError                    (generic HTTP errors)
    ├── ValidationError         (422, carries `errors` list)
    ├── ResourceNotFoundError   (404)
    ├── RateLimitError          (429, carries `retry_after`)
    ├── TimeoutError            (request timeout)
    └── ConnectionError         (connection failure)
```

## AUTH FLOW

- **API Key**: `APIKeyHandler` → injects `X-API-Key` header. Stateless.
- **OAuth2**: `OAuth2Handler` → password grant to `/api/v1/token`. Thread-safe token cache with auto-refresh (60s buffer before expiry). Uses `threading.Lock`.
- Client `__init__` enforces mutual exclusivity: api_key XOR (username + password)

## UTILS SUBPACKAGE

| File | Purpose | Status |
|------|---------|--------|
| `pagination.py` | Pagination helpers | Implemented |
| `cache.py` | Response caching utilities | Implemented |
| `batch.py` | Batch operation helpers | Implemented |
| `validators.py` | Custom validators | Implemented, excluded from coverage |

## CLI SUBPACKAGE

- Entry point: `nioto` (registered in pyproject.toml)
- Framework: Click with Rich for formatting
- Groups: `org`, `projects`, `collections`, `data`, `keys`
- Auth: `--api-key` flag or `NOSTRADAMUS_API_KEY` env var
- Output formats: `table` (default), `json`, `compact`

## ANTI-PATTERNS

- **NEVER** add `import` of client types outside `TYPE_CHECKING` in resources — causes circular imports
- **NEVER** add new retry-exempt exception without updating the `except` clause in `make_request_with_retry()` AND `make_async_request_with_retry()`
- When adding a new resource, must wire it in **both** `client.py` AND `async_client.py`
