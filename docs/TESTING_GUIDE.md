# Nostradamus IoTO SDK - Testing Guide

This guide helps you test the SDK with your actual IoTO credentials.

## Prerequisites

### 1. Get Your Credentials

You need the following from the Nostradamus IoTO platform:

- **Project ID**: Your project identifier
- **Master Key**: For creating/deleting collections
- **Write Key**: For sending data to collections
- **Read Key**: For querying data from collections

### 2. Set Environment Variables

```bash
export NOSTRADAMUS_PROJECT_ID="your-project-id-here"
export NOSTRADAMUS_MASTER_KEY="your-master-key-here"
export NOSTRADAMUS_WRITE_KEY="your-write-key-here"
export NOSTRADAMUS_READ_KEY="your-read-key-here"
```

**Tip**: Add these to your `~/.bashrc` or `~/.zshrc` for persistence.

### 3. Install the SDK

```bash
# From the project directory
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

---

## Quick Test (Recommended First)

The quickest way to verify everything works:

```bash
python test_sdk_quick.py
```

This script will:
1. ✅ Create a test collection
2. ✅ Send 3 sample data records
3. ✅ Query the data (all data + filtered)
4. ✅ Calculate statistics
5. ✅ Delete the test collection

**Expected Output**:
```
🧪 Nostradamus IoTO SDK - Quick Test
============================================================

[1/4] Creating test collection...
✅ Collection created: sdk_test_20260201_123456
   ID: abc123...

[2/4] Sending test data...
✅ Sent 3 data records

[3/4] Querying data...
✅ Retrieved 3 total records
✅ Retrieved 1 filtered records (SENSOR_001)
✅ Average temperature: 25.53

[4/4] Deleting test collection...
✅ Collection deleted

============================================================
✨ All tests passed successfully!
============================================================
```

---

## Comprehensive Soil Monitoring Example

A complete real-world example matching the official API demonstration:

```bash
python examples/soil_monitoring_example.py
```

This demonstrates:
- **Collection Creation** with schema definition
- **Data Generation** (3 sensors × 24 readings = 72 records)
- **Batch Data Sending** (efficient bulk operations)
- **Complex Querying**:
  - Get all data
  - Limit results
  - Order by field
  - Filter by sensor ID
  - Filter by value (e.g., moisture > 45%)
  - Multi-condition filters (moisture < 35 AND battery < 80)
- **Statistics**:
  - Average soil moisture
  - Maximum temperature
  - Minimum battery level for specific sensor
  - Distinct sensor keys
- **Data Deletion** by key and time range
- **Collection Cleanup**

**Features Tested**: All SDK capabilities in a realistic IoT scenario

---

## Other Examples

### Basic Usage
```bash
python examples/basic_usage.py
```
Demonstrates fundamental operations with clear step-by-step execution.

### Async Usage
```bash
python examples/async_usage.py
```
Shows concurrent operations using `AsyncNostradamusClient` for high-performance scenarios.

### Data Ingestion
```bash
python examples/data_ingestion.py
```
IoT-focused example with continuous data ingestion patterns.

---

## Manual Testing

### Test SDK Import

```python
python -c "from nostradamus_ioto_sdk import NostradamusClient; print('✅ SDK import successful')"
```

### Test Client Creation

```python
from nostradamus_ioto_sdk import NostradamusClient

# With API key
client = NostradamusClient(api_key="your-key")
print("✅ Client created")
```

### Test Basic Operations

```python
from nostradamus_ioto_sdk import NostradamusClient
import os

client = NostradamusClient(api_key=os.getenv("NOSTRADAMUS_MASTER_KEY"))

# List projects
projects = client.projects.list()
print(f"✅ Found {len(projects)} projects")

# Get organization
org = client.organizations.get()
print(f"✅ Organization: {org.organization_name}")
```

---

## Troubleshooting

### Issue: "Missing required environment variables"

**Solution**: Set all four environment variables:
```bash
export NOSTRADAMUS_PROJECT_ID="..."
export NOSTRADAMUS_MASTER_KEY="..."
export NOSTRADAMUS_WRITE_KEY="..."
export NOSTRADAMUS_READ_KEY="..."
```

Verify they're set:
```bash
env | grep NOSTRADAMUS
```

### Issue: "401 Authentication Error"

**Possible Causes**:
1. Invalid API key
2. Wrong key type (e.g., using read key for write operation)
3. Expired key

**Solution**:
- Verify your keys are correct
- Check you're using the right key for each operation:
  - Master key: Create/delete collections
  - Write key: Send data
  - Read key: Query data

### Issue: "404 Resource Not Found"

**Possible Causes**:
1. Wrong project ID
2. Collection doesn't exist
3. Collection was already deleted

**Solution**: Verify your project ID and collection ID are correct.

### Issue: "422 Validation Error"

**Possible Causes**:
1. Missing required fields
2. Invalid data format
3. Schema mismatch

**Solution**: Check the error details for specific field issues.

### Issue: Import errors

**Error**: `ModuleNotFoundError: No module named 'nostradamus_ioto_sdk'`

**Solution**:
```bash
# Make sure you're in the project directory
cd /path/to/nostradamus-ioto-sdk

