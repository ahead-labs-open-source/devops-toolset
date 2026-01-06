"""Constants for the Postman project type module."""

# Postman Collection Schema
POSTMAN_COLLECTION_SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"

# Supported OpenAPI versions
SUPPORTED_OPENAPI_VERSIONS = ["3.0.0", "3.0.1", "3.0.2", "3.0.3", "3.1.0"]

# HTTP Methods
HTTP_METHODS = ["get", "post", "put", "delete", "patch", "options", "head", "trace"]

# Content Types
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_FORM_URLENCODED = "application/x-www-form-urlencoded"
CONTENT_TYPE_FORM_DATA = "multipart/form-data"
CONTENT_TYPE_XML = "application/xml"
CONTENT_TYPE_TEXT = "text/plain"

# Azure AD OAuth2 Token Endpoint
AZURE_AD_TOKEN_ENDPOINT = "https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token"

# Default values
DEFAULT_API_VERSION = "1.0.0"
DEFAULT_API_TITLE = "API"
DEFAULT_BASE_URL = "{{baseUrl}}"

# File naming
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
COLLECTION_FILENAME_TEMPLATE = "{title}_v{version}_{timestamp}_collection.json"
ENVIRONMENT_FILENAME_TEMPLATE = "{title}_v{version}_{timestamp}_{environment}_environment.json"
