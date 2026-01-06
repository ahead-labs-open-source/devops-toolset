"""
OpenAPI to Postman Collection Converter

This module converts OpenAPI 3.0 specifications (YAML or JSON) to Postman Collection v2.1 format.
It also generates environment files for different deployment environments.
"""

import json
import yaml
from datetime import datetime
from collections.abc import Mapping, Sequence
from typing import Any, Optional, cast
from pathlib import Path
import urllib.request

try:
    # Normal package import
    from devops_toolset.project_types.postman.utils import (
        convert_path_to_postman,
        is_url,
        merge_parameters,
        sanitize_filename,
        validate_openapi_version,
    )
except ImportError:  # pragma: no cover
    # Allow running this file directly (e.g. `python openapi_to_postman.py ...`)
    from utils import (  # type: ignore
        convert_path_to_postman,
        is_url,
        merge_parameters,
        sanitize_filename,
        validate_openapi_version,
    )


class OpenAPIToPostmanConverter:
    """Converts OpenAPI specifications to Postman collections and environment files."""

    def __init__(self, openapi_source: str, output_folder: str, environments: Optional[list[str]] = None):
        """
        Initialize the converter.

        Args:
            openapi_source: Path to OpenAPI file or URL
            output_folder: Directory where generated files will be saved
            environments: Optional list of environment names. If not provided, will be read from x-postman-environments in OpenAPI spec
        """
        self.openapi_source = openapi_source
        self.output_folder = Path(output_folder)
        self.environments: Optional[list[str]] = environments  # Will be set from OpenAPI if None
        self.global_vars: dict[str, str] = {}  # Global variables from _global section
        self.openapi_spec: dict[str, Any] = {}
        self.api_version: str = "1.0.0"
        self.api_title: str = "API"
        
        # Ensure output folder exists
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def load_openapi_spec(self) -> None:
        """
        Load OpenAPI specification from file or URL.
        Supports both JSON and YAML formats.
        """
        try:
            # Check if source is a URL
            if is_url(self.openapi_source) or self.openapi_source.startswith(('http://', 'https://')):
                print(f"Downloading OpenAPI spec from: {self.openapi_source}")
                with urllib.request.urlopen(self.openapi_source) as response:
                    content = response.read().decode('utf-8')
                    # Try JSON first, then YAML
                    try:
                        self.openapi_spec = json.loads(content)
                    except json.JSONDecodeError:
                        self.openapi_spec = yaml.safe_load(content)
            else:
                # Load from local file
                file_path = Path(self.openapi_source)
                if not file_path.exists():
                    raise FileNotFoundError(f"OpenAPI file not found: {self.openapi_source}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Detect format by extension or content
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    self.openapi_spec = yaml.safe_load(content)
                elif file_path.suffix.lower() == '.json':
                    self.openapi_spec = json.loads(content)
                else:
                    # Try to auto-detect
                    try:
                        self.openapi_spec = json.loads(content)
                    except json.JSONDecodeError:
                        self.openapi_spec = yaml.safe_load(content)
            
            # Extract API information
            info = self.openapi_spec.get('info', {})
            self.api_version = info.get('version', '1.0.0')
            self.api_title = info.get('title', 'API')

            # Basic OpenAPI version validation (non-fatal: raises on clearly unsupported versions)
            openapi_version = str(self.openapi_spec.get('openapi', '')).strip()
            if openapi_version and not validate_openapi_version(openapi_version):
                raise Exception(
                    f"❌ Unsupported OpenAPI version: {openapi_version}. "
                    "Supported versions: 3.0.x and 3.1.0"
                )
            
            # Determine version display with prefix (avoiding double 'v')
            version_prefix = '' if self.api_version.startswith('v') else 'v'
            version_display = f"{version_prefix}{self.api_version}"
            
            # If environments not provided, read from x-postman-environments
            if self.environments is None:
                # Validate x-postman-environments exists
                if 'x-postman-environments' not in self.openapi_spec:
                    raise Exception(
                        "❌ Missing 'x-postman-environments' section in OpenAPI specification.\n"
                        "Please add the x-postman-environments section with at least one environment configuration.\n"
                        "Example:\n"
                        "x-postman-environments:\n"
                        "  _global:  # Optional: shared variables\n"
                        "    tenantId: \"your-tenant-id\"\n"
                        "  staging:\n"
                        "    clientId: \"your-client-id\"\n"
                        "    clientSecret: \"<replace-with-your-secret>\"\n"
                        "    scope: \"api://your-client-id/.default\""
                    )
                
                x_postman_envs_raw: Any = self.openapi_spec.get('x-postman-environments', {})
                if not isinstance(x_postman_envs_raw, dict):
                    raise Exception("❌ 'x-postman-environments' must be a dictionary/object")

                # Narrow unknown types coming from YAML/JSON parsing
                x_postman_envs: dict[str, dict[str, str]] = {}
                x_postman_envs_raw_dict = cast(dict[object, Any], x_postman_envs_raw)
                for env_name_any, env_config_raw in x_postman_envs_raw_dict.items():
                    if not isinstance(env_name_any, str):
                        continue
                    env_name = env_name_any
                    if isinstance(env_config_raw, dict):
                        env_config_raw_dict = cast(dict[str, Any], env_config_raw)
                        env_config: dict[str, str] = {
                            str(k): "" if v is None else str(v)
                            for k, v in env_config_raw_dict.items()
                        }
                    else:
                        env_config = {}
                    x_postman_envs[env_name] = env_config
                
                # Extract _global variables (if present) and filter from environments
                self.global_vars = x_postman_envs.get('_global', {})
                env_list: list[str] = [k for k in x_postman_envs.keys() if k != '_global']
                
                # Validate at least one environment exists (excluding _global)
                if not env_list or len(env_list) == 0:
                    raise Exception(
                        "❌ The 'x-postman-environments' section has no environments defined.\n"
                        "At least one environment (other than _global) must be defined."
                    )
                
                self.environments = env_list
                print(f"Loaded OpenAPI spec: {self.api_title} {version_display}")
                if self.global_vars:
                    print(f"Detected global variables: {', '.join(self.global_vars.keys())}")
                print(f"Detected environments from x-postman-environments: {', '.join(self.environments)}")
                
                # Validate environment consistency (excluding _global)
                envs_without_global: dict[str, dict[str, str]] = {
                    k: v for k, v in x_postman_envs.items() if k != '_global'
                }
                self._validate_environment_consistency(envs_without_global)
            else:
                print(f"Loaded OpenAPI spec: {self.api_title} {version_display}")
                assert self.environments is not None
                print(f"Using provided environments: {', '.join(self.environments)}")
            
        except Exception as e:
            raise Exception(f"Error loading OpenAPI specification: {str(e)}")

    def _validate_environment_consistency(self, x_postman_envs: dict[str, dict[str, str]]) -> None:
        """
        Validate that all environments have the same set of keys.
        Note: _global section should be filtered out before calling this method.
        
        Args:
            x_postman_envs: Dictionary of environment configurations (excluding _global)
            
        Raises:
            Exception: If environments have inconsistent keys
        """
        if not x_postman_envs or len(x_postman_envs) < 2:
            return  # Nothing to validate if 0 or 1 environment
        
        # Get all unique keys across all environments
        all_keys: set[str] = set()
        env_keys: dict[str, set[str]] = {}
        for env_name, env_config in x_postman_envs.items():
            keys: set[str] = set(env_config.keys())
            env_keys[env_name] = keys
            all_keys.update(keys)
        
        # Check if all environments have the same keys
        inconsistencies: list[str] = []
        for env_name, keys in env_keys.items():
            missing_keys = all_keys - keys
            if missing_keys:
                inconsistencies.append(f"  - Environment '{env_name}' is missing keys: {', '.join(sorted(missing_keys))}")
        
        if inconsistencies:
            error_msg = "❌ Environment validation failed: Inconsistent keys in x-postman-environments\n"
            error_msg += "\n".join(inconsistencies)
            error_msg += f"\n\nAll environments must have the same keys. Expected keys: {', '.join(sorted(all_keys))}"
            raise Exception(error_msg)
        
        print(f"✅ Environment validation passed: All environments have consistent keys ({', '.join(sorted(all_keys))})")

    def _get_base_url(self) -> str:
        """
        Extract base URL from OpenAPI servers section.
        
        Returns:
            Base URL string from servers[0].url, or '{{baseUrl}}' if none.
        """
        servers = self.openapi_spec.get('servers', [])
        if servers:
            return servers[0].get('url', '{{baseUrl}}')
        return '{{baseUrl}}'

    def _convert_parameters(self, parameters: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """
        Convert OpenAPI parameters to Postman format.
        
        Args:
            parameters: List of OpenAPI parameter objects
            
        Returns:
            Dictionary with 'query', 'header', and 'path' parameter lists
        """
        result: dict[str, list[dict[str, Any]]] = {
            'query': [],
            'header': [],
            'path': []
        }
        
        for param in parameters:
            # Skip $ref parameters (not resolved here)
            if '$ref' in param:
                continue

            param_in = str(param.get('in', 'query'))
            postman_param: dict[str, Any] = {
                'key': str(param.get('name', '')),
                'value': '',
                'description': str(param.get('description', '')),
                'disabled': not param.get('required', False)
            }
            
            if param_in in result:
                result[param_in].append(postman_param)
        
        return result

    def _convert_request_body(self, request_body: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        """
        Convert OpenAPI request body to Postman body format.
        
        Args:
            request_body: OpenAPI requestBody object
            
        Returns:
            Postman body object or None
        """
        if not request_body:
            return None
        
        content_raw: Any = request_body.get('content', {})
        content: dict[str, Any] = cast(dict[str, Any], content_raw) if isinstance(content_raw, dict) else {}
        
        # Prefer JSON content
        if 'application/json' in content:
            json_content_raw: Any = content.get('application/json')
            json_content: dict[str, Any] = cast(dict[str, Any], json_content_raw) if isinstance(json_content_raw, dict) else {}

            example: Any = json_content.get('example')
            if example is None:
                examples: Any = json_content.get('examples') or {}
                if isinstance(examples, dict) and examples:
                    first_example = next(iter(cast(dict[str, Any], examples).values()))
                    if isinstance(first_example, dict) and 'value' in first_example:
                        example = first_example['value']

            schema = json_content.get('schema', {})
            if example is None:
                # Schema may not be a concrete example; use empty object by default
                example = {} if isinstance(schema, dict) else {}
            
            return {
                'mode': 'raw',
                'raw': json.dumps(example, indent=2, ensure_ascii=False),
                'options': {
                    'raw': {
                        'language': 'json'
                    }
                }
            }
        
        # Handle form data
        elif 'application/x-www-form-urlencoded' in content:
            return {
                'mode': 'urlencoded',
                'urlencoded': []
            }
        
        # Handle multipart form data
        elif 'multipart/form-data' in content:
            return {
                'mode': 'formdata',
                'formdata': []
            }
        
        return None

    def _create_postman_request(
        self,
        path: str,
        method: str,
        operation: dict[str, Any],
        parameters: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """
        Create a Postman request item from OpenAPI operation.
        
        Args:
            path: API endpoint path
            method: HTTP method (GET, POST, etc.)
            operation: OpenAPI operation object
            parameters: Merged parameter list (path-level + operation-level)
            
        Returns:
            Postman request item
        """
        # Convert OpenAPI template path to Postman format (/users/{id} -> /users/:id)
        postman_path = convert_path_to_postman(path)
        param_dict = self._convert_parameters(parameters)

        # Build URL object. Keep it minimal so {{baseUrl}} can include protocol and path.
        url_obj: dict[str, Any] = {
            'raw': f"{{{{baseUrl}}}}{postman_path}",
            'query': param_dict['query']
        }
        
        # Build request object
        request: dict[str, Any] = {
            'name': operation.get('summary', operation.get('operationId', f"{method.upper()} {path}")),
            'request': {
                'method': method.upper(),
                'header': param_dict['header'],
                'url': url_obj,
                'description': operation.get('description', '')
            }
        }
        
        # Add request body if present
        request_body = self._convert_request_body(operation.get('requestBody'))
        if request_body:
            request['request']['body'] = request_body
        
        return request

    def _create_auth_request(self) -> dict[str, Any]:
        """
        Create JWT token authentication request for Azure AD.
        
        Returns:
            Postman request item for getting JWT token
        """
        return {
            'name': 'Get JWT Token',
            'request': {
                'method': 'POST',
                'header': [
                    {
                        'key': 'Content-Type',
                        'value': 'application/x-www-form-urlencoded'
                    }
                ],
                'body': {
                    'mode': 'urlencoded',
                    'urlencoded': [
                        {
                            'key': 'grant_type',
                            'value': 'client_credentials',
                            'type': 'text'
                        },
                        {
                            'key': 'client_id',
                            'value': '{{clientId}}',
                            'type': 'text'
                        },
                        {
                            'key': 'client_secret',
                            'value': '{{clientSecret}}',
                            'type': 'text'
                        },
                        {
                            'key': 'scope',
                            'value': '{{scope}}',
                            'type': 'text'
                        }
                    ]
                },
                'url': {
                    'raw': 'https://login.microsoftonline.com/{{tenantId}}/oauth2/v2.0/token',
                    'protocol': 'https',
                    'host': ['login', 'microsoftonline', 'com'],
                    'path': ['{{tenantId}}', 'oauth2', 'v2.0', 'token']
                },
                'description': 'Get JWT token from Azure AD for API authentication'
            },
            'response': [],
            'event': [
                {
                    'listen': 'test',
                    'script': {
                        'exec': [
                            '// Automatically capture the access token from the response',
                            'if (pm.response.code === 200) {',
                            '    const jsonData = pm.response.json();',
                            '    if (jsonData.access_token) {',
                            '        pm.environment.set("accessToken", jsonData.access_token);',
                            '        console.log("✅ Access token captured and stored in environment");',
                            '    }',
                            '}'
                        ],
                        'type': 'text/javascript'
                    }
                }
            ]
        }

    def generate_collection(self) -> str:
        """
        Generate Postman collection from OpenAPI specification.
        
        Returns:
            Path to generated collection file
        """
        if not self.openapi_spec:
            raise Exception("OpenAPI specification not loaded. Call load_openapi_spec() first.")
        
        paths_raw: Any = self.openapi_spec.get('paths', {})
        paths: dict[str, Any] = cast(dict[str, Any], paths_raw) if isinstance(paths_raw, dict) else {}
        
        # Create authentication folder
        auth_folder: dict[str, Any] = {
            'name': 'Authentication',
            'item': [self._create_auth_request()],
            'description': 'Authentication endpoints'
        }
        
        # Determine collection name with version (avoiding double 'v' prefix)
        version_prefix = '' if self.api_version.startswith('v') else 'v'
        collection_name = f"{self.api_title} {version_prefix}{self.api_version}"
        
        # Create collection structure (all variables are in environment files)
        collection: dict[str, Any] = {
            'info': {
                'name': collection_name,
                'description': self.openapi_spec.get('info', {}).get('description', ''),
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            'item': [auth_folder]
        }
        
        # Group endpoints by tags or create flat structure
        endpoint_folders: dict[str, list[dict[str, Any]]] = {}
        
        for path, path_item in paths.items():
            for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                if not isinstance(path_item, dict) or method not in path_item:
                    continue

                path_item_dict = cast(dict[str, Any], path_item)
                operation_raw: Any = path_item_dict.get(method)
                if not isinstance(operation_raw, dict):
                    continue
                operation: dict[str, Any] = cast(dict[str, Any], operation_raw)

                tags_raw: Any = operation.get('tags', ['Default'])
                tags: list[str] = [str(t) for t in tags_raw] if isinstance(tags_raw, list) else ['Default']
                tag: str = tags[0] if tags else 'Default'
                    
                if tag not in endpoint_folders:
                    endpoint_folders[tag] = []
                    
                # Merge path-level and operation-level parameters
                path_level_params_raw: Any = path_item_dict.get('parameters', [])
                operation_params_raw: Any = operation.get('parameters', [])
                path_level_params = (
                    [cast(dict[str, Any], p) for p in path_level_params_raw if isinstance(p, dict)]
                    if isinstance(path_level_params_raw, list)
                    else []
                )
                operation_params = (
                    [cast(dict[str, Any], p) for p in operation_params_raw if isinstance(p, dict)]
                    if isinstance(operation_params_raw, list)
                    else []
                )
                merged_params = merge_parameters(
                    cast(list[dict[str, Any]], path_level_params),
                    cast(list[dict[str, Any]], operation_params),
                )

                request_item = self._create_postman_request(path, method, operation, merged_params)
                endpoint_folders[tag].append(request_item)
        
        # Add folders to collection
        for folder_name, requests in endpoint_folders.items():
            collection['item'].append({
                'name': folder_name,
                'item': requests
            })
        
        # Generate filename with version and timestamp (reusing collection_name for consistency)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{sanitize_filename(collection_name)}_{timestamp}_collection.json"
        file_path = self.output_folder / filename
        
        # Write collection file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        print(f"Generated collection: {file_path}")
        return str(file_path)

    def generate_environment_files(self) -> list[str]:
        """
        Generate Postman environment files for each specified environment.
        
        Returns:
            List of paths to generated environment files
        """
        if not self.openapi_spec:
            raise Exception("OpenAPI specification not loaded. Call load_openapi_spec() first.")
        
        base_url = self._get_base_url()
        generated_files: list[str] = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Determine name prefix with version (avoiding double 'v' prefix)
        version_prefix = '' if self.api_version.startswith('v') else 'v'
        name_base = f"{self.api_title} {version_prefix}{self.api_version}"
        filename_base = sanitize_filename(name_base)
        
        # Get x-postman-environments from OpenAPI spec (if exists)
        x_postman_envs_raw: Any = self.openapi_spec.get('x-postman-environments', {})
        x_postman_envs: dict[str, Any] = cast(dict[str, Any], x_postman_envs_raw) if isinstance(x_postman_envs_raw, dict) else {}

        assert self.environments is not None
        
        for env_name in self.environments:
            # Get environment-specific values from x-postman-environments
            env_config_raw: Any = x_postman_envs.get(env_name, {})
            env_config: dict[str, str] = cast(dict[str, str], env_config_raw) if isinstance(env_config_raw, dict) else {}
            
            # Merge global variables with environment-specific ones (env-specific overrides global)
            merged_config: dict[str, str] = {**self.global_vars, **env_config}
            
            # Determine baseUrl based on environment
            env_base_url = base_url
            if env_name == 'staging':
                # Use staging server from OpenAPI servers array
                servers = self.openapi_spec.get('servers', [])
                for server in servers:
                    if 'stg' in server.get('url', '').lower() or 'staging' in server.get('description', '').lower():
                        env_base_url = server.get('url', base_url)
                        break
            elif env_name == 'production':
                # Use production server (usually the first without staging markers)
                servers = self.openapi_spec.get('servers', [])
                for server in servers:
                    if 'stg' not in server.get('url', '').lower() and 'staging' not in server.get('description', '').lower():
                        env_base_url = server.get('url', base_url)
                        break
            
            environment: dict[str, Any] = {
                'id': f"{env_name}-{timestamp}",
                'name': f"{name_base} - {env_name.capitalize()}",
                'values': [
                    {
                        'key': 'baseUrl',
                        'value': env_base_url,
                        'type': 'default',
                        'enabled': True
                    },
                    {
                        'key': 'environment',
                        'value': env_name,
                        'type': 'default',
                        'enabled': True
                    },
                    {
                        'key': 'tenantId',
                        'value': merged_config.get('tenantId', ''),
                        'type': 'secret',
                        'enabled': True
                    },
                    {
                        'key': 'clientId',
                        'value': merged_config.get('clientId', ''),
                        'type': 'secret',
                        'enabled': True
                    },
                    {
                        'key': 'clientSecret',
                        'value': merged_config.get('clientSecret', '<replace-with-your-secret>'),
                        'type': 'secret',
                        'enabled': True
                    },
                    {
                        'key': 'scope',
                        'value': merged_config.get('scope', 'api://.default'),
                        'type': 'default',
                        'enabled': True
                    },
                    {
                        'key': 'accessToken',
                        'value': '',
                        'type': 'secret',
                        'enabled': True
                    }
                ],
                '_postman_variable_scope': 'environment'
            }
            
            # Generate filename using consistent naming (reusing filename_base for consistency)
            filename = f"{filename_base}_{timestamp}_{env_name}_environment.json"
            file_path = self.output_folder / filename
            
            # Write environment file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(environment, f, indent=2, ensure_ascii=False)
            
            generated_files.append(str(file_path))
            print(f"Generated environment: {file_path}")
        
        return generated_files

    def convert(self) -> dict[str, Any]:
        """
        Execute the full conversion process.
        
        Returns:
            Dictionary with paths to generated files
        """
        print("=" * 60)
        print("OpenAPI to Postman Converter")
        print("=" * 60)
        
        # Load OpenAPI specification
        self.load_openapi_spec()
        
        # Generate collection
        collection_file = self.generate_collection()
        
        # Generate environment files
        environment_files = self.generate_environment_files()
        
        result: dict[str, Any] = {
            'collection': collection_file,
            'environments': environment_files,
            'api_version': self.api_version,
            'api_title': self.api_title
        }
        
        print("=" * 60)
        print("Conversion completed successfully!")
        print(f"Collection: {collection_file}")
        print(f"Environments: {len(environment_files)} files generated")
        print("=" * 60)
        
        return result


def main(openapi_source: str, output_folder: str, environments: Optional[list[str]] = None):
    """
    Main function for command-line usage.
    
    Args:
        openapi_source: Path to OpenAPI file or URL
        output_folder: Directory where generated files will be saved
        environments: Optional list of environment names. If not provided, reads from x-postman-environments
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        converter = OpenAPIToPostmanConverter(
            openapi_source=openapi_source,
            output_folder=output_folder,
            environments=environments
        )
        
        result = converter.convert()
        
        print()
        print("=" * 70)
        print("✅ GENERATION SUCCESSFUL")
        print("=" * 70)
        version_prefix = '' if str(result['api_version']).startswith('v') else 'v'
        print(f"API: {result['api_title']} {version_prefix}{result['api_version']}")
        print(f"Collection: {result['collection']}")
        print(f"Environments ({len(result['environments'])} files):")
        for env_file in result['environments']:
            print(f"  - {env_file}")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert OpenAPI 3.0 specifications to Postman Collection v2.1 format",
        epilog="""
Examples:
  python openapi_to_postman.py openapi.yaml ./output
  python openapi_to_postman.py openapi.yaml ./output --environments staging production
  python openapi_to_postman.py https://petstore3.swagger.io/api/v3/openapi.json ./output

OpenAPI x-postman-environments structure:
  x-postman-environments:
    _global:                    # Optional: Variables shared across all environments
      tenantId: "your-tenant-id"
    staging:
      clientId: "staging-client-id"
      scope: "api://staging-client-id/.default"
    production:
      clientId: "production-client-id"
      scope: "api://production-client-id/.default"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "openapi_source",
        help="Path to OpenAPI specification file or URL"
    )
    parser.add_argument(
        "output_folder",
        help="Directory where generated files will be saved"
    )
    parser.add_argument(
        "--environments",
        nargs='+',
        default=None,
        help="Optional environment names (e.g., staging production). If not provided, reads from x-postman-environments in OpenAPI spec"
    )
    
    args = parser.parse_args()
    
    exit(main(args.openapi_source, args.output_folder, args.environments))
