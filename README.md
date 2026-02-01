# Nostradamus IoTO Python SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
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
- ✅ **Thoroughly Tested** - >85% code coverage

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
    print(f"Project: {project.name}")

# Create a new project
new_project = client.projects.create(
    name="My IoT Project",
    description="Collecting sensor data",
    tags=["sensors", "temperature"]
)

# Create a collection in the project
collection = client.collections.create(
    project_id=new_project.id,
    name="Temperature Sensors",
    description="Data from temperature sensors"
)

# Send data to the collection
client.data.send(
    project_id=new_project.id,
    collection_id=collection.id,
    data={
        "sensor_id": "temp_001",
        "temperature": 22.5,
        "humidity": 45.2,
        "timestamp": "2024-02-01T12:00:00Z"
    }
)

# Query data
data = client.data.get(
    project_id=new_project.id,
    collection_id=collection.id,
    filters={"sensor_id": "temp_001"},
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
            print(f"Project: {project.name}")

import asyncio
asyncio.run(main())
```

### Using the CLI

```bash
# Configure credentials
export NOSTRADAMUS_API_KEY="your-api-key"

# List projects
nostradamus projects list

# Create a project
nostradamus projects create "My Project" --description "IoT sensors"

# List collections
nostradamus collections list <project-id>

# Send data
nostradamus data send <project-id> <collection-id> --file data.json
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

- Python 3.8 or higher
- `httpx` >= 0.25.0
- `pydantic` >= 2.0.0

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
- `data_querying.py` - Advanced querying with filters
- `statistics.py` - Analytics and aggregations
- `error_handling.py` - Graceful error handling

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Support

- GitHub Issues: [Report a bug](https://github.com/nostradamus/nostradamus-ioto-sdk/issues)
- Documentation: [Read the docs](https://nostradamus-ioto-sdk.readthedocs.io)

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.
