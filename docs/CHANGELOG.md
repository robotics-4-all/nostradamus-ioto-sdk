# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and configuration
- Phase 1: Foundation complete (pyproject.toml, Makefile, CI/CD)

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
