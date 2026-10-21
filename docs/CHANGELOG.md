# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `DailyBreakdownItem` model for collection-key statistics daily buckets

### Fixed (verified live against Cenotoo API)
- Organization routes no longer append a hardcoded org name: the API exposes
  only `/organization` scoped to the caller's JWT; `update()` now refetches
  via `get()` since the server returns `{message}`
- `projects`/`collections` `list()` unwrap the server's paginated
  `{items, total, ...}` envelope; `create()` unwraps the nested
  `{id: {project_id}}` response; `update()` refetches via `get()`
- `project_keys` `create()` unwraps the nested key id; `get()` resolves via
  list+match (no single-key server route, miss raises
  `ResourceNotFoundError`); `regenerate()`/`delete()` use the real body-based
  `PUT .../keys/regenerate` / `DELETE .../keys/delete_key` routes and return
  `ProjectKeyResponse` (`.api_key`)
- `users.update_password()`/`delete()` take `organization_id` and hit the real
  org-scoped routes; `list()` unwraps the envelope to plain usernames
- `KeyStatisticsResponse.daily_breakdown` is a list of `{date, record_count}`
  items, matching the server payload

## [0.1.0] - TBD

### Added
- Synchronous client for all API endpoints
- Asynchronous client with full async/await support
- OAuth2 and API Key authentication
- Comprehensive Pydantic models for all API resources
- Automatic retry with exponential backoff
- Adaptive rate limiting
- Optional response caching
- CLI tool for common operations
- Full test suite with >85% coverage
- Complete documentation with examples

### API Coverage
- Authentication (OAuth2 password flow)
- Organization management
- Project CRUD operations
- Project key management (read/write/master)
- Collection CRUD operations
- Data operations (send, get, delete)
- Statistics and aggregations

[Unreleased]: https://github.com/nostradamus/nostradamus-ioto-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nostradamus/nostradamus-ioto-sdk/releases/tag/v0.1.0
