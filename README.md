# Nostradamus IoTO Python SDK

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Professional Python SDK for the Nostradamus IoT Observatory API - a comprehensive client library for managing IoT data collection, projects, and analytics.

## Features

- ✅ **Sync and Async Support** - Use synchronous or asynchronous client based on your needs
- ✅ **Type Hints & Validation** - Full type coverage with Pydantic models
- ✅ **Automatic Retry & Rate Limiting** - Built-in resilience for production use
- ✅ **Dual Authentication** - Support for both OAuth2 and API Key authentication
- ✅ **Comprehensive Error Handling** - Clear, actionable error messages
- ✅ **CLI Tool Included** - Command-line interface for common operations
- ✅ **Well Documented** - Extensive documentation with examples
- ✅ **Thoroughly Tested** - >94% code coverage

## Installation

```bash
pip install nostradamus-ioto-sdk
```

For CLI support:
```bash
pip install nostradamus-ioto-sdk[cli]
```

For development:
```bash
pip install nostradamus-ioto-sdk[dev]
```

## Quick Start

### Using API Key

```python
from nostradamus_ioto_sdk import NostradamusClient

# Initialize client with API key
client = NostradamusClient(api_key="your-api-key-here")

# List all projects
projects = client.projects.list()
for project in projects:
    print(f"Project: {project.project_name}")

# Create a new project
new_project = client.projects.create(
    name="My IoT Project",
    description="Collecting sensor data",
    tags=["sensors", "temperature"]
)

# Create a collection in the project
collection = client.collections.create(
    project_id=new_project.project_id,
    name="Temperature Sensors",
    description="Data from temperature sensors",
    collection_schema={"temperature": "float", "humidity": "float", "sensor_id": "string"}
)

# Send data to the collection
client.data.send(
    project_id=new_project.project_id,
    collection_id=collection.collection_id,
    data={
        "sensor_id": "temp_001",
        "temperature": 22.5,
        "humidity": 45.2,
        "timestamp": "2024-02-01T12:00:00Z"
    }
)

# Query data
data = client.data.get(
    project_id=new_project.project_id,
    collection_id=collection.collection_id,
    filters=[{"attribute": "sensor_id", "operator": "eq", "value": "temp_001"}],
    limit=100
)
```

### Using OAuth2 Credentials

```python
client = NostradamusClient(
    username="your-username",
    password="your-password"
)

# Same API as above
projects = client.projects.list()
```

### Async Usage

```python
from nostradamus_ioto_sdk import AsyncNostradamusClient

async def main():
    async with AsyncNostradamusClient(api_key="your-api-key") as client:
        projects = await client.projects.alist()
        for project in projects:
            print(f"Project: {project.project_name}")

import asyncio
asyncio.run(main())
```

### Using the CLI

```bash
# Configure credentials
export NOSTRADAMUS_API_KEY="your-api-key"

# List projects
nioto projects list

# Create a project
nioto projects create --name "My Project" --description "IoT sensors"

# List collections
nioto collections list --project <project-id>

# Send data
nioto data send --project <project-id> --collection <collection-id> \
  --data '[{"temperature": 22.5}]'
```

## API Coverage

The SDK covers all Nostradamus IoTO API endpoints:

- **Authentication** - OAuth2 token management
- **Organizations** - Get and update organization info
- **Projects** - Full CRUD operations for projects
- **Project Keys** - Manage API keys (read/write/master)
- **Collections** - Full CRUD operations for data collections
- **Data Operations** - Send, query, delete data with filtering and aggregations
- **Statistics** - Get analytics with aggregations (avg, max, min, sum, count, distinct)

## Documentation

- [Full Documentation](https://nostradamus-ioto-sdk.readthedocs.io)
- [API Reference](https://nostradamus-ioto-sdk.readthedocs.io/api/)
- [Examples](./examples/)
- [Contributing Guide](./CONTRIBUTING.md)

## Requirements

- Python 3.9 or higher
- `httpx` >= 0.25.0
- `pydantic` >= 2.0.0
- `python-dateutil` >= 2.8.0
- `typing-extensions` >= 4.5.0

## Configuration

The SDK can be configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `NOSTRADAMUS_API_KEY` | API key for authentication | — |
| `NOSTRADAMUS_BASE_URL` | API base URL | `https://nostradamus-ioto.issel.ee.auth.gr` |
| `NOSTRADAMUS_TIMEOUT` | Request timeout in seconds | `30.0` |
| `NOSTRADAMUS_MAX_RETRIES` | Maximum retry attempts | `3` |
| `NOSTRADAMUS_BACKOFF_FACTOR` | Exponential backoff factor | `0.5` |
| `NOSTRADAMUS_ENABLE_CACHE` | Enable response caching (`true`/`false`) | `false` |
| `NOSTRADAMUS_CACHE_TTL` | Cache TTL in seconds | `60` |
| `NOSTRADAMUS_RATE_LIMIT_RPS` | Rate limit (requests/second, `0` = disabled) | `0.0` |
| `NOSTRADAMUS_LOG_LEVEL` | Logging level | `INFO` |
| `NOSTRADAMUS_VERIFY_SSL` | Verify SSL certificates (`true`/`false`) | `true` |

Use `ClientConfig.from_env()` to load configuration from environment:

```python
from nostradamus_ioto_sdk.config import ClientConfig

config = ClientConfig.from_env()
```

## Development

```bash
# Clone the repository
git clone https://github.com/nostradamus/nostradamus-ioto-sdk.git
cd nostradamus-ioto-sdk

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
make install-dev

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Type checking
make typecheck
```

## Examples

Check the [examples/](./examples/) directory for more comprehensive examples:

- `basic_usage.py` - Basic SDK usage
- `async_usage.py` - Async/await patterns
- `data_ingestion.py` - Batch data ingestion
- `ioto_api_demo.py` - Demonstration of all core API features
- `soil_monitoring_example.py` - Domain-specific example for agriculture
- `agriculture/` - Agriculture domain examples (precision farming, greenhouse, soil monitoring)
- `smart_city/` - Smart city IoT examples
- `smart_energy/` - Smart energy grid examples
- `smart_transportation/` - Smart transportation examples
- `cyber_physical/` - Cyber-physical systems with robots

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Support

- GitHub Issues: [Report a bug](https://github.com/nostradamus/nostradamus-ioto-sdk/issues)
- Documentation: [Read the docs](https://nostradamus-ioto-sdk.readthedocs.io)

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.
