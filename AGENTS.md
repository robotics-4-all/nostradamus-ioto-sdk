# Agent Guidelines for Nostradamus IoT Observatory SDK

Guidelines for AI agents working on the Nostradamus IoT Observatory Python SDK - a client library for integrating IoT observatory functionality.

## Build, Lint, and Test Commands

### Setup
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Testing
```bash
pytest                                    # Run all tests
pytest tests/test_filename.py             # Run single test file
pytest tests/test_filename.py::test_name  # Run single test function
pytest -k "pattern"                       # Run tests matching pattern
pytest -v                                 # Verbose output
pytest -x                                 # Stop at first failure
pytest --cov=nostradamus_ioto_sdk --cov-report=html  # Coverage report
```

### Linting and Formatting
```bash
black .                    # Format code
black --check .            # Check formatting
isort .                    # Sort imports
isort --check-only .       # Check import sorting
ruff check .               # Lint code
ruff check --fix .         # Auto-fix issues
mypy nostradamus_ioto_sdk  # Type checking
```

### Building
```bash
python -m build   # Build distribution packages
pip install -e .  # Install locally
```

## Code Style Guidelines

### Python Version
- **Target**: Python 3.8+
- Use modern Python features but maintain compatibility with 3.8

### Imports
- **Order**: Standard library → Third-party → Local imports
- **Tool**: Use `isort` with Black-compatible profile
- **Style**: Absolute imports preferred; relative imports only within packages
- **Example**:
```python
import os
from typing import Optional, Dict, Any

import requests
from pydantic import BaseModel

from nostradamus_ioto_sdk.exceptions import APIError
from .utils import validate_response
```

### Formatting
- Line length: 88 characters (Black default)
- Double quotes for strings
- 4 spaces indentation (never tabs)
- Trailing commas in multi-line structures

### Type Hints
- All public functions/methods must have type hints
- Always specify return types (use `None` for no return)
- Example:
```python
from typing import Optional, Dict, Any

def fetch_device_data(device_id: str, include_metadata: bool = False) -> Dict[str, Any]:
    """Fetch device data from the API."""
    pass
```

### Naming Conventions
- Functions/Variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_private_method`
- Boolean variables: `is_`, `has_`, `can_` prefix

### Documentation
- **Docstrings**: Google style format
- **Module level**: Brief description at top of file
- **Public API**: All public functions/classes must have docstrings
- **Example**:
```python
def authenticate(api_key: str, timeout: int = 30) -> AuthToken:
    """Authenticate with the Nostradamus API.
    
    Args:
        api_key: The API key for authentication.
        timeout: Request timeout in seconds. Defaults to 30.
    
    Returns:
        AuthToken object containing the session token.
    
    Raises:
        AuthenticationError: If authentication fails.
        TimeoutError: If request times out.
    """
```

### Error Handling
- **Custom exceptions**: Define in `exceptions.py` module
- **Hierarchy**: Inherit from base SDK exception class
- **Logging**: Use `logging` module, not `print()`
- **Re-raising**: Preserve context with `raise ... from err`
- **Example**:
```python
import logging
from .exceptions import APIError, AuthenticationError

logger = logging.getLogger(__name__)

try:
    response = requests.get(url)
    response.raise_for_status()
except requests.HTTPError as err:
    logger.error(f"API request failed: {err}")
    raise APIError(f"Failed to fetch data: {err}") from err
```

### Testing Guidelines
- **Framework**: pytest
- **Coverage**: Aim for >80% code coverage
- **File naming**: `test_*.py` or `*_test.py`
- **Test naming**: `test_<what>_<condition>_<expected>`
- **Fixtures**: Use pytest fixtures for setup/teardown
- **Mocking**: Use `unittest.mock` or `pytest-mock`
- **Example**:
```python
import pytest
from nostradamus_ioto_sdk import Client

def test_client_authentication_with_valid_key_succeeds():
    """Test that client authenticates successfully with valid API key."""
    client = Client(api_key="valid_key")
    assert client.is_authenticated is True
```

### Project Structure
```
nostradamus-ioto-sdk/
├── nostradamus_ioto_sdk/     # Main package
│   ├── __init__.py           # Package exports
│   ├── client.py             # Main client class
│   ├── models.py             # Data models (Pydantic)
│   ├── exceptions.py         # Custom exceptions
│   └── utils.py              # Utility functions
├── tests/                    # Test directory
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   └── test_client.py
├── docs/                     # Documentation
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml           # Project metadata and config
└── setup.py                 # Setup configuration (if needed)
```

### Dependencies
- **Required**: Specify in `pyproject.toml` under `[project.dependencies]`
- **Development**: Specify under `[project.optional-dependencies]`
- **Pinning**: Use flexible version constraints for library (`>=x.y`)
- **Lock files**: Consider using `poetry.lock` or `requirements.txt` for reproducibility

### Git Commit Messages
- Format: `<type>: <description>`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
- Keep first line under 72 characters
- Example: `feat: add device registration endpoint`

## Additional Notes
- Prefer composition over inheritance
- Keep functions small and focused (single responsibility)
- Use context managers for resource management
- Avoid global state; use dependency injection
- Write idiomatic Python ("Pythonic" code)
