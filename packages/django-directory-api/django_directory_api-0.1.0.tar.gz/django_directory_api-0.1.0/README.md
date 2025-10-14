# django-directory-api

Reusable Django REST API framework with auto-discovery and bearer token authentication.

## Features

- 🔐 **Bearer Token Authentication** - Secure API access with per-user tokens
- 🔌 **Auto-Discovery** - Automatically discovers and registers API routers from `api.py` files
- 📚 **Django Shinobi** - Built on Django Shinobi (Django Ninja fork) for type-safe APIs
- 🤖 **LLM-Optimized** - Rich OpenAPI documentation designed for AI agent consumption
- 🎯 **Zero Config** - Just create an `api.py` file and start building

## Installation

```bash
pip install django-directory-api
```

## Quick Start

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django_directory_api",  # Must come before apps that define API endpoints
    # ...
]
```

### 2. Include API URLs

```python
# urls.py
from django_directory_api import api

urlpatterns = [
    path("api/", api.urls),
    # ...
]
```

### 3. Create API Endpoints

Create an `api.py` file in any Django app:

```python
# myapp/api.py
from ninja import Router
from .models import MyModel

router = Router(tags=["My App"])

@router.get("/items/")
def list_items(request):
    return {"items": list(MyModel.objects.values())}
```

That's it! The router is automatically discovered and registered.

## Authentication

### Creating API Tokens

1. Log into Django admin
2. Navigate to "API Tokens"
3. Click "Add API Token"
4. Give it a name (e.g., "Production Bot")
5. Copy the token value (shown only once)

### Using Tokens

```bash
curl -H "Authorization: Bearer <your-token>" \
     https://example.com/api/items/
```

```python
import requests

headers = {"Authorization": "Bearer <your-token>"}
response = requests.get("https://example.com/api/items/", headers=headers)
```

## Auto-Discovery

The package automatically discovers `api.py` files in all installed Django apps:

- ✅ Looks for `router` attribute (single router)
- ✅ Looks for `routers` attribute (list of routers)
- ✅ Skips apps without `api.py` files
- ✅ No explicit registration required

### Example with Multiple Routers

```python
# myapp/api.py
from ninja import Router

public_router = Router(tags=["Public"])
admin_router = Router(tags=["Admin"])

@public_router.get("/public/")
def public_endpoint(request):
    return {"message": "Hello world"}

@admin_router.get("/admin/")
def admin_endpoint(request):
    return {"message": "Admin only"}

# Export multiple routers
routers = [public_router, admin_router]
```

## API Documentation

Once installed, automatic documentation is available at:

- **Swagger UI**: `/api/docs`
- **OpenAPI Schema**: `/api/openapi.json`
- **ReDoc**: `/api/redoc`

## Architecture

The package provides:

1. **APIToken Model** - Database-backed authentication tokens
2. **APIKeyAuth** - Bearer token authentication handler
3. **Auto-Discovery System** - Scans apps for `api.py` files at startup
4. **Common Schemas** - Shared Pydantic schemas (e.g., PaginatedResponse)

## Development

```bash
# Install dependencies
uv sync --extra dev

# Run tests
python tests/manage.py test

# Format code
ruff format .

# Lint
ruff check .
```

## License

MIT License - see LICENSE file for details.
