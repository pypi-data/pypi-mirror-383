# Rango API Framework

A modern Python web framework built on FastAPI with Django-like features for rapid API development.

## Features

- **FastAPI Integration**: Built on top of FastAPI for high performance and automatic API documentation
- **Django-like Structure**: Familiar project and app structure similar to Django
- **ORM Integration**: Built-in Tortoise ORM support with migrations
- **Generic Views**: Pre-built views for common CRUD operations
- **Serializers**: Django REST Framework-like serializers
- **CLI Tools**: Command-line interface for project management
- **CORS Middleware**: Built-in CORS support

## Installation

```bash
pip install rango-api
```

## Quick Start

### 1. Create a new project

```bash
rango startproject myproject
cd myproject
```

### 2. Create an app

```bash
rango startapp blog
```






### Initialize database
Init Aerich config

```bash

aerich init -t project.settings.TORTOISE_ORM
```
Create database & initial migration

```bash

aerich init-db
```
Make migrations after changing models

```bash

aerich migrate --name "initial"
aerich upgrade
```

Every time you create or modify models:
 aerich migrate --name "your_message" → aerich upgrade






### 3. Run migrations

```bash
rango makemigrations
rango migrate
```

### 4. Start the development server

```bash
rango runserver
```

## Tutorial

### Create models with ForeignKey

```python
from tortoise import fields, models

class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)

class Product(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    category = fields.ForeignKeyField('models.Category', related_name='products')
```

### Serializers (nested FK supported)

```python
from rango_api.serializers import ModelSerializer
from .models import Category, Product

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "category"]  # can send category or category_id
        nested_serializers = {
            'Category': CategorySerializer
        }
```

### Views (generic, with FK optimization)

```python
from rango_api.generics import ListCreateView, RetrieveUpdateDeleteView
from .models import Product
from .serializers import ProductSerializer

class ProductListCreateView(ListCreateView):
    model = Product
    serializer_class = ProductSerializer
    select_related = ['category']  # optimize FK

class ProductDetailView(RetrieveUpdateDeleteView):
    model = Product
    serializer_class = ProductSerializer
    select_related = ['category']
```

### URLs

```python
from rango_api.router import Router
from .views import ProductListCreateView, ProductDetailView

router = Router()
router.add("/products", ProductListCreateView, methods=["GET", "POST"])
router.add("/products/{id}", ProductDetailView, methods=["GET", "PUT", "PATCH", "DELETE"])
```

### Test the API

- Create category:
```bash
curl -X POST http://127.0.0.1:8000/categories \
  -H "Content-Type: application/json" \
  -d '{"name":"Electronics"}'
```

- Create product (supports category or category_id):
```bash
curl -X POST http://127.0.0.1:8000/products \
  -H "Content-Type: application/json" \
  -d '{"title":"Phone","category":1}'
```

## Extensibility (DRF-like Hooks)

You can override hooks in generic views to customize behavior:

```python
class ProductListCreateView(ListCreateView):
    model = Product
    serializer_class = ProductSerializer

    def get_queryset(self, request):
        return self.model.all().select_related('category')

    async def before_create(self, request, data: dict) -> dict:
        # mutate/validate incoming data
        data.setdefault("title", data.get("title", "Untitled"))
        return data

    async def after_create(self, request, obj):
        # side-effects, logging, etc.
        return obj

class ProductDetailView(RetrieveUpdateDeleteView):
    model = Product
    serializer_class = ProductSerializer

    async def before_update(self, request, obj, data: dict) -> dict:
        # e.g. normalize FK input
        if 'category' in data and 'category_id' not in data:
            data['category_id'] = data.pop('category')
        return data
```

Available hooks include: `get_queryset`, `filter_queryset`, `before_create`, `perform_create`, `after_create`, `before_update`, `perform_update`, `after_update`, `before_delete`, `perform_delete`, `after_delete`.

## Project Structure

```
myproject/
├── apps/
│   └── blog/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
├── project/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── asgi.py
├── main.py
└── manage.py
```

## Basic Usage

### Models

```python
from tortoise import fields, models

class Post(models.Model):
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
```

### Serializers

```python
from rango_api.serializers import ModelSerializer
from .models import Post

class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "content", "created_at"]
```

### Views

```python
from rango_api.generics import ListCreateView, RetrieveUpdateDeleteView
from .models import Post
from .serializers import PostSerializer

class PostListCreateView(ListCreateView):
    model = Post
    serializer_class = PostSerializer

class PostDetailView(RetrieveUpdateDeleteView):
    model = Post
    serializer_class = PostSerializer
```

### URLs

```python
from rango_api.router import Router
from .views import PostListCreateView, PostDetailView

router = Router()
router.add("/posts", PostListCreateView, methods=["GET", "POST"])
router.add("/posts/{id}", PostDetailView, methods=["GET", "PUT", "DELETE"])
```

## CLI Commands

- `rango startproject <name>` - Create a new project
- `rango startapp <name>` - Create a new app
- `rango makemigrations [message]` - Create database migrations
- `rango migrate` - Apply database migrations
- `rango runserver [host] [port]` - Start development server

## Requirements

- Python 3.8+
- FastAPI
- Tortoise ORM
- Uvicorn

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you have any questions or need help, please open an issue on GitHub.