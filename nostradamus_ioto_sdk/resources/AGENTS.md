# resources — API Resource Classes

## OVERVIEW

One class per API domain. Each provides sync + async CRUD methods. All inherit `BaseResource`.

## STRUCTURE

| File | Class | API Domain | Endpoints |
|------|-------|------------|-----------|
| `_base.py` | `BaseResource` | — | Path building, response parsing, UUID validation |
| `organizations.py` | `OrganizationsResource` | Organizations | `get`, `update` |
| `projects.py` | `ProjectsResource` | Projects | `list`, `get`, `create`, `update`, `delete` |
| `collections.py` | `CollectionsResource` | Collections | `list`, `get`, `create`, `update`, `delete` |
| `data.py` | `DataResource` | Data | `send`, `get`, `delete`, `stats` |
| `project_keys.py` | `ProjectKeysResource` | API Keys | `list`, `create`, `delete` |

## PATTERNS

### Method Naming
- Sync: `list()`, `get()`, `create()`, `update()`, `delete()`
- Async: `alist()`, `aget()`, `acreate()`, `aupdate()`, `adelete()`
- Each sync method has an async twin — **always add both**

### BaseResource API
```python
self._client              # Parent client (sync or async)
self._base_path           # "/api/v1"
self._build_path(*parts)  # Joins parts: _build_path("projects", id) → "/api/v1/projects/{id}"
self._parse_response(data, ModelClass)  # Dict → Model or List[Dict] → List[Model]
self._validate_uuid(value)              # Validates and stringifies UUID
```

### Request Flow
```python
# Sync
response = self._client._request("GET", self._build_path("projects", project_id))
return self._parse_response(response.json(), ProjectResponse)

# Async
response = await self._client._request("GET", self._build_path("projects", project_id))
return self._parse_response(response.json(), ProjectResponse)
```

## ADDING A NEW RESOURCE

1. Create `{entity}.py` in `resources/`
2. Inherit `BaseResource`
3. Import client types under `TYPE_CHECKING` only
4. Implement sync methods + async twins (prefix `a`)
5. Wire in `client.py`: `self.{entity} = {Entity}Resource(self)`
6. Wire in `async_client.py`: same line
7. Create models in `models/{entity}.py`

## QUIRKS

- **`projects.create()`** has special handling: API may return full object OR just an ID/message with UUID. The method extracts the UUID from response text via regex and re-fetches. Duplicated in `acreate()`.
- **Circular import guard**: Client types imported only under `if TYPE_CHECKING:`. The `_base.py` imports both `NostradamusClient` and `AsyncNostradamusClient` this way.
- **mypy overrides**: This module has `union-attr`, `misc`, `return-value` errors disabled in `pyproject.toml` because sync/async methods coexist on the same class with different client types.

## ANTI-PATTERNS

- **NEVER** import `NostradamusClient` or `AsyncNostradamusClient` at module level — circular import
- **NEVER** add sync-only method without async twin (or vice versa)
- **NEVER** build URL paths manually — use `self._build_path()`
