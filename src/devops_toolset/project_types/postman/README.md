# Postman Project Type Module

This module provides tools for working with Postman collections and converting OpenAPI specifications to Postman collections.

## Features

- **OpenAPI to Postman Conversion**: Convert OpenAPI 3.0+ specifications (YAML or JSON) to Postman Collection v2.1 format
- **Environment Generation**: Automatically generate environment files for multiple deployment environments
- **JWT Authentication**: Automatically includes Azure AD OAuth2 token endpoint for authentication
- **Version Tracking**: Generated files include API version and timestamp for better organization
- **Flexible Input**: Supports both local files and remote URLs for OpenAPI specifications

## Usage

### Basic Usage

```python
from devops_toolset.project_types.postman.openapi_to_postman import OpenAPIToPostmanConverter

# Create converter instance
converter = OpenAPIToPostmanConverter(
    openapi_source="https://petstore3.swagger.io/api/v3/openapi.json",
    output_folder="./output",
    environments=["staging", "production"]
)

# Execute conversion
result = converter.convert()
```

### Command Line Usage

```bash
python -m devops_toolset.project_types.postman.openapi_to_postman
```

### Parameters

- **openapi_source**: Path to OpenAPI YAML/JSON file or URL
- **output_folder**: Directory where generated files will be saved
- **environments**: List of environment names (e.g., `["staging", "production"]`)

## Generated Files

The converter generates the following files:

1. **Collection File**: `{API_Title}_v{version}_{timestamp}_collection.json`
   - Contains all API endpoints from the OpenAPI specification
   - Includes authentication endpoint for JWT token retrieval
   - Organized by OpenAPI tags

2. **Environment Files**: `{API_Title}_v{version}_{timestamp}_{environment}_environment.json`
   - One file per environment specified
   - Pre-configured with variables for authentication and API endpoints

## OpenAPI Support

### Supported Features

- OpenAPI 3.0.x and 3.1.x specifications
- Both YAML and JSON formats
- Path parameters, query parameters, and headers
- Request bodies (JSON, form-urlencoded, multipart)
- Multiple HTTP methods (GET, POST, PUT, DELETE, PATCH, etc.)
- Tag-based organization
- Server URLs

### Authentication

The converter automatically adds an authentication endpoint for Azure AD OAuth2:

```
POST https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token
```

This endpoint supports client credentials flow with the following parameters:
- `grant_type`: client_credentials
- `client_id`: {{clientId}}
- `client_secret`: {{clientSecret}}
- `scope`: {{scope}}

## Environment Variables

Each generated environment file includes the following variables:

- **baseUrl**: Base API URL for the environment
- **environment**: Environment name (staging, production, etc.)
- **tenantId**: Azure AD tenant ID (to be filled)
- **clientId**: Azure AD application client ID (to be filled)
- **clientSecret**: Azure AD application client secret (to be filled)
- **scope**: OAuth2 scope (default: api://.default)
- **accessToken**: JWT token storage (populated after authentication)

## Examples

### Using Petstore API

```python
converter = OpenAPIToPostmanConverter(
    openapi_source="https://petstore3.swagger.io/api/v3/openapi.json",
    output_folder="./postman_collections",
    environments=["dev", "staging", "production"]
)

result = converter.convert()

# Output:
# {
#     'collection': './postman_collections/Swagger_Petstore_v1.0.17_20260104_123456_collection.json',
#     'environments': [
#         './postman_collections/Swagger_Petstore_v1.0.17_20260104_123456_dev_environment.json',
#         './postman_collections/Swagger_Petstore_v1.0.17_20260104_123456_staging_environment.json',
#         './postman_collections/Swagger_Petstore_v1.0.17_20260104_123456_production_environment.json'
#     ],
#     'api_version': '1.0.17',
#     'api_title': 'Swagger Petstore'
# }
```

### Using Local File

```python
converter = OpenAPIToPostmanConverter(
    openapi_source="./api-spec.yaml",
    output_folder="./output",
    environments=["staging", "production"]
)

result = converter.convert()
```

## Dependencies

- Python 3.7+
- PyYAML (for YAML support)

## Notes

- Generated files include timestamps to avoid overwriting
- Collection variables can be overridden by environment variables
- The authentication endpoint is always included in a separate folder
- Path parameters are automatically converted to Postman variables