# Install in editable mode
pip install -e .

# Verify installation
pip list | grep nostradamus
```

---

## Test Coverage

### Unit Tests

Run the unit tests:
```bash
# All unit tests
pytest tests/unit/ -v

# Specific module
pytest tests/unit/test_http.py -v

# With coverage
pytest tests/unit/ --cov=nostradamus_ioto_sdk --cov-report=html
```

**Current Coverage**:
- HTTP utilities: 99% ✅
- Models: 100% ✅
- Authentication: 44%
- Overall: 44%

### Integration Tests

**Note**: Integration tests use mocked API responses (no real credentials needed):
```bash
pytest tests/integration/ -v
```

---

## API Endpoint Coverage

All 22 API endpoints are implemented and testable:

### Organizations
- ✅ GET `/api/v1/organization` - Get organization info
- ✅ PUT `/api/v1/organization` - Update organization

### Projects
- ✅ GET `/api/v1/projects` - List projects
- ✅ GET `/api/v1/projects/{id}` - Get project
- ✅ POST `/api/v1/projects` - Create project
- ✅ PUT `/api/v1/projects/{id}` - Update project
- ✅ DELETE `/api/v1/projects/{id}` - Delete project

### Collections
- ✅ GET `/api/v1/projects/{pid}/collections` - List collections
- ✅ GET `/api/v1/projects/{pid}/collections/{cid}` - Get collection
- ✅ POST `/api/v1/projects/{pid}/collections` - Create collection
- ✅ PUT `/api/v1/projects/{pid}/collections/{cid}` - Update collection
- ✅ DELETE `/api/v1/projects/{pid}/collections/{cid}` - Delete collection

### Project Keys
- ✅ GET `/api/v1/projects/{pid}/keys` - List keys
- ✅ GET `/api/v1/projects/{pid}/keys/{kid}` - Get key
- ✅ POST `/api/v1/projects/{pid}/keys` - Create key
- ✅ POST `/api/v1/projects/{pid}/keys/{kid}/regenerate` - Regenerate key
- ✅ DELETE `/api/v1/projects/{pid}/keys/{kid}` - Delete key

### Data Operations
- ✅ POST `/api/v1/projects/{pid}/collections/{cid}/send_data` - Send data
- ✅ GET `/api/v1/projects/{pid}/collections/{cid}/get_data` - Query data
- ✅ GET `/api/v1/projects/{pid}/collections/{cid}/statistics` - Get statistics
- ✅ DELETE `/api/v1/projects/{pid}/collections/{cid}/delete_data` - Delete data

---

## Performance Testing

### Test Batch Operations

```python
# Generate large dataset
import random
from datetime import datetime, timedelta

data = []
for i in range(1000):  # 1000 records
    data.append({
        "key": f"SENSOR_{i % 10:03d}",
        "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
        "value": random.uniform(20, 30)
    })

# Send in batch (efficient)
client.data.send(project_id, collection_id, data)
```

### Test Concurrent Operations (Async)

```python
import asyncio
from nostradamus_ioto_sdk import AsyncNostradamusClient

async def test_concurrent():
    async with AsyncNostradamusClient(api_key=key) as client:
        # Run 10 queries concurrently
        tasks = [
            client.data.aget(project_id, collection_id, limit=100)
            for _ in range(10)
        ]
        results = await asyncio.gather(*tasks)
        print(f"Completed {len(results)} concurrent queries")

asyncio.run(test_concurrent())
```

---

## Next Steps

1. ✅ Run `test_sdk_quick.py` to verify basic functionality
2. ✅ Run `examples/soil_monitoring_example.py` for comprehensive test
3. ✅ Try the async example if you need high performance
4. ✅ Read the API documentation for advanced usage
5. ✅ Report any issues on GitHub

---

## Support

- **Documentation**: See `README.md` and `SDK_READY.md`
- **Examples**: Check `examples/` directory
- **Issues**: Report on GitHub (if applicable)
- **API Reference**: https://nostradamus-ioto.issel.ee.auth.gr/docs

---

*Last Updated: 2026-02-01*
