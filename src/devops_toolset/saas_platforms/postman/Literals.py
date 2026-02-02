"""Literals for the Postman project type module."""

from devops_toolset.core.ValueDictsBase import ValueDictsBase


class Literals(ValueDictsBase):
    """Literal strings for the Postman module."""

    _messages = {
        "loading_openapi": "Loading OpenAPI specification from: {source}",
        "loaded_openapi": "Loaded OpenAPI spec: {title} v{version}",
        "error_loading_openapi": "Error loading OpenAPI specification: {error}",
        "error_file_not_found": "OpenAPI file not found: {path}",
        "generating_collection": "Generating Postman collection...",
        "collection_generated": "Generated collection: {path}",
        "generating_environments": "Generating environment files...",
        "environment_generated": "Generated environment: {path}",
        "conversion_started": "OpenAPI to Postman Converter",
        "conversion_completed": "Conversion completed successfully!",
        "error_no_spec_loaded": "OpenAPI specification not loaded. Call load_openapi_spec() first.",
        "separator": "=" * 60
    }

    _errors = {
        "invalid_openapi": "Invalid OpenAPI specification format",
        "unsupported_version": "Unsupported OpenAPI version: {version}",
        "missing_required_field": "Missing required field in OpenAPI spec: {field}",
        "conversion_failed": "Conversion failed: {error}"
    }

    _warnings = {
        "no_servers_defined": "No servers defined in OpenAPI spec, using default baseUrl",
        "missing_operation_id": "Missing operationId for {method} {path}",
        "unsupported_content_type": "Unsupported content type: {content_type}"
    }
