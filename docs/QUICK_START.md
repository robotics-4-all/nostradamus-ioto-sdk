# Quick Start Guide - Nostradamus IoTO SDK

## 🎉 SDK is Ready for Testing!

The Nostradamus IoTO Python SDK is now functional and ready to interact with the IoTO API.

## Installation

The SDK is installed in development mode:

```bash
# Already done - SDK is installed in editable mode
source .venv/bin/activate  # Activate virtual environment
```

## Authentication

You can authenticate using either an API key or OAuth2 credentials.

### Option 1: API Key

```bash
export NOSTRADAMUS_API_KEY="your-api-key-here"
```

```python
from nostradamus_ioto_sdk import NostradamusClient

client = NostradamusClient(api_key="your-api-key")
```

### Option 2: OAuth2 (Username/Password)

```bash
export NOSTRADAMUS_USERNAME="your-username"
export NOSTRADAMUS_PASSWORD="your-password"
```

```python
from nostradamus_ioto_sdk import NostradamusClient

client = NostradamusClient(
    username="your-username",
    password="your-password"
)
```

## Running the Test Script

We've created a test script for you to verify the SDK works with your IoTO API:

```bash
# Set your credentials first:
export NOSTRADAMUS_API_KEY="your-api-key"
# OR
export NOSTRADAMUS_USERNAME="your-username"
export NOSTRADAMUS_PASSWORD="your-password"

# Run the test script:
.venv/bin/python test_client.py
```

The test script will:
1. ✅ Connect to the IoTO API
2. ✅ Get your organization information
3. ✅ List your projects
4. ✅ Create and delete a test project
5. ✅ List collections (if you have projects)

## Basic Usage Examples

### 1. Get Organization Info

```python
from nostradamus_ioto_sdk import NostradamusClient

client = NostradamusClient(api_key="your-api-key")

# Get organization
org = client.organizations.get()
print(f"Organization: {org.organization_name}")
print(f"ID: {org.organization_id}")
```

### 2. Manage Projects

```python
# List all projects
projects = client.projects.list()
for project in projects:
    print(f"- {project.project_name}")

# Create a new project
new_project = client.projects.create(
    name="My IoT Project",
    description="Collecting sensor data",
    tags=["sensors", "iot"]
)

# Get project by ID
project = client.projects.get(new_project.project_id)

# Update project
updated = client.projects.update(
    project_id=new_project.project_id,
    description="Updated description",
    tags=["sensors", "iot", "updated"]
)

# Delete project
client.projects.delete(new_project.project_id)
```

### 3. Manage Collections

```python
# Create a collection
collection = client.collections.create(
    project_id="your-project-id",
    name="Temperature Sensors",
    description="Temperature readings from sensors",
    collection_schema={
        "type": "object",
        "properties": {
            "sensor_id": {"type": "string"},
            "temperature": {"type": "number"},
            "timestamp": {"type": "string"}
        }
    },
    tags=["temperature", "sensors"]
)

# List collections
collections = client.collections.list(project_id="your-project-id")

# Get collection
collection = client.collections.get(
    project_id="your-project-id",
    collection_id="your-collection-id"
)
```

### 4. Send and Query Data

```python
from nostradamus_ioto_sdk import StatOperation

# Send data (single record)
client.data.send(
    project_id="your-project-id",
    collection_id="your-collection-id",
    data={
        "sensor_id": "temp_001",
        "temperature": 22.5,
        "humidity": 45.2,
        "timestamp": "2024-02-01T12:00:00Z"
    }
)

# Send data (batch)
client.data.send(
    project_id="your-project-id",
    collection_id="your-collection-id",
    data=[
        {"sensor_id": "temp_001", "temperature": 22.5, "timestamp": "2024-02-01T12:00:00Z"},
        {"sensor_id": "temp_002", "temperature": 23.1, "timestamp": "2024-02-01T12:01:00Z"},
        {"sensor_id": "temp_003", "temperature": 21.8, "timestamp": "2024-02-01T12:02:00Z"},
    ]
)

# Query data
data = client.data.get(
    project_id="your-project-id",
    collection_id="your-collection-id",
    filters={"sensor_id": "temp_001"},
    limit=100,
    order_by="timestamp"
)

# Get statistics
stats = client.data.statistics(
    project_id="your-project-id",
    collection_id="your-collection-id",
    operation=StatOperation.AVG,
    attribute="temperature",
    group_by="sensor_id"
)
```

### 5. Manage API Keys

```python
from nostradamus_ioto_sdk import KeyType

# Create API key
key = client.project_keys.create(
    project_id="your-project-id",
    key_type=KeyType.READ
)
print(f"New API key: {key.api_key}")

# List all keys
keys = client.project_keys.list(project_id="your-project-id")

# Regenerate key
new_key = client.project_keys.regenerate(
    project_id="your-project-id",
    api_key="old-key"
)

# Delete key
client.project_keys.delete(
    project_id="your-project-id",
    api_key="key-to-delete"
)
```

### 6. Context Manager

```python
# Automatic cleanup with context manager
with NostradamusClient(api_key="your-api-key") as client:
    projects = client.projects.list()
    # Client automatically closes when done
```

## Available Resources

The SDK provides access to all IoTO API endpoints:

- **Organizations** - `client.organizations`
  - `get()` - Get organization info
  - `update()` - Update organization

- **Projects** - `client.projects`
  - `list()` - List all projects
  - `get(project_id)` - Get project by ID
  - `create(name, ...)` - Create project
  - `update(project_id, ...)` - Update project
  - `delete(project_id)` - Delete project

- **Project Keys** - `client.project_keys`
  - `list(project_id)` - List API keys
  - `create(project_id, key_type)` - Create API key
  - `get(project_id, api_key)` - Get key details
  - `regenerate(project_id, api_key)` - Regenerate key
  - `delete(project_id, api_key)` - Delete key

- **Collections** - `client.collections`
  - `list(project_id)` - List collections
  - `get(project_id, collection_id)` - Get collection
  - `create(project_id, ...)` - Create collection
  - `update(project_id, collection_id, ...)` - Update collection
  - `delete(project_id, collection_id)` - Delete collection

- **Data** - `client.data`
  - `send(project_id, collection_id, data)` - Send data
  - `get(project_id, collection_id, ...)` - Query data
  - `statistics(project_id, collection_id, ...)` - Get aggregations
  - `delete(project_id, collection_id, ...)` - Delete data

## Error Handling

```python
from nostradamus_ioto_sdk import (
    NostradamusClient,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    APIError
)

client = NostradamusClient(api_key="your-key")

try:
    project = client.projects.get("invalid-id")
except AuthenticationError:
    print("Authentication failed")
except ResourceNotFoundError:
    print("Project not found")
except ValidationError as e:
    print(f"Validation error: {e.errors}")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except APIError as e:
    print(f"API error: {e}")
```

## Next Steps

1. **Test with your IoTO credentials** - Run the test script
2. **Explore the API** - Try different operations
3. **Build your application** - Integrate the SDK into your project

## Need Help?

- Check the full documentation: `docs/`
- See example scripts: `examples/` (to be created)
- Review the API reference: Generated from docstrings

---

**The SDK is ready!** 🎉

You can now interact with the Nostradamus IoTO API using this professional Python SDK.
