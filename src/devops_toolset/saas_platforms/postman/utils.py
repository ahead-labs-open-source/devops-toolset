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
    # Try to find successful response
    for status_code in ['200', '201', '202', '204']:
        if status_code in responses:
            response = responses[status_code]
            content = response.get('content', {})
            
            if 'application/json' in content:
                json_content = content['application/json']
                
                # Check for example
                if 'example' in json_content:
                    return json_content['example']
                
                # Check for examples
                if 'examples' in json_content:
                    examples = json_content['examples']
                    first_example = next(iter(examples.values()), None)
                    if first_example and 'value' in first_example:
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
