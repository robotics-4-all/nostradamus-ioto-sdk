# Improved Error Handling for Create Operations

## Changes Made

Added robust error handling to all `create()` methods to handle different API response formats and provide clear error messages.

### What Was Added

1. **Multiple ID field name checks**:
   - `collection_id`, `id`, `collectionId` for collections
   - `project_id`, `id`, `projectId` for projects  
   - `key_id`, `id`, `keyId` for keys

2. **Full response detection**:
   - If API returns complete object, use it directly
   - If API returns only ID, fetch full details

3. **Detailed error messages**:
   - Shows the actual API response when ID field is missing
   - Helps debug API response format issues

### Example Error Message

If the API response doesn't contain the expected ID field, you'll now see:

```
APIError: Create response missing collection ID. Response: {'message': 'Collection created', 'data': {'uuid': 'abc-123'}}
```

This shows exactly what the API returned, making it easy to identify the correct field name.

### Code Pattern

```python
def create(...) -> CollectionResponse:
    # Make create request
    response = self._client._request("POST", path, json=data)
    response_data = response.json()
    
    # Check if full object returned
    if "collection_name" in response_data:
        return self._parse_response(response_data, CollectionResponse)
    
    # Try to extract ID with multiple possible field names
    collection_id = (
        response_data.get("collection_id") or 
        response_data.get("id") or
        response_data.get("collectionId")
    )
    
    # Provide helpful error if ID not found
    if not collection_id:
        raise APIError(f"Create response missing collection ID. Response: {response_data}")
    
    # Fetch full details
    return self.get(project_id, collection_id)
```

## Next Steps

When you run `python test_sdk_quick.py` now:

1. **If it succeeds**: Great! The API returns one of the expected formats
2. **If it fails**: You'll see the exact API response in the error message

### If You See an Error

The error will look like:
```
APIError: Create response missing collection ID. Response: {...actual response...}
```

**What to do**:
1. Copy the `Response:` part from the error
2. Share it so we can see the exact field names the API uses
3. We'll update the SDK to handle that specific format

## Files Modified

- `nostradamus_ioto_sdk/resources/collections.py`
- `nostradamus_ioto_sdk/resources/projects.py`
- `nostradamus_ioto_sdk/resources/project_keys.py`

All `create()` and `acreate()` methods now have improved error handling.

---

*Updated: 2026-02-01*
