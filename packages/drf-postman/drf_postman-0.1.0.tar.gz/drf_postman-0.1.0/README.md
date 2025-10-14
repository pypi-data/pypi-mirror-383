# DRF Postman

Generate Postman Collections from your Django REST Framework APIs with a single command. This tool automatically introspects your DRF routes and generates a ready-to-import Postman Collection v2.1 JSON file.

## Installation

```bash
pip install drf-postman
```

Add to your `INSTALLED_APPS`:

```py
INSTALLED_APPS = [
    # ...
    'drf_postman'
]
```

Configure your REST framework settings:

```py
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

## Quick Start

Generate a Postman collection:

```bash
python3 manage.py generatepostman
```

This creates `postman_collection.json` in your project root. Import into Postman and start testing!

## Usage

### Basic Command

```bash
python3 manage.py generatepostman
```

### With Options

```bash
# Custom output path
python3 manage.py generatepostman --output my_api.json

# Custom collection name
python3 manage.py generatepostman --name "My Awesome API"

# Custom base URL
python3 manage.py generatepostman --base-url "https://api.example.com"

# All together
python3 manage.py generatepostman -o collections/api.json -n "My API v2" -b "https://staging.api.com"
```

## Configuration

Customize defaults in your `settings.py`:

```py
DRF_POSTMAN = {
    'COLLECTION_NAME': 'My API',
    'BASE_URL': 'https://api.example.com',
    'OUTPUT_PATH': 'postman_collection.json',
}
```

## What Gets Generated

### Collection Structure

```
My API Collection
├── Accounts
│   ├── POST Login
│   └── POST Register
└── Todos
    ├── GET List Todos
    ├── POST Create Todo
    ├── GET Retrieve Todo
    ├── PUT Update Todo
    └── DELETE Delete Todo
```

### Request Features

-   Method & URL: Correctly formatted with path parameters
-   Headers: Content-Type and Authorization when needed
-   Body: JSON examples generated from serializers
-   Parameters: Path and query parameters with descriptions
-   Variables: {{base_url}} environment variable included

### Example Request Body

For a serializer like:

```python
class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'completed']
        read_only_fields = ['id']
```

Generates:

```json
{
    "title": "string",
    "description": "string",
    "completed": true
}
```

> Note: `id` is excluded because it's read-only.

## Requirements

-   Python >= 3.8
-   Django >= 3.2
-   Django REST Framework >= 3.12
-   drf-spectacular >= 0.26.0

## How It Works

1. Uses `drf-spectacular` to generate an OpenAPI 3.0 schema from your DRF routes
2. Converts the OpenAPI schema to Postman Collection v2.1 format
3. Groups endpoints by tags (typically ViewSet names)
4. Generates example request bodies from serializer schemas
5. Includes authentication, parameters, and metadata

## Limitations

-   Requires `drf-spectacular` for schema generation

## Example Project

Check out the `example_project/` directory for a complete example with:

-   JWT Authentication
-   django-filter integration
-   Multiple related models

Run it:

```bash
cd example_project
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py generatepostman
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

Tests coming soon :)

## License

MIT License - see [LICENSE](./LICENSE.md) file for details.

## Support

If you encounter any issues or have questions:

1. [Open an issue](https://github.com/kimanikevin254/django-drf-postman/issues)
2. Check existing issues for solutions

---

⭐ Star this repo if you find it useful!
