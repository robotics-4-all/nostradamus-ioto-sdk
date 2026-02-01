# Nostradamus IoTO SDK Examples

This directory contains example scripts demonstrating various features of the Nostradamus IoTO Python SDK.

## Prerequisites

1. **Install the SDK**:
   ```bash
   pip install nostradamus-ioto-sdk
   # Or from source:
   pip install -e .
   ```

2. **Set up authentication**:
   ```bash
   export NOSTRADAMUS_API_KEY="your-api-key-here"
   ```

## Examples

### 1. Soil Monitoring Example (`soil_monitoring_example.py`) ⭐ **RECOMMENDED**

**Complete workflow matching the official API demonstration**:
- Create collection with schema
- Generate and send soil sensor data (3 sensors × 24 readings)
- Query data with various filters:
  - Get all data
  - Limit results
  - Order by temperature
  - Filter by sensor ID
  - Filter by moisture level
  - Complex multi-condition filters
- Get statistics (avg, max, min, distinct)
- Delete specific data by key and time range
- Clean up collection

**Environment Variables Required**:
```bash
export NOSTRADAMUS_PROJECT_ID="your-project-id"
export NOSTRADAMUS_MASTER_KEY="your-master-key"
export NOSTRADAMUS_WRITE_KEY="your-write-key"
export NOSTRADAMUS_READ_KEY="your-read-key"
```

**Run it**:
```bash
python examples/soil_monitoring_example.py
```

This example demonstrates **all major SDK features** in a realistic IoT scenario.

---

### 2. Basic Usage (`basic_usage.py`)

Demonstrates fundamental SDK operations:
- Getting organization information
- Listing, creating, updating, and deleting projects
- Managing collections
- Sending and querying data

**Run it**:
```bash
python examples/basic_usage.py
```

### 3. Async Usage (`async_usage.py`)

Shows how to use the async client for concurrent operations:
- Parallel API requests
- Creating multiple resources concurrently
- Efficient batch operations

**Run it**:
```bash
python examples/async_usage.py
```

### 4. Data Ingestion (`data_ingestion.py`)

IoT-focused example for sensor data ingestion:
- Simulating sensor readings
- Individual vs batch data sending
- Continuous data ingestion patterns
- Querying and analyzing data

**Run it**:
```bash
python examples/data_ingestion.py
```

## Tips

### Batch Operations

When sending multiple data points, use batch operations for better performance:

```python
# Instead of this:
for data_point in data_points:
    client.data.send(project_id, collection_id, data_point)

# Do this:
client.data.send(project_id, collection_id, data_points)
```

### Error Handling

Always handle potential errors:

```python
from nostradamus_ioto_sdk.exceptions import (
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
)

try:
    project = client.projects.get(project_id)
except ResourceNotFoundError:
    print("Project not found")
except AuthenticationError:
    print("Invalid credentials")
```

### Context Managers

Use context managers to ensure proper cleanup:

```python
with NostradamusClient(api_key=api_key) as client:
    # Your code here
    pass
# Client automatically closed
```

### Async Operations

For high-throughput scenarios, use the async client:

```python
import asyncio
from nostradamus_ioto_sdk import AsyncNostradamusClient

async def main():
    async with AsyncNostradamusClient(api_key=api_key) as client:
        # Concurrent operations
        results = await asyncio.gather(
            client.projects.alist(),
            client.organizations.aget(),
        )

asyncio.run(main())
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NOSTRADAMUS_API_KEY` | Your API key | Yes (if not using OAuth2) |
| `NOSTRADAMUS_USERNAME` | OAuth2 username | Yes (if not using API key) |
| `NOSTRADAMUS_PASSWORD` | OAuth2 password | Yes (if not using API key) |

## Need Help?

- Check the main [README.md](../README.md)
- Read the [documentation](https://nostradamus-ioto-sdk.readthedocs.io/)
- Open an issue on [GitHub](https://github.com/yourusername/nostradamus-ioto-sdk/issues)
