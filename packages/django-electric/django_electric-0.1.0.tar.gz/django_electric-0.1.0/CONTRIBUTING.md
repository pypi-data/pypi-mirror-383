# Contributing to Django Electric

Thank you for your interest in contributing to Django Electric! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/django-electric.git
cd django-electric
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=django_electric --cov-report=html

# Run specific test
pytest tests/test_client.py::TestElectricClient::test_sync_shape_success

# Run in watch mode
pytest-watch
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with black
black django_electric tests

# Sort imports with isort
isort django_electric tests

# Lint with flake8
flake8 django_electric

# Type check with mypy
mypy django_electric
```

### Pre-commit Checks

Run all checks before committing:

```bash
# Format
black . && isort .

# Lint
flake8 django_electric

# Type check
mypy django_electric

# Test
pytest
```

## Making Changes

### 1. Code Style

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes

Example:

```python
def sync_model(
    model: Type[models.Model],
    where: Optional[str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Sync a Django model with Electric SQL.

    Args:
        model: Django model class to sync
        where: SQL WHERE clause for filtering
        force: Force sync even if recently synced

    Returns:
        Dictionary containing sync result

    Raises:
        ElectricSyncError: If sync fails
    """
    pass
```

### 2. Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use pytest fixtures for common setups
- Mock external services (Electric SQL API)

Example:

```python
import pytest
from unittest.mock import Mock, patch

def test_sync_success(sync_manager):
    """Test successful sync operation."""
    with patch("django_electric.client.ElectricClient.sync_shape") as mock_sync:
        mock_sync.return_value = {"shape_id": "test-123"}

        shape = SyncShape(table="users")
        result = sync_manager.sync(shape)

        assert result["shape_id"] == "test-123"
        mock_sync.assert_called_once()
```

### 3. Documentation

- Update README.md for new features
- Add docstrings to all public APIs
- Update examples if needed
- Add inline comments for complex logic

### 4. Commit Messages

Use clear, descriptive commit messages:

```
Add support for WebSocket subscriptions

- Implement async WebSocket connection handler
- Add subscription management
- Include tests for WebSocket functionality
- Update documentation with WebSocket examples
```

## Pull Request Process

### 1. Before Submitting

- [ ] All tests pass
- [ ] Code is formatted (black, isort)
- [ ] No linting errors (flake8)
- [ ] Type checking passes (mypy)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (for significant changes)

### 2. Submit PR

1. Push your branch to your fork
2. Create a Pull Request to `main` branch
3. Fill out the PR template
4. Link any related issues

### 3. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test the changes

## Checklist
- [ ] Tests pass
- [ ] Code is formatted
- [ ] Documentation updated
```

### 4. Review Process

- Maintainers will review your PR
- Address any feedback
- Once approved, your PR will be merged

## Project Structure

```
django-electric/
├── django_electric/       # Main package
│   ├── __init__.py
│   ├── client.py         # Electric SQL client
│   ├── sync.py           # Sync manager
│   ├── models.py         # Model mixins
│   ├── managers.py       # Model managers
│   ├── signals.py        # Django signals
│   ├── middleware.py     # Middleware
│   ├── decorators.py     # Utility decorators
│   └── management/       # Management commands
├── tests/                # Test suite
├── examples/             # Example projects
├── docs/                 # Documentation
└── pyproject.toml        # Package configuration
```

## Feature Requests

Have an idea? Open an issue with:

- Clear description of the feature
- Use cases
- Potential implementation approach
- Examples

## Bug Reports

Found a bug? Open an issue with:

- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (Python version, Django version, etc.)
- Stack trace if applicable

## Questions

- Check existing documentation
- Search closed issues
- Ask in GitHub Discussions
- Open a new issue with the "question" label

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. Build: `python -m build`
6. Upload to PyPI: `twine upload dist/*`

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Thank You!

Your contributions make Django Electric better for everyone. Thank you for taking the time to contribute!
