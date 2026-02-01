# Postman Project Type Module

This module provides tools for working with Postman collections and converting OpenAPI specifications to Postman collections.

## Features

- **OpenAPI to Postman Conversion**: Convert OpenAPI 3.0+ specifications (YAML or JSON) to Postman Collection v2.1 format
- **Environment Generation**: Automatically generate environment files for multiple deployment environments
- **JWT Authentication**: Automatically includes Azure AD OAuth2 token endpoint for authentication
- **Version Tracking**: Generated files include API version and timestamp for better organization
- **Flexible Input**: Supports both local files and remote URLs for OpenAPI specifications
- **Automated Deployment**: Deploy collections and environments to Postman workspaces
- **Secret Injection**: Inject secrets into environment files during deployment

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

---

## inject_secrets_and_deploy.py

This module automates the deployment of Postman collections and environments to Postman workspaces, with built-in secret injection and optional GitHub Actions secret masking.

### Purpose

Replaces manual Bash scripting in CI/CD workflows with a maintainable Python module that:
- Injects secrets into Postman environment files (APIM keys, Azure AD credentials)
- Optionally masks secrets for GitHub Actions (`::add-mask::` workflow commands)
- Deploys collections and environments to Postman workspaces via REST API

### Usage

#### Basic Deployment

```bash
python -m devops_toolset.project_types.postman.inject_secrets_and_deploy \
  --collection ./AI-Assistant-API.postman_collection.json \
  --environment ./postman/environments/ai-assistant-staging.postman_environment.json \
  --workspace-id 12345678-1234-1234-1234-123456789012 \
  --apim-api-key "my-apim-key" \
  --client-secret "my-client-secret" \
  --api-key "${POSTMAN_API_KEY}"
```

#### With GitHub Actions Secret Masking

```bash
python -m devops_toolset.project_types.postman.inject_secrets_and_deploy \
  --collection ./collection.json \
  --environment ./environment.json \
  --workspace-id "${WORKSPACE_ID}" \
  --apim-api-key "${APIM_API_KEY}" \
  --tenant-id "${AZURE_TENANT_ID}" \
  --client-id "${AZURE_CLIENT_ID}" \
  --client-secret "${ARM_CLIENT_SECRET}" \
  --api-key "${POSTMAN_API_KEY}" \
  --mask-secrets
```

The `--mask-secrets` flag emits GitHub Actions workflow commands to prevent secret leakage in logs:
```
::add-mask::my-apim-key
::add-mask::my-client-secret
```

### Parameters

| Parameter           | Required | Description                                              |
|---------------------|----------|----------------------------------------------------------|
| `--collection`      | Yes      | Path to Postman collection JSON file                     |
| `--environment`     | Yes      | Path to Postman environment JSON file                    |
| `--workspace-id`    | Yes      | Target Postman workspace ID                              |
| `--apim-api-key`    | Yes      | Azure API Management subscription key                    |
| `--client-secret`   | Yes      | Azure AD application client secret                       |
| `--tenant-id`       | No       | Azure AD tenant ID (injected as `tenantId` variable)     |
| `--client-id`       | No       | Azure AD application client ID                           |
| `--api-key`         | No       | Postman API key (or set `POSTMAN_API_KEY` env var)      |
| `--mask-secrets`    | No       | Emit GitHub Actions `::add-mask::` commands              |

### Secret Injection

The module injects the following secrets into the environment JSON:

| Environment Variable       | Type    | Description                        |
|----------------------------|---------|------------------------------------|
| `ocpApimSubscriptionKey`   | secret  | APIM API key (from `--apim-api-key`) |
| `tenantId`                 | default | Azure AD tenant ID                 |
| `clientId`                 | default | Azure AD application client ID     |
| `clientSecret`             | secret  | Azure AD client secret             |

Variables are **upserted** (created if missing, updated if existing) in the environment's `values` array with `enabled: true`.

### Integration with GitHub Actions

Replace inline Bash scripting with this module:

**Before (Bash):**
```yaml
- name: Deploy to Postman
  run: |
    echo "::add-mask::${{ secrets.APIM_API_KEY }}"
    # 80 lines of complex Bash...
```

**After (Python):**
```yaml
- name: Deploy to Postman
  run: |
    python -m devops_toolset.project_types.postman.inject_secrets_and_deploy \
      --collection ./AI-Assistant-API.postman_collection.json \
      --environment ./postman/environments/ai-assistant-${{ inputs.environment }}.postman_environment.json \
      --workspace-id ${{ secrets.POSTMAN_WORKSPACE_ID }} \
      --apim-api-key "${{ secrets.APIM_API_KEY }}" \
      --tenant-id "${{ secrets.AZURE_TENANT_ID }}" \
      --client-id "${{ secrets.AZURE_CLIENT_ID }}" \
      --client-secret "${{ secrets.ARM_CLIENT_SECRET }}" \
      --api-key "${{ secrets.POSTMAN_API_KEY }}" \
      --mask-secrets
```

### Error Handling

The module returns exit code `1` on failure:
- Missing required secrets (`APIM_API_KEY`, `ARM_CLIENT_SECRET`)
- Missing Postman API key (neither `--api-key` nor `POSTMAN_API_KEY` env var)
- File not found errors (collection or environment)
- Postman API errors (HTTP 4xx/5xx responses)

### Dependencies

Reuses existing `deploy_to_workspace.py` functions:
- `upsert_collection()` - Create or update Postman collection
- `upsert_environment()` - Create or update Postman environment
- `_load_json_file()` - Load and parse JSON files
- `PostmanApiError` - Postman API exception handling

### Testing

Comprehensive unit tests with >95% coverage:
```bash
pytest tests/project_types/postman/inject_secrets_and_deploy_test.py -v
```

Test coverage includes:
- Secret injection (create, update, preserve existing values)
- GitHub Actions secret masking
- CLI argument parsing
- File validation
- Error scenarios (missing files, missing secrets)
- Integration with `deploy_to_workspace` module (mocked)
