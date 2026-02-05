"""Utility functions for the Postman project type module."""

import re
from typing import Any, Optional
from urllib.parse import urlparse


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    return filename


def _strip_alpha_dash_suffix(name: str) -> str:
    if " - " not in name:
        return name

    base, suffix = name.rsplit(" - ", 1)
    suffix_stripped = suffix.strip()
    if suffix_stripped and suffix_stripped.replace(" ", "").isalpha():
        return base.strip()
    return name


def _is_version_token(token: str) -> bool:
    token = token.strip()
    if len(token) < 2 or token[0].lower() != "v":
        return False

    rest = token[1:]
    if not rest or not rest[0].isdigit():
        return False

    return all(ch.isalnum() or ch in ".-" for ch in rest)


def strip_version_suffix(name: str, *, strip_dash_suffix: bool = False) -> str:
    """Strip common trailing version suffixes from a resource name.

    Intended for Postman resource names such as:
    - "Test API v1-rev0"
    - "Test API v1-rev0 v1.0.0"
    - "Test API v2-rev1 v2.5.0 - Development"

    This function intentionally avoids complex regular expressions.
    """

    result = str(name or "").strip()
    if not result:
        return result

    if strip_dash_suffix:
        result = _strip_alpha_dash_suffix(result)

    tokens = result.split()
    while tokens and _is_version_token(tokens[-1]):
        tokens.pop()

    return " ".join(tokens).strip()


def is_url(path: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        path: String to check
        
    Returns:
        True if the string is a URL, False otherwise
    """
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_path_variables(path: str) -> list[str]:
    """
    Extract path variables from an OpenAPI path template.
    
    Args:
        path: OpenAPI path template (e.g., "/users/{userId}/posts/{postId}")
        
    Returns:
        List of variable names
    """
    return re.findall(r'\{([^}]+)\}', path)


def convert_path_to_postman(path: str) -> str:
    """
    Convert OpenAPI path template to Postman format.
    
    Args:
        path: OpenAPI path template (e.g., "/users/{userId}")
        
    Returns:
        Postman-formatted path (e.g., "/users/:userId")
    """
    return re.sub(r'\{([^}]+)\}', r':\1', path)


def get_response_example(responses: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Extract example response from OpenAPI responses object.
    
    Args:
        responses: OpenAPI responses object
        
    Returns:
        Example response or None
    """
    # Try to find a successful JSON response
    for status_code in ['200', '201', '202', '204']:
        response = responses.get(status_code)
        if not isinstance(response, dict):
            continue

        content = response.get('content')
        if not isinstance(content, dict):
            continue

        json_content = content.get('application/json')
        if not isinstance(json_content, dict):
            continue

        example = json_content.get('example')
        if example is not None:
            return example

        examples = json_content.get('examples')
        if not isinstance(examples, dict) or not examples:
            continue

        first_example = next(iter(examples.values()), None)
        if isinstance(first_example, dict) and 'value' in first_example:
            return first_example['value']

    return None


def merge_parameters(path_params: list[dict[str, Any]], operation_params: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Merge path-level and operation-level parameters.
    Operation parameters override path parameters with the same name.
    
    Args:
        path_params: Parameters defined at path level
        operation_params: Parameters defined at operation level
        
    Returns:
        Merged list of parameters
    """
    # Create a dictionary of path parameters
    params_dict: dict[str, dict[str, Any]] = {str(param.get('name', '')): param for param in path_params}
    
    # Override with operation parameters
    for param in operation_params:
        params_dict[str(param.get('name', ''))] = param
    
    return list(params_dict.values())


def get_default_value_for_type(param_type: str) -> Any:
    """
    Get default value based on parameter type.
    
    Args:
        param_type: OpenAPI parameter type
        
    Returns:
        Default value for the type
    """
    type_defaults = {
        'string': '',
        'integer': 0,
        'number': 0.0,
        'boolean': False,
        'array': [],
        'object': {}
    }
    
    return type_defaults.get(param_type, '')


def validate_openapi_version(version: str) -> bool:
    """
    Validate if the OpenAPI version is supported.
    
    Args:
        version: OpenAPI version string
        
    Returns:
        True if version is supported, False otherwise
    """
    supported_versions = ['3.0.0', '3.0.1', '3.0.2', '3.0.3', '3.1.0']
    
    # Extract major.minor.patch
    version_match = re.match(r'(\d+\.\d+\.\d+)', version)
    if version_match:
        version = version_match.group(1)
    
    return version in supported_versions


def generate_postman_variable(key: str, value: Any, var_type: str = 'default', enabled: bool = True) -> dict[str, Any]:
    """
    Generate a Postman environment variable object.
    
    Args:
        key: Variable key
        value: Variable value
        var_type: Variable type ('default' or 'secret')
        enabled: Whether the variable is enabled
        
    Returns:
        Postman variable object
    """
    return {
        'key': key,
        'value': value,
        'type': var_type,
        'enabled': enabled
    }
