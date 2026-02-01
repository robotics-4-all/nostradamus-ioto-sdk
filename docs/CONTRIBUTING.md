# Contributing to Nostradamus IoTO SDK

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Setup Instructions

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/nostradamus-ioto-sdk.git
   cd nostradamus-ioto-sdk
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   make install-dev
   ```

4. **Verify installation**
   ```bash
   make test
   ```

## Code Style Guidelines

This project follows strict code style guidelines. Please refer to [AGENTS.md](./AGENTS.md) for detailed coding standards.

### Key Points
- **Python Version**: Target Python 3.8+
- **Line Length**: 88 characters (Black default)
- **Imports**: Standard library → Third-party → Local (use isort)
- **Type Hints**: Required for all public functions
- **Docstrings**: Google style format
- **Testing**: >85% coverage required

### Running Code Quality Checks

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make typecheck

# Run all checks
make ci
```

## Testing

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Specific test file
pytest tests/unit/test_auth.py

# Specific test function
pytest tests/unit/test_auth.py::test_oauth2_login
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names: `test_<what>_<condition>_<expected>`
- Mock external HTTP calls using `respx`
- Aim for >85% code coverage

Example:
```python
import pytest
from nostradamus_ioto_sdk import NostradamusClient

def test_client_initialization_with_api_key_succeeds():
    """Test that client initializes correctly with API key."""
    client = NostradamusClient(api_key="test-key")
    assert client is not None
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   make format
   make ci
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   Follow conventional commits format:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

6. **PR Requirements**
   - All tests must pass
   - Code coverage must not decrease
   - All CI checks must pass
   - Code must be reviewed and approved
   - Documentation must be updated

## Reporting Bugs

Use GitHub Issues to report bugs. Please include:
- Python version
- SDK version
- Minimal reproducible example
- Expected vs actual behavior
- Full error traceback

## Feature Requests

Feature requests are welcome! Please:
- Check existing issues first
- Clearly describe the use case
- Explain why it would be useful
- Consider submitting a PR

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's guidelines

## Questions?

- Open a GitHub Issue for questions
- Check existing documentation first
- Search closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
