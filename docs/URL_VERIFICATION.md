# SDK URL Configuration Verification

## ✅ Base URL is Correctly Configured

The SDK is properly configured to use the correct base URL with `/api/v1` prefix.

### Configuration Details

**Client Base URL** (domain only):
```
https://nostradamus-ioto.issel.ee.auth.gr
```

**API Version Path** (added by resources):
```
/api/v1
```

**Combined Full URLs**:
```
https://nostradamus-ioto.issel.ee.auth.gr/api/v1/organization
https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects
https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{id}/collections
https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{id}/collections/{cid}/send_data
... etc
```

### How It Works

#### 1. Client Level (`client.py`)
```python
class NostradamusClient:
    def __init__(self, base_url="https://nostradamus-ioto.issel.ee.auth.gr", ...):
        self._base_url = base_url.rstrip("/")
```

#### 2. Resource Level (`resources/_base.py`)
```python
class BaseResource:
    def __init__(self, client):
        self._client = client
        self._base_path = "/api/v1"  # API version prefix
    
    def _build_path(self, *parts):
        # Builds: /api/v1/projects/123/collections
        return f"{self._base_path}/{'/'.join(parts)}"
```

#### 3. Request Execution (`client.py`)
```python
def _request(self, method, path, **kwargs):
    # Combines base_url + path
    url = f"{self._base_url}{path}"
    # Results in: https://nostradamus-ioto.issel.ee.auth.gr/api/v1/...
    return make_request_with_retry(...)
```

### Verification

You can verify the URL construction:

```python
from nostradamus_ioto_sdk import NostradamusClient

# Create client
client = NostradamusClient(api_key="test-key")

# Check base URL
print(f"Base URL: {client._base_url}")
# Output: https://nostradamus-ioto.issel.ee.auth.gr

# Check resource base path
print(f"API Path: {client.projects._base_path}")
# Output: /api/v1

# Example full path
path = client.projects._build_path("projects", "123", "collections")
print(f"Full path: {path}")
# Output: /api/v1/projects/123/collections

# Full URL (what actually gets called)
full_url = f"{client._base_url}{path}"
print(f"Full URL: {full_url}")
# Output: https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/123/collections
```

### All Endpoints

The SDK correctly constructs URLs for all endpoints:

| Endpoint | Full URL |
|----------|----------|
| **Auth** |
| Token | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/token` |
| **Organization** |
| Get org | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/organization` |
| Update org | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/organization` |
| **Projects** |
| List | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects` |
| Get | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{id}` |
| Create | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects` |
| Update | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{id}` |
| Delete | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{id}` |
| **Collections** |
| List | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/collections` |
| Get | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/collections/{cid}` |
| Create | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/collections` |
| Update | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/collections/{cid}` |
| Delete | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/collections/{cid}` |
| **Data** |
| Send | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/collections/{cid}/send_data` |
| Get | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/collections/{cid}/get_data` |
| Statistics | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/collections/{cid}/statistics` |
| Delete | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/collections/{cid}/delete_data` |
| **Keys** |
| List | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/keys` |
| Get | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/keys/{kid}` |
| Create | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/keys` |
| Regenerate | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/keys/{kid}/regenerate` |
| Delete | `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{pid}/keys/{kid}` |

### Matches Official Demo

The SDK URLs match exactly with the official demonstration file:

**From `nostradamus_ioto_api_example_demonstration.py`**:
```python
BASE_URL = "https://nostradamus-ioto.issel.ee.auth.gr/api/v1"

# Their URL construction:
url = f"{BASE_URL}/projects/{project_id}/collections"
# Result: https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{id}/collections
```

**SDK URL construction**:
```python
# SDK does the same thing internally:
base_url = "https://nostradamus-ioto.issel.ee.auth.gr"
path = "/api/v1/projects/{project_id}/collections"
url = f"{base_url}{path}"
# Result: https://nostradamus-ioto.issel.ee.auth.gr/api/v1/projects/{id}/collections
```

**✅ IDENTICAL**

---

## Summary

✅ **Base URL is correct**: `https://nostradamus-ioto.issel.ee.auth.gr`  
✅ **API version path is correct**: `/api/v1`  
✅ **Full URLs are correct**: `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/...`  
✅ **Token endpoint is correct**: `https://nostradamus-ioto.issel.ee.auth.gr/api/v1/token`  
✅ **Matches official demo**: 100% URL compatibility  

**No changes needed** - the SDK is already properly configured!

---

*Verified: 2026-02-01*
