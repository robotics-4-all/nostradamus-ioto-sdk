# Integration Tests

## Two Kinds of Integration Test

| Suite | File | Backend | Runs by default |
|-------|------|---------|-----------------|
| Live API (active) | `test_live_api.py` | Real Nostradamus API | No - skipped without credentials |
| Mocked (disabled) | `test_client_integration.py.disabled` | `respx` mocks | Never (`.disabled` suffix) |

Only `test_live_api.py` is collected. It is read-only (health, organization,
project listing) and therefore safe to point at production.

## Running the Live Suite

```bash
export NOSTRADAMUS_API_KEY='your-api-key'   # or the OAuth2 pair below
# export NOSTRADAMUS_USERNAME='user'
# export NOSTRADAMUS_PASSWORD='pass'

make test-integration
# or
pytest tests/integration/ -v --no-cov
```

Optional variables:

| Variable | Purpose |
|----------|---------|
| `NOSTRADAMUS_BASE_URL` | Override the API base URL |
| `NOSTRADAMUS_PROJECT_ID` | Enables the project-by-id test |

Every test carries the `integration` marker (`pytestmark`). Without
credentials the fixtures call `pytest.skip(...)`, so the suite reports
`6 skipped` and exits 0.

`make test-integration` fails loudly (exit 1) when pytest collects zero tests,
so an empty directory can no longer masquerade as a passing run.

## Why the Mocked Suite Is Disabled

`test_client_integration.py.disabled` mocks responses that do not match the
real API:

1. **Wrong endpoints** - mocks `/api/v1/organization`; the SDK calls
   `/api/v1/organization` scoped to the caller's auth context.
2. **Wrong field names** - mocks `id`, `name`, `created_at`; models use
   `organization_id`, `organization_name`, `creation_date`.
3. **Missing UUID extraction** - `projects.create()` extracts the UUID from
   the response message, which the mocks do not emulate.
4. **Filter format** - the API requires JSON-encoded filter strings, not dicts.

Re-enabling it means recreating mocks against the live contract - the same
drift that caused the disable. The live suite is the maintained path.

## Unit Tests

```bash
make test-unit
# or
pytest tests/unit/ -v
```
