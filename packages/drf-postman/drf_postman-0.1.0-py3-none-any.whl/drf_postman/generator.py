import json
from typing import Dict, Any, Optional
from drf_spectacular.generators import SchemaGenerator

class PostmanCollectionGenerator:
    """
    Core logic for generating a Postman v2.1 collection with the following steps:
        1. Generate a OpenAPI schema using drf_spectacular
        2. Generate a Postman v2.1 collection from the OpenAPI schema using custom methods
    """

    def __init__(self, collection_name: str = "API Collection", base_url: str = "{{base_url}}"):
        """
        Initialize the generator.

        Args:
            collection_name: The name of the Postman collection. Defaults to "API Collection" 
            base_url: The base URL for the collection. Defaults to {{base_url}}, a environment variable in Postman.
        """
        self.collection_name = collection_name
        self.base_url = base_url

    def generate_openapi_schema(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 collection from DRF routes"""
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)
        return schema
    
    def convert_to_postman_collection(self, openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert OpenAPI 3.0 collection to Postman collection v2.1"""
        collection = {
            "info": {
                "name": self.collection_name,
                "description": openapi_schema.get("info", {}).get("description", ""),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [],
            "variable": [
                {
                    "key": "base_url",
                    "value": openapi_schema.get("servers", [{}])[0].get("url", "http://localhost:8000"),
                    "type": "string"
                }
            ]
        }

        # Group endpoints by tags (typically corresponds to apps/viewsets)
        paths = openapi_schema.get('paths', {})
        tags_map = {}

        for path, methods in paths.items():
            for method, details in methods.items():
                if method not in ['get', 'post', 'patch', 'put', 'delete']:
                    continue

                # Get tags
                tags = details.get('tags')
                tag = tags[0] if tags else 'Default'

                if tag not in tags_map:
                    tags_map[tag] = []

                # Build Postman request
                request = self._build_request(path, method, details, openapi_schema)
                tags_map[tag].append(request)

        # Convert tags to folders
        for tag, requests in tags_map.items():
            collection['item'].append({
                'name': tag,
                "item": requests
            })

        return collection

    def _build_request(self, path: str, method: str, details: Dict[str, Any], openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Build a single Postman request item"""
        # Convert OpenAPI path params to Postman format
        postman_path = path.replace("{", ":").replace("}", "")

        request = {
            'name': details.get('summary') or details.get('operationId', f"{method.upper()} {path}"),
            'request': {
                'method': method.upper(),
                'header': self._build_headers(details),
                'url': {
                    'raw': f'{self.base_url}{postman_path}',
                    'host': [self.base_url],
                    'path': [p for p in postman_path.strip('/').split('/') if p],
                    'variable': self._extract_path_variables(path, details)
                }
            },
            'response': []
        }

        # Add object body if applicable
        if method.lower() in ['post', 'put', 'patch']:
            body = self._build_request_body(details, openapi_schema)
            if body:
                request['request']['body'] = body

        # Add query parameters
        query_params = self._extract_query_params(details)
        if query_params:
            request["request"]["url"]["query"] = query_params
        
        # Add description
        if details.get("description"):
            request["request"]["description"] = details["description"]
        
        return request

    def _build_headers(self, details: Dict[str, Any]) -> list:
        """Build request headers"""
        headers = [
            {
                'key': 'Content-Type',
                'value': 'application/json'
            }
        ]

        # Check if authentication is required
        security = details.get('security', [])
        if security:
            headers.append({
                'key': 'Authorization',
                'value': 'Bearer {{access_token}}'
            })

        return headers

    def _extract_path_variables(self, path: str, details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract path variables for Postman."""
        variables = []
        parameters = details.get("parameters", [])
        
        for param in parameters:
            if param.get("in") == "path":
                variables.append({
                    "key": param["name"],
                    "value": "",
                    "description": param.get("description", "")
                })
        
        return variables

    def _build_request_body(self, details: Dict[str, Any], openapi_schema: Dict[str, Any]):
        """Build request body from schema"""
        request_body = details.get('requestBody', {})
        content = request_body.get('content', {})

        if "application/json" in content:
            json_schema = content['application/json'].get('schema', {})
            example = self._generate_example_from_schema(json_schema, openapi_schema)

            return {
                'mode': 'raw',
                'raw': json.dumps(example, indent=2),
                'options': {
                    'raw': {
                        'language': 'json'
                    }
                }
            }
        
        return None

    def _extract_query_params(self, details: Dict[str, Any]):
        """Extract query parameters."""
        query_params = []
        parameters = details.get("parameters", [])
        
        for param in parameters:
            if param.get("in") == "query":
                query_params.append({
                    "key": param["name"],
                    "value": "",
                    "description": param.get("description", ""),
                    "disabled": not param.get("required", False)
                })
        
        return query_params

    def _generate_example_from_schema(self, json_schema: Dict[str, Any], root_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate example JSON from OpenAPI schema.
        
        This function recursively traverses an OpenAPI schema to build example data.
        It handles schema references ($ref) and nested object structures.
        
        Args:
            json_schema: The current schema node being processed
            root_schema: The complete OpenAPI schema (needed to resolve $ref)
        
        Returns:
            A dictionary representing example data matching the schema
        """
        
        # Handle $ref: OpenAPI uses JSON references to avoid duplication
        # Example: "$ref": "#/components/schemas/Todo"
        if '$ref' in json_schema:
            # Split the reference path into parts
            # "#/components/schemas/Todo" becomes ['#', 'components', 'schemas', 'Todo']
            ref_path = json_schema['$ref'].split('/')
            
            # Navigate through the root schema following the reference path
            ref_schema = root_schema
            for part in ref_path:
                # Skip the '#' anchor symbol
                if part == '#':
                    continue
                # Drill down: components -> schemas -> Todo
                ref_schema = ref_schema.get(part, {})
            
            # Recursively generate example from the referenced schema
            return self._generate_example_from_schema(ref_schema, root_schema)
        
        # Handle object type: generate example for each property
        if json_schema.get('type') == 'object':
            properties = json_schema.get('properties', {})
            example = {}
            
            # Build example object by processing each property
            for prop_name, prop_schema in properties.items():
                # Skip readOnly properties (like id, created_at, updated_at)
                # These are set by the server and shouldn't be in request bodies
                if prop_schema.get('readOnly', False):
                    continue

                example[prop_name] = self._get_example_value(prop_schema, root_schema)
            
            return example
        
        # For non-object types (string, integer, etc.), get a simple example value
        return self._get_example_value(json_schema, root_schema)
    
    def _get_example_value(self, schema: Dict[str, Any], root_schema: Dict[str, Any]) -> Any:
        """
        Get an example value for a single schema property.
        
        This function determines what example value to use for a property based on:
        1. Explicit examples in the schema (highest priority)
        2. Schema references that need resolution
        3. The property's type (fallback to sensible defaults)
        
        Args:
            schema: The schema for the current property
            root_schema: The complete OpenAPI schema (for resolving $ref)
        
        Returns:
            An example value appropriate for the property type
        """
        
        # Priority 1: Use explicit example if provided in schema
        # OpenAPI allows schemas to define example values like: {"type": "string", "example": "john@example.com"}
        if "example" in schema:
            return schema["example"]
        
        # Priority 2: Handle $ref - property references another schema
        # Example: "user": {"$ref": "#/components/schemas/User"}
        if "$ref" in schema:
            return self._generate_example_from_schema(schema, root_schema)
        
        # Priority 3: Generate default value based on JSON Schema type
        prop_type = schema.get("type", "string")  # Default to string if no type specified
        
        # Map of JSON Schema types to sensible example values
        type_examples = {
            "string": "string",      # Generic string placeholder
            "integer": 0,            # Zero for whole numbers
            "number": 0.0,           # Zero for floats/decimals
            "boolean": True,         # True as default boolean
            "array": [],             # Empty array
            "object": {}             # Empty object
        }
        
        # Return the example for this type, defaulting to "string" if type is unknown
        return type_examples.get(prop_type, "string")
    
    def generate(self) -> Dict[str, Any]:
        """Main method to generate Postman collection."""
        openapi_schema = self.generate_openapi_schema()
        postman_collection = self.convert_to_postman_collection(openapi_schema)
        return postman_collection
    
    def save_to_file(self, output_path: str) -> None:
        """Generate and save collection to file."""
        collection = self.generate()
        with open(output_path, 'w') as f:
            json.dump(collection, f, indent=2)