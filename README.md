# Nostradamus IoTO Python SDK

[![PyPI version](https://img.shields.io/pypi/v/nostradamus-ioto-sdk.svg)](https://pypi.org/project/nostradamus-ioto-sdk/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI](https://img.shields.io/github/actions/workflow/status/nostradamus/nostradamus-ioto-sdk/test.yml?branch=main)](https://github.com/nostradamus/nostradamus-ioto-sdk/actions)

A production-ready Python client for the [Nostradamus IoT Observatory](https://nostradamus-ioto.issel.ee.auth.gr) API. Manage IoT projects, collections, and time-series data with a clean, typed interface.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Error Handling](#error-handling)
- [CLI](#cli)
- [Examples](#examples)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | Description |
|---------|-------------|
| **Sync & Async** | `NostradamusClient` and `AsyncNostradamusClient` share the same API surface |
| **Type Safety** | Full type hints with Pydantic v2 models for request/response validation |
| **Auto-Retry** | Exponential backoff with configurable retry policies |
| **Rate Limiting** | Token-bucket rate limiter (sync + async) |
| **Dual Auth** | OAuth2 (username/password) or API Key |
| **Response Caching** | Optional LRU + TTL cache for GET requests |
| **CLI** | `nioto` command for scripting and interactive use |
| **94%+ Coverage** | Thoroughly tested with `pytest` and `respx` |

---

## Installation

### Base SDK

```bash
pip install nostradamus-ioto-sdk
```

### With CLI

```bash
pip install "nostradamus-ioto-sdk[cli]"
```

### Development (editable + all extras)

```bash
git clone https://github.com/nostradamus/nostradamus-ioto-sdk.git
cd nostradamus-ioto-sdk
pip install -e ".[dev,cli,docs]"
```

---

## Quick Start

### 1. Authentication

The SDK supports two authentication methods. Choose one:

**API Key** (recommended for scripts and services):

```python
from nostradamus_ioto_sdk import NostradamusClient

client = NostradamusClient(api_key="your-api-key")
```

**OAuth2** (username/password):

```python
client = NostradamusClient(
    username="your-username",
    password="your-password",
)
```

You can also load credentials from environment variables — see [Configuration](#configuration).

### 2. List Projects

```python
projects = client.projects.list()

for project in projects:
    print(f"{project.project_name} ({project.project_id})")
```

### 3. Create a Project

```python
project = client.projects.create(
    name="Weather Station Network",
    description="Distributed temperature and humidity sensors",
    tags=["weather", "sensors"],
)

print(f"Created: {project.project_id}")
```

### 4. Create a Collection

```python
collection = client.collections.create(
    project_id=project.project_id,
    name="Temperature Readings",
    description="Hourly sensor readings",
    collection_schema={
        "sensor_id": "string",
        "temperature": "float",
        "humidity": "float",
    },
)
```

### 5. Send Data

```python
client.data.send(
    project_id=project.project_id,
    collection_id=collection.collection_id,
    data={
        "sensor_id": "ws-001",
        "temperature": 22.5,
        "humidity": 45.2,
        "timestamp": "2024-06-15T12:00:00Z",
    },
)
```

### 6. Query Data

```python
response = client.data.get(
    project_id=project.project_id,
    collection_id=collection.collection_id,
    filters=[
        {"attribute": "sensor_id", "operator": "eq", "value": "ws-001"},
    ],
    limit=100,
)

for record in response.data:
    print(f"{record['timestamp']}: {record['temperature']}°C")
```

### 7. Async Usage

Every sync method has an async counterpart prefixed with `a`:

```python
import asyncio
from nostradamus_ioto_sdk import AsyncNostradamusClient

async def main():
    async with AsyncNostradamusClient(api_key="your-api-key") as client:
        projects = await client.projects.alist()
        for project in projects:
            print(project.project_name)

asyncio.run(main())
```

---

## Configuration

### Environment Variables

Set these before initializing the client, or use a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `NOSTRADAMUS_API_KEY` | API key for authentication | — |
| `NOSTRADAMUS_USERNAME` | OAuth2 username | — |
| `NOSTRADAMUS_PASSWORD` | OAuth2 password | — |
| `NOSTRADAMUS_BASE_URL` | API base URL | `https://nostradamus-ioto.issel.ee.auth.gr` |
| `NOSTRADAMUS_TIMEOUT` | Request timeout (seconds) | `30.0` |
| `NOSTRADAMUS_MAX_RETRIES` | Max retry attempts | `3` |
| `NOSTRADAMUS_BACKOFF_FACTOR` | Exponential backoff multiplier | `0.5` |
| `NOSTRADAMUS_ENABLE_CACHE` | Enable response caching | `false` |
| `NOSTRADAMUS_CACHE_TTL` | Cache TTL (seconds) | `60` |
| `NOSTRADAMUS_RATE_LIMIT_RPS` | Rate limit (req/s, `0` = disabled) | `0` |
| `NOSTRADAMUS_LOG_LEVEL` | Logging level | `INFO` |
| `NOSTRADAMUS_VERIFY_SSL` | Verify SSL certificates | `true` |

### Programmatic Configuration

```python
from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.config import ClientConfig, RetryConfig

config = ClientConfig(
    api_key="your-api-key",
    base_url="https://custom-api.example.com",
    timeout=60.0,
    max_retries=5,
    retry_config=RetryConfig(backoff_factor=1.0),
    enable_cache=True,
    cache_ttl=120,
    rate_limit_rps=10.0,
)

client = NostradamusClient(config=config)
```

Or load from environment:

```python
config = ClientConfig.from_env()
client = NostradamusClient(config=config)
```

---

## API Reference

The SDK exposes these resource namespaces on the client:

| Resource | Access | Description |
|----------|--------|-------------|
| **Organizations** | `client.organizations` | Get/update organization info |
| **Projects** | `client.projects` | CRUD operations for projects |
| **Project Keys** | `client.project_keys` | Manage API keys (read/write/master) |
| **Collections** | `client.collections` | CRUD operations for data collections |
| **Data** | `client.data` | Send, query, delete records |
| **Statistics** | `client.data.stats(...)` | Aggregations (avg, max, min, sum, count, distinct) |
| **Health** | `client.health` | API health and readiness checks |

### Common Operations

```python
# Projects
projects = client.projects.list()
project = client.projects.get(project_id="...")
project = client.projects.create(name="...", description="...")
project = client.projects.update(project_id="...", name="new name")
client.projects.delete(project_id="...")

# Collections
collections = client.collections.list(project_id="...")
collection = client.collections.create(project_id="...", name="...", collection_schema={...})

# Data
client.data.send(project_id="...", collection_id="...", data={...})
response = client.data.get(project_id="...", collection_id="...", filters=[...], limit=50)
client.data.delete(project_id="...", collection_id="...", filters=[...])

# Statistics
stats = client.data.stats(
    project_id="...",
    collection_id="...",
    attribute="temperature",
    operation="avg",  # avg | max | min | sum | count | distinct
)
```

---

## Error Handling

All SDK errors inherit from `NostradamusError`. Catch specific exceptions for precise control:

```python
from nostradamus_ioto_sdk import (
    NostradamusError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    APIConnectionError,
    RequestTimeoutError,
)

try:
    project = client.projects.get(project_id="nonexistent-id")
except AuthenticationError:
    print("Check your API key or credentials")
except ResourceNotFoundError:
    print("Project does not exist")
except ValidationError as e:
    print(f"Invalid request: {e.errors}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except RequestTimeoutError:
    print("Request timed out — try increasing NOSTRADAMUS_TIMEOUT")
except APIConnectionError:
    print("Cannot reach the API server")
except NostradamusError as e:
    print(f"SDK error: {e.message}")
```

### Exception Hierarchy

```
NostradamusError
├── ConfigurationError
├── AuthenticationError          (401, 403)
└── APIError
    ├── ValidationError          (422)
    ├── ResourceNotFoundError    (404)
    ├── RateLimitError           (429)
    ├── RequestTimeoutError
    └── APIConnectionError
```

---

## CLI

The `nioto` CLI is installed with the `[cli]` extra.

### Setup

```bash
export NOSTRADAMUS_API_KEY="your-api-key"
```

### Commands

```bash
# Projects
nioto projects list
nioto projects create --name "My Project" --description "IoT sensors"
nioto projects get <project-id>

# Collections
nioto collections list --project <project-id>
nioto collections create --project <project-id> --name "Readings" --schema '{"temp": "float"}'

# Data
nioto data send --project <project-id> --collection <collection-id> --data '[{"temp": 22.5}]'
nioto data get --project <project-id> --collection <collection-id> --limit 10

# API Keys
nioto keys list --project <project-id>
nioto keys create --project <project-id> --name "CI Key" --type write

# Organization
nioto org get
```

### Output Formats

```bash
nioto projects list --format json     # JSON output
nioto projects list --format table    # Table (default)
nioto projects list --format compact  # Minimal
```

---

## Examples

The [`examples/`](./examples/) directory contains runnable scripts:

| Example | Description |
|---------|-------------|
| `basic_usage.py` | Core SDK operations |
| `async_usage.py` | Async/await patterns |
| `data_ingestion.py` | Batch data ingestion |
| `ioto_api_demo.py` | Full API feature walkthrough |
| `soil_monitoring_example.py` | Agriculture sensor monitoring |
| `agriculture/` | Precision farming, greenhouse, soil monitoring |
| `smart_city/` | Urban IoT deployments |
| `smart_energy/` | Energy grid monitoring |
| `smart_transportation/` | Fleet and transit tracking |
| `cyber_physical/` | Robotics and cyber-physical systems |

Run any example:

```bash
cd examples
python basic_usage.py
```

---

## Development

### Prerequisites

- Python 3.9+
- `make` (optional, for convenience commands)

### Setup

```bash
git clone https://github.com/nostradamus/nostradamus-ioto-sdk.git
cd nostradamus-ioto-sdk
python -m venv .venv
source .venv/bin/activate
make install-dev
```

### Commands

| Command | Description |
|---------|-------------|
| `make test` | Run tests with coverage |
| `make test-unit` | Unit tests only |
| `make lint` | black + isort + ruff + mypy |
| `make format` | Auto-format code |
| `make typecheck` | mypy only |
| `make docs` | Serve documentation locally |
| `make build` | Build distribution packages |
| `make clean` | Remove build artifacts |
| `make ci` | Full CI pipeline (lint + typecheck + test) |

### Project Structure

```
nostradamus-ioto-sdk/
├── nostradamus_ioto_sdk/       # SDK package
│   ├── client.py               # Sync client
│   ├── async_client.py         # Async client
│   ├── auth.py                 # OAuth2 + API Key handlers
│   ├── config.py               # ClientConfig, RetryConfig
│   ├── exceptions.py           # Exception hierarchy
│   ├── _base_client.py         # Retry logic, response handling
│   ├── _http.py                # Cache, rate limiter, retry utils
│   ├── _logging.py             # SDKLogger with credential masking
│   ├── models/                 # Pydantic request/response models
│   ├── resources/              # API resource classes
│   ├── utils/                  # Pagination, caching, batch helpers
│   └── cli/                    # Click CLI (nioto command)
├── tests/                      # Unit and integration tests
├── examples/                   # Runnable examples
├── docs/                       # MkDocs documentation
└── scripts/                    # Dev utilities
```

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before submitting a pull request.

### Quick Checklist

1. Fork and create a feature branch
2. Write tests for new functionality
3. Run `make ci` to verify lint, types, and tests pass
4. Submit a PR with a clear description

---

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

---

## Support

- **Bug Reports**: [GitHub Issues](https://github.com/nostradamus/nostradamus-ioto-sdk/issues)
- **Documentation**: [Read the Docs](https://nostradamus-ioto-sdk.readthedocs.io)
- **Changelog**: [CHANGELOG.md](./CHANGELOG.md)
