# Django Electric

A Django integration package for [Electric SQL](https://electric-sql.com/), enabling real-time data synchronization between Django applications and client devices.

[![PyPI version](https://badge.fury.io/py/django-electric.svg)](https://badge.fury.io/py/django-electric)
[![Python versions](https://img.shields.io/pypi/pyversions/django-electric.svg)](https://pypi.org/project/django-electric/)
[![Django versions](https://img.shields.io/badge/django-4.2%20%7C%205.0-blue)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## What is Electric SQL?

Electric SQL is a sync engine that enables local-first development with real-time synchronization. Instead of traditional request-response patterns, Electric provides efficient delta-based syncing between your backend database and client applications.

## Features

- **Seamless Django Integration**: Works naturally with Django ORM and existing models
- **Real-time Sync**: Bidirectional synchronization between Django and Electric SQL
- **Shape-based Sync**: Sync specific data subsets using SQL-like filters
- **Offline-First**: Build applications that work offline and sync when connected
- **Type-Safe**: Full type hints and mypy support
- **Battle-Tested**: Comprehensive test suite with pytest
- **Developer-Friendly**: Management commands, admin integration, and decorators
- **Signals Support**: React to sync events with Django signals
- **Caching**: Built-in caching for sync operations

## Installation

```bash
pip install django-electric
```

## Quick Start

### 1. Add to `INSTALLED_APPS`

```python
# settings.py
INSTALLED_APPS = [
    ...
    'django_electric',
    ...
]
```

### 2. Configure Electric SQL

```python
# settings.py

# Electric service URL (required)
ELECTRIC_SERVICE_URL = 'http://localhost:5133'

# Optional settings
ELECTRIC_AUTH_TOKEN = 'your-auth-token'  # If using authentication
ELECTRIC_AUTO_SYNC = True  # Auto-sync on model save
ELECTRIC_SYNC_BATCH_SIZE = 100  # Batch size for sync operations
ELECTRIC_TIMEOUT = 30  # Request timeout in seconds
```

### 3. Update Your Models

```python
from django.db import models
from django_electric.models import ElectricSyncMixin
from django_electric.managers import ElectricManager

class Article(ElectricSyncMixin, models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Use Electric manager for sync capabilities
    objects = ElectricManager()

    class Meta:
        electric_sync = True  # Enable sync for this model
        electric_where = "published = true"  # Only sync published articles
```

### 4. Sync Your Data

```python
# Sync to Electric
result = Article.electric_sync()
print(f"Shape ID: {result['shape_id']}")

# Pull data from Electric
stats = Article.electric_pull()
print(f"Created: {stats['created']}, Updated: {stats['updated']}")

# Get synced data
articles = Article.electric_get_data(limit=50)
```

### 5. Use Management Commands

```bash
# Check Electric status
python manage.py electric_status

# Sync all models
python manage.py electric_sync --all

# Sync specific model
python manage.py electric_sync --model myapp.Article

# Pull data from Electric
python manage.py electric_sync --model myapp.Article --pull
```

## Documentation

### Core Concepts

#### Shape-Based Syncing

Electric SQL uses "shapes" to define what data to sync. A shape is a subset of your data defined by:

- **Table**: Which model/table to sync
- **Where clause**: SQL filter for the data
- **Columns**: Specific fields to include
- **Include**: Related models to sync

```python
# Sync only published articles
Article.electric_sync(where="published = true")

# Sync with specific columns
shape = Article.get_electric_shape(
    columns=['id', 'title', 'created_at']
)
```

#### Model Configuration

Configure sync behavior in your model's `Meta` class:

```python
class Meta:
    electric_sync = True  # Enable sync
    electric_where = "status = 'active'"  # Default filter
    electric_columns = ['id', 'name', 'email']  # Specific columns
```

### API Reference

#### Model Methods

**`Model.electric_sync(where=None, force=False)`**

Sync model to Electric SQL.

```python
Article.electric_sync(where="published = true", force=True)
```

**`Model.electric_pull(where=None, update_existing=True)`**

Pull data from Electric to local database.

```python
stats = Article.electric_pull(where="created_at > '2024-01-01'")
```

**`Model.electric_get_data(where=None, offset=0, limit=100)`**

Get synced data from Electric.

```python
articles = Article.electric_get_data(limit=50)
```

#### Decorators

**`@electric_cached(timeout=300)`**

Cache Electric sync results.

```python
from django_electric.decorators import electric_cached

@electric_cached(timeout=600)
def get_articles():
    return Article.electric_get_data()
```

**`@electric_retry(max_attempts=3, delay=1.0)`**

Retry sync operations on failure.

```python
from django_electric.decorators import electric_retry

@electric_retry(max_attempts=5)
def sync_all_data():
    Article.electric_sync()
    Comment.electric_sync()
```

#### Client API

For advanced usage, use the `ElectricClient` directly:

```python
from django_electric.client import ElectricClient

with ElectricClient() as client:
    # Create a shape
    shape = client.create_shape(
        table="articles",
        where="published = true",
        columns=["id", "title", "content"]
    )

    # Sync the shape
    result = client.sync_shape(shape)

    # Get shape data
    data = client.get_shape_data(result['shape_id'])
```

### Management Commands

#### `electric_status`

Check Electric SQL connection and configuration.

```bash
python manage.py electric_status
```

#### `electric_sync`

Sync models with Electric SQL.

```bash
# Sync all models
python manage.py electric_sync --all

# Sync specific model
python manage.py electric_sync --model blog.Post

# Sync with custom filter
python manage.py electric_sync --model blog.Post --where "published = true"

# Force sync (ignore cache)
python manage.py electric_sync --model blog.Post --force

# Pull data from Electric
python manage.py electric_sync --model blog.Post --pull
```

### Django Admin Integration

Add Electric sync to your admin actions:

```python
from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    actions = ['sync_to_electric', 'pull_from_electric']

    def sync_to_electric(self, request, queryset):
        result = Article.electric_sync()
        self.message_user(request, f"Synced: {result}")

    def pull_from_electric(self, request, queryset):
        stats = Article.electric_pull()
        self.message_user(
            request,
            f"Created: {stats['created']}, Updated: {stats['updated']}"
        )
```

### Signals

React to sync events:

```python
from django_electric.signals import (
    electric_sync_started,
    electric_sync_completed,
    electric_sync_failed,
)

@receiver(electric_sync_completed)
def on_sync_complete(sender, **kwargs):
    print(f"Sync completed for {sender.__name__}")

@receiver(electric_sync_failed)
def on_sync_failed(sender, error, **kwargs):
    print(f"Sync failed: {error}")
```

## Examples

See the [examples/demo_project](examples/demo_project) directory for a complete working Django application demonstrating:

- Model configuration with Electric sync
- Management command usage
- Admin panel integration
- API views with sync operations
- Decorator usage

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/django-electric.git
cd django-electric

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=django_electric

# Run specific test file
pytest tests/test_client.py

# Run in watch mode
pytest-watch
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint
flake8 django_electric
mypy django_electric

# Type checking
mypy django_electric
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Publishing to PyPI

```bash
# Build the package
python -m build

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## Requirements

- Python >= 3.9
- Django >= 4.2
- Electric SQL service running

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/django-electric/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/django-electric/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/django-electric/wiki)

## Acknowledgments

- Built for [Electric SQL](https://electric-sql.com/)
- Inspired by local-first and offline-first architectures
- Thanks to the Django and Electric SQL communities

## Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Conflict resolution strategies
- [ ] Multi-tenancy support
- [ ] GraphQL integration
- [ ] Django REST Framework integration
- [ ] Async support with Django 4.2+
- [ ] Schema migration tools
- [ ] Performance monitoring and metrics

---

Made with ❤️ for the Django and Electric SQL communities
