"""
OpenAPI to Postman Collection Converter

This module converts OpenAPI 3.0 specifications (YAML or JSON) to Postman Collection v2.1 format.
It also generates environment files for different deployment environments.
"""

import json
import yaml
from datetime import datetime, timezone
from collections.abc import Mapping, Sequence
from typing import Any, Optional, cast
from pathlib import Path
import urllib.request
import re
from urllib.parse import urlparse, urlunparse


POSTMAN_BASE_URL_TEMPLATE = "{{baseUrl}}"

try:
    # Normal package import
    from devops_toolset.saas_platforms.postman.utils import (
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
        self.generated_at_iso: str = datetime.now(timezone.utc).isoformat()
        self.api_id_slug: str = ""  # Stable API identifier (without version)
        
        # Ensure output folder exists
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def _generate_api_id_slug(self, title: str) -> str:
        """
        Generate a stable API identifier slug from the title, removing version suffix.
        
        Args:
            title: The API title (e.g., "AI Personal Assistant API v1-rev0")
            
        Returns:
            Slug identifier (e.g., "ai-personal-assistant-api")
        """
        try:
            from devops_toolset.saas_platforms.postman.utils import strip_version_suffix
        except ImportError:  # pragma: no cover
            from utils import strip_version_suffix  # type: ignore

        slug = strip_version_suffix(title)
        
        # Convert to lowercase
        slug = slug.lower()
        
        # Replace spaces and special characters with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        
        # Remove leading/trailing hyphens and collapse multiple hyphens
        slug = re.sub(r'-+', '-', slug).strip('-')
        
        return slug

    def _load_openapi_source_text(self) -> tuple[str, Optional[Path]]:
        """Load raw OpenAPI source text from URL or local file."""

        parsed_source = urlparse(self.openapi_source)
        if parsed_source.scheme == "http":
            raise ValueError("Refusing to download OpenAPI spec over insecure http; use https")

        if is_url(self.openapi_source) or self.openapi_source.startswith(("http://", "https://")):
            print(f"Downloading OpenAPI spec from: {self.openapi_source}")
            with urllib.request.urlopen(self.openapi_source) as response:
                content = response.read().decode("utf-8")
            return content, None

        file_path = Path(self.openapi_source)
        if not file_path.exists():
            raise FileNotFoundError(f"OpenAPI file not found: {self.openapi_source}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return content, file_path

    def _parse_openapi_text(self, content: str, file_path: Optional[Path]) -> dict[str, Any]:
        """Parse OpenAPI spec text as JSON or YAML, optionally guided by a file extension."""

        if file_path is not None:
            suffix = file_path.suffix.lower()
            if suffix in [".yaml", ".yml"]:
                return cast(dict[str, Any], yaml.safe_load(content))
            if suffix == ".json":
                return cast(dict[str, Any], json.loads(content))

        try:
            return cast(dict[str, Any], json.loads(content))
        except json.JSONDecodeError:
            return cast(dict[str, Any], yaml.safe_load(content))

    def _load_openapi_spec_from_source(self) -> None:
        content, file_path = self._load_openapi_source_text()
        self.openapi_spec = self._parse_openapi_text(content, file_path)

    def _set_api_metadata_from_spec(self) -> None:
        info = self.openapi_spec.get("info", {})
        self.api_version = info.get("version", "1.0.0")
        self.api_title = info.get("title", "API")

        # Generate stable API ID slug (without version)
        self.api_id_slug = self._generate_api_id_slug(self.api_title)

    def _validate_openapi_version_or_raise(self) -> None:
        # Basic OpenAPI version validation (non-fatal: raises on clearly unsupported versions)
        openapi_version = str(self.openapi_spec.get("openapi", "")).strip()
        if openapi_version and not validate_openapi_version(openapi_version):
            raise Exception(
                f"❌ Unsupported OpenAPI version: {openapi_version}. "
                "Supported versions: 3.0.x and 3.1.0"
            )

    def _format_version_display(self) -> str:
        # Determine version display with prefix (avoiding double 'v')
        version_prefix = "" if self.api_version.startswith("v") else "v"
        return f"{version_prefix}{self.api_version}"

    def _parse_x_postman_environments(self) -> dict[str, dict[str, str]]:
        if "x-postman-environments" not in self.openapi_spec:
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

        x_postman_envs_raw: Any = self.openapi_spec.get("x-postman-environments", {})
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

        return x_postman_envs

    def _load_or_validate_environments(self, version_display: str) -> None:
        if self.environments is None:
            x_postman_envs = self._parse_x_postman_environments()

            # Extract _global variables (if present) and filter from environments
            self.global_vars = x_postman_envs.get("_global", {})
            env_list: list[str] = [k for k in x_postman_envs.keys() if k != "_global"]

            # Validate at least one environment exists (excluding _global)
            if not env_list:
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
                k: v for k, v in x_postman_envs.items() if k != "_global"
            }
            self._validate_environment_consistency(envs_without_global)
            return

        print(f"Loaded OpenAPI spec: {self.api_title} {version_display}")
        assert self.environments is not None
        print(f"Using provided environments: {', '.join(self.environments)}")

    def load_openapi_spec(self) -> None:
        """
        Load OpenAPI specification from file or URL.
        Supports both JSON and YAML formats.
        """
        try:
            self._load_openapi_spec_from_source()
            self._set_api_metadata_from_spec()
            self._validate_openapi_version_or_raise()
            version_display = self._format_version_display()
            self._load_or_validate_environments(version_display)
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
            Base URL string from servers[0].url, or a Postman baseUrl template if none.
        """
        servers = self.openapi_spec.get('servers', [])
        if servers:
            return servers[0].get('url', POSTMAN_BASE_URL_TEMPLATE)
        return POSTMAN_BASE_URL_TEMPLATE

    def _get_version_path_segment(self) -> Optional[str]:
        """Derive a version path segment from info.version.

        Examples:
          - v1-rev0 -> v1
          - v2 -> v2
          - 1.0.0 -> v1

        Returns:
            A string like 'v1' or None if it cannot be derived.
        """
        version = str(self.api_version or '').strip()
        if not version:
            return None

        m = re.match(r'^(v\d+)', version, flags=re.IGNORECASE)
        if m:
            # Keep the canonical 'v' prefix
            return f"v{m.group(1)[1:]}"  # normalize casing

        m = re.match(r'^(\d+)', version)
        if m:
            return f"v{m.group(1)}"

        return None

    def _append_version_to_server_url(self, server_url: str) -> str:
        """Append /vN to a server URL based on info.version, if not already present."""
        version_seg = self._get_version_path_segment()
        if not version_seg:
            return server_url

        # Skip templated values like the baseUrl template
        if server_url.strip().startswith('{{'):
            return server_url

        parsed = urlparse(server_url)
        path = (parsed.path or '').rstrip('/')
        if path.lower().endswith('/' + version_seg.lower()):
            new_path = path
        else:
            new_path = (path + '/' + version_seg) if path else ('/' + version_seg)

        return urlunparse(parsed._replace(path=new_path))

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
        content = self._request_body_content(request_body)
        if not content:
            return None

        if 'application/json' in content:
            return self._postman_json_body(content.get('application/json'))
        if 'application/x-www-form-urlencoded' in content:
            return {
                'mode': 'urlencoded',
                'urlencoded': [],
            }
        if 'multipart/form-data' in content:
            return {
                'mode': 'formdata',
                'formdata': [],
            }

        return None

    @staticmethod
    def _request_body_content(request_body: Optional[dict[str, Any]]) -> dict[str, Any]:
        if not request_body:
            return {}
        content_raw: Any = request_body.get('content', {})
        return cast(dict[str, Any], content_raw) if isinstance(content_raw, dict) else {}

    @staticmethod
    def _extract_json_example(json_content: dict[str, Any]) -> Any:
        example: Any = json_content.get('example')
        if example is not None:
            return example

        examples: Any = json_content.get('examples') or {}
        if not isinstance(examples, dict) or not examples:
            return None

        first_example = next(iter(examples.values()), None)
        if isinstance(first_example, dict) and 'value' in first_example:
            return first_example['value']

        return None

    def _postman_json_body(self, json_content_raw: Any) -> dict[str, Any]:
        json_content: dict[str, Any] = (
            cast(dict[str, Any], json_content_raw) if isinstance(json_content_raw, dict) else {}
        )

        example = self._extract_json_example(json_content)
        if example is None:
            # Schema may not be a concrete example; use empty object by default
            example = {}

        return {
            'mode': 'raw',
            'raw': json.dumps(example, indent=2, ensure_ascii=False),
            'options': {
                'raw': {
                    'language': 'json',
                }
            },
        }

    @staticmethod
    def _to_lower_camel_from_header_name(header_name: str) -> str:
        parts = [p for p in re.split(r'[^A-Za-z0-9]+', header_name) if p]
        if not parts:
            return ''
        first = parts[0].lower()
        rest = ''.join(p[:1].upper() + p[1:] for p in parts[1:])
        return first + rest

    def _security_headers_for_operation(self, operation: dict[str, Any]) -> list[dict[str, Any]]:
        """Build Postman headers implied by OpenAPI security requirements."""
        security_reqs = self._security_requirements_for_operation(operation)
        schemes = self._security_schemes()
        used_scheme_names = self._used_security_scheme_names(security_reqs)

        headers: list[dict[str, Any]] = []
        for scheme_name in sorted(used_scheme_names):
            scheme = self._scheme_dict(schemes.get(scheme_name, {}))
            header = self._header_for_security_scheme(scheme)
            if header:
                headers.append(header)

        return headers

    def _security_requirements_for_operation(self, operation: dict[str, Any]) -> list[dict[str, Any]]:
        security_reqs_raw: Any = operation.get('security')
        if security_reqs_raw is None:
            security_reqs_raw = self.openapi_spec.get('security', []) if self.openapi_spec else []

        if not isinstance(security_reqs_raw, list):
            return []
        return [r for r in security_reqs_raw if isinstance(r, dict)]

    def _security_schemes(self) -> dict[str, Any]:
        schemes_raw: Any = (self.openapi_spec or {}).get('components', {}).get('securitySchemes', {})
        return schemes_raw if isinstance(schemes_raw, dict) else {}

    @staticmethod
    def _used_security_scheme_names(security_reqs: list[dict[str, Any]]) -> set[str]:
        used_scheme_names: set[str] = set()
        for req in security_reqs:
            used_scheme_names.update(str(k) for k in req.keys())
        return used_scheme_names

    @staticmethod
    def _scheme_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _header_for_security_scheme(self, scheme: dict[str, Any]) -> Optional[dict[str, Any]]:
        scheme_type = str(scheme.get('type', '')).lower()
        if scheme_type == 'apikey':
            return self._header_for_apikey_scheme(scheme)
        if scheme_type == 'oauth2':
            return {
                'key': 'Authorization',
                'value': 'Bearer {{accessToken}}',
                'description': 'OAuth2 access token',
                'disabled': False,
            }
        return None

    def _header_for_apikey_scheme(self, scheme: dict[str, Any]) -> Optional[dict[str, Any]]:
        if str(scheme.get('in', '')).lower() != 'header':
            return None

        header_name = str(scheme.get('name', '')).strip()
        if not header_name:
            return None

        var_key = self._to_lower_camel_from_header_name(header_name)
        if not var_key:
            return None

        return {
            'key': header_name,
            'value': f"{{{{{var_key}}}}}",
            'description': str(scheme.get('description', '')),
            'disabled': False,
        }

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

        # Build URL object.
        # Postman accepts either a raw string or a structured object. Some Postman clients
        # display the URL bar more reliably when host/path are also provided.
        raw_url = f"{POSTMAN_BASE_URL_TEMPLATE}{postman_path}"
        path_segments = [seg for seg in postman_path.lstrip('/').split('/') if seg]

        url_obj: dict[str, Any] = {
            'raw': raw_url,
            # Keep baseUrl as a single host token so environments can override it.
            # baseUrl may include protocol and base path; raw remains the source of truth.
            'host': [POSTMAN_BASE_URL_TEMPLATE],
            'path': path_segments,
            'query': param_dict['query'],
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

        # Add security-derived headers (e.g., APIM subscription key, OAuth2 token)
        existing_header_keys = {str(h.get('key', '')).lower() for h in request['request'].get('header', []) if isinstance(h, dict)}
        for hdr in self._security_headers_for_operation(operation):
            key_lower = str(hdr.get('key', '')).lower()
            if key_lower and key_lower not in existing_header_keys:
                request['request']['header'].append(hdr)
                existing_header_keys.add(key_lower)
        
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

    @staticmethod
    def _ordinal_suffix(day: int) -> str:
        if 11 <= (day % 100) <= 13:
            return 'th'
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    def _require_openapi_loaded(self) -> None:
        if not self.openapi_spec:
            raise Exception("OpenAPI specification not loaded. Call load_openapi_spec() first.")

    def _get_paths_dict(self) -> dict[str, Any]:
        paths_raw: Any = self.openapi_spec.get('paths', {})
        return cast(dict[str, Any], paths_raw) if isinstance(paths_raw, dict) else {}

    def _format_collection_name(self) -> str:
        version_display = self._format_version_display()
        return f"{self.api_title} {version_display}"

    def _create_auth_folder(self) -> dict[str, Any]:
        return {
            'name': 'Authentication',
            'item': [self._create_auth_request()],
            'description': 'Authentication endpoints'
        }

    def _init_collection(self, collection_name: str) -> dict[str, Any]:
        return {
            'info': {
                'name': collection_name,
                'description': self.openapi_spec.get('info', {}).get('description', ''),
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            'item': [self._create_auth_folder()]
        }

    def _operation_primary_tag(self, operation: dict[str, Any]) -> str:
        tags_raw: Any = operation.get('tags', ['Default'])
        tags: list[str] = [str(t) for t in tags_raw] if isinstance(tags_raw, list) else ['Default']
        return tags[0] if tags else 'Default'

    def _merged_parameters_for_operation(
        self,
        path_item_dict: dict[str, Any],
        operation: dict[str, Any],
    ) -> list[dict[str, Any]]:
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

        return merge_parameters(
            cast(list[dict[str, Any]], path_level_params),
            cast(list[dict[str, Any]], operation_params),
        )

    def _group_requests_by_tag(self, paths: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        endpoint_folders: dict[str, list[dict[str, Any]]] = {}
        methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']

        for path, path_item in paths.items():
            for method in methods:
                if not isinstance(path_item, dict) or method not in path_item:
                    continue

                path_item_dict = cast(dict[str, Any], path_item)
                operation_raw: Any = path_item_dict.get(method)
                if not isinstance(operation_raw, dict):
                    continue
                operation: dict[str, Any] = cast(dict[str, Any], operation_raw)

                tag = self._operation_primary_tag(operation)
                merged_params = self._merged_parameters_for_operation(path_item_dict, operation)
                request_item = self._create_postman_request(path, method, operation, merged_params)
                endpoint_folders.setdefault(tag, []).append(request_item)

        return endpoint_folders

    def _add_endpoint_folders_to_collection(
        self,
        collection: dict[str, Any],
        endpoint_folders: dict[str, list[dict[str, Any]]],
    ) -> None:
        for folder_name, requests in endpoint_folders.items():
            collection['item'].append({
                'name': folder_name,
                'item': requests
            })

    def _prepend_generated_timestamp_to_description(
        self,
        collection: dict[str, Any],
        generated_at: datetime,
    ) -> None:
        human_timestamp = (
            f"{generated_at.strftime('%B')} {generated_at.day}{self._ordinal_suffix(generated_at.day)}, "
            f"{generated_at.year}, {generated_at.strftime('%H:%M:%S')} GMT"
        )
        generated_line = f"Collection generated on {human_timestamp}."

        info_obj_raw: Any = collection.get('info', {})
        info_obj: dict[str, Any] = cast(dict[str, Any], info_obj_raw) if isinstance(info_obj_raw, dict) else {}
        existing_desc = str(info_obj.get('description', '') or '').strip()
        info_obj['description'] = generated_line if not existing_desc else f"{generated_line}\n\n{existing_desc}"
        info_obj['x-api-id'] = self.api_id_slug
        info_obj['x-generated-at'] = self.generated_at_iso
        collection['info'] = info_obj

    def _write_collection_file(
        self,
        collection: dict[str, Any],
        generated_at: datetime,
        collection_name: str,
    ) -> str:
        timestamp = generated_at.strftime('%Y%m%d_%H%M%S')
        filename = f"{sanitize_filename(collection_name)}_{timestamp}_collection.json"
        file_path = self.output_folder / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)

        print(f"Generated collection: {file_path}")
        return str(file_path)

    def generate_collection(self) -> str:
        """
        Generate Postman collection from OpenAPI specification.
        
        Returns:
            Path to generated collection file
        """
        self._require_openapi_loaded()

        paths = self._get_paths_dict()
        collection_name = self._format_collection_name()
        collection = self._init_collection(collection_name)

        endpoint_folders = self._group_requests_by_tag(paths)
        self._add_endpoint_folders_to_collection(collection, endpoint_folders)

        generated_at = datetime.now(timezone.utc)
        self._prepend_generated_timestamp_to_description(collection, generated_at)

        return self._write_collection_file(collection, generated_at, collection_name)

    def _environment_name_base(self) -> str:
        version_prefix = '' if self.api_version.startswith('v') else 'v'
        return f"{self.api_title} {version_prefix}{self.api_version}"

    def _get_x_postman_envs(self) -> dict[str, Any]:
        assert self.openapi_spec is not None
        x_postman_envs_raw: Any = self.openapi_spec.get('x-postman-environments', {})
        return cast(dict[str, Any], x_postman_envs_raw) if isinstance(x_postman_envs_raw, dict) else {}

    def _get_env_config(self, x_postman_envs: dict[str, Any], env_name: str) -> dict[str, str]:
        env_config_raw: Any = x_postman_envs.get(env_name, {})
        return cast(dict[str, str], env_config_raw) if isinstance(env_config_raw, dict) else {}

    def _merge_global_and_env_config(self, env_config: dict[str, str]) -> dict[str, str]:
        return {**self.global_vars, **env_config}

    def _choose_first_server_url(
        self,
        servers: list[Any],
        default_url: str,
        predicate: Any,
    ) -> str:
        for server in servers:
            if not isinstance(server, dict):
                continue
            if predicate(server):
                return str(server.get('url', default_url))
        return default_url

    @staticmethod
    def _is_staging_server(server: dict[str, Any]) -> bool:
        url = str(server.get('url', '') or '').lower()
        desc = str(server.get('description', '') or '').lower()
        return 'stg' in url or 'staging' in desc

    @staticmethod
    def _is_production_server(server: dict[str, Any]) -> bool:
        url = str(server.get('url', '') or '').lower()
        desc = str(server.get('description', '') or '').lower()
        return 'stg' not in url and 'staging' not in desc

    def _select_environment_server_url(self, env_name: str, default_base_url: str) -> str:
        assert self.openapi_spec is not None

        if env_name not in {'staging', 'production'}:
            return default_base_url

        servers_raw: Any = self.openapi_spec.get('servers', [])
        servers: list[Any] = servers_raw if isinstance(servers_raw, list) else []

        if env_name == 'staging':
            return self._choose_first_server_url(servers, default_base_url, self._is_staging_server)

        return self._choose_first_server_url(servers, default_base_url, self._is_production_server)

    def _build_environment_values(
        self,
        env_name: str,
        env_base_url: str,
        merged_config: dict[str, str],
    ) -> list[dict[str, Any]]:
        return [
            {
                'key': 'baseUrl',
                'value': env_base_url,
                'type': 'default',
                'enabled': True,
            },
            {
                'key': 'environment',
                'value': env_name,
                'type': 'default',
                'enabled': True,
            },
            {
                'key': 'tenantId',
                'value': merged_config.get('tenantId', ''),
                'type': 'secret',
                'enabled': True,
            },
            {
                'key': 'clientId',
                'value': merged_config.get('clientId', ''),
                'type': 'secret',
                'enabled': True,
            },
            {
                'key': 'clientSecret',
                'value': merged_config.get('clientSecret', '<replace-with-your-secret>'),
                'type': 'secret',
                'enabled': True,
            },
            {
                'key': 'scope',
                'value': merged_config.get('scope', 'api://.default'),
                'type': 'default',
                'enabled': True,
            },
            {
                'key': 'accessToken',
                'value': '',
                'type': 'secret',
                'enabled': True,
            },
        ]

    @staticmethod
    def _infer_postman_value_type(key: str) -> str:
        return 'secret' if re.search(r'(secret|token|key|password)', key, flags=re.IGNORECASE) else 'default'

    def _append_additional_environment_values(
        self,
        values: list[dict[str, Any]],
        merged_config: dict[str, str],
    ) -> None:
        existing_keys = {v.get('key') for v in values if isinstance(v, dict)}
        for key in sorted(merged_config.keys()):
            if key in existing_keys:
                continue
            values.append(
                {
                    'key': key,
                    'value': merged_config.get(key, ''),
                    'type': self._infer_postman_value_type(key),
                    'enabled': True,
                }
            )

    def _write_environment_file(
        self,
        environment: dict[str, Any],
        filename_base: str,
        timestamp: str,
        env_name: str,
    ) -> str:
        filename = f"{filename_base}_{timestamp}_{env_name}_environment.json"
        file_path = self.output_folder / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(environment, f, indent=2, ensure_ascii=False)

        print(f"Generated environment: {file_path}")
        return str(file_path)

    def generate_environment_files(self) -> list[str]:
        """
        Generate Postman environment files for each specified environment.
        
        Returns:
            List of paths to generated environment files
        """
        self._require_openapi_loaded()

        base_url = self._get_base_url()
        generated_files: list[str] = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        name_base = self._environment_name_base()
        filename_base = sanitize_filename(name_base)
        x_postman_envs = self._get_x_postman_envs()

        assert self.environments is not None
        for env_name in self.environments:
            env_config = self._get_env_config(x_postman_envs, env_name)
            merged_config = self._merge_global_and_env_config(env_config)

            server_url = self._select_environment_server_url(env_name, base_url)
            env_base_url = self._append_version_to_server_url(str(server_url))

            values = self._build_environment_values(env_name, env_base_url, merged_config)
            self._append_additional_environment_values(values, merged_config)

            environment: dict[str, Any] = {
                'id': f"{env_name}-{timestamp}",
                'name': f"{name_base} - {env_name.capitalize()}",
                'x-api-id': self.api_id_slug,
                'x-generated-at': self.generated_at_iso,
                'values': values,
                '_postman_variable_scope': 'environment',
            }

            generated_files.append(
                self._write_environment_file(environment, filename_base, timestamp, env_name)
            )

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
