"""
OpenAPI to Postman Collection Converter

This module converts OpenAPI 3.0 specifications (YAML or JSON) to Postman Collection v2.1 format.
It also generates environment files for different deployment environments.
"""

import json
import yaml
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import urllib.request


class OpenAPIToPostmanConverter:
    """Converts OpenAPI specifications to Postman collections and environment files."""

    def __init__(self, openapi_source: str, output_folder: str, environments: List[str]):
        """
        Initialize the converter.

        Args:
            openapi_source: Path to OpenAPI file or URL
            output_folder: Directory where generated files will be saved
            environments: List of environment names (e.g., ["staging", "production"])
        """
        self.openapi_source = openapi_source
        self.output_folder = Path(output_folder)
        self.environments = environments
        self.openapi_spec: Dict[str, Any] = {}
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
            if self.openapi_source.startswith(('http://', 'https://')):
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
            
            print(f"Loaded OpenAPI spec: {self.api_title} v{self.api_version}")
            
        except Exception as e:
            raise Exception(f"Error loading OpenAPI specification: {str(e)}")

    def _get_base_url(self) -> str:
        """
        Extract base URL from OpenAPI servers section.
        
        Returns:
            Base URL string with {{baseUrl}} variable placeholder
        """
        servers = self.openapi_spec.get('servers', [])
        if servers:
            return servers[0].get('url', '{{baseUrl}}')
        return '{{baseUrl}}'

    def _convert_parameters(self, parameters: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Convert OpenAPI parameters to Postman format.
        
        Args:
            parameters: List of OpenAPI parameter objects
            
        Returns:
            Dictionary with 'query', 'header', and 'path' parameter lists
        """
        result = {
            'query': [],
            'header': [],
            'path': []
        }
        
        for param in parameters:
            param_in = param.get('in', 'query')
            postman_param = {
                'key': param.get('name', ''),
                'value': '',
                'description': param.get('description', ''),
                'disabled': not param.get('required', False)
            }
            
            if param_in in result:
                result[param_in].append(postman_param)
        
        return result

    def _convert_request_body(self, request_body: Optional[Dict]) -> Optional[Dict]:
        """
        Convert OpenAPI request body to Postman body format.
        
        Args:
            request_body: OpenAPI requestBody object
            
        Returns:
            Postman body object or None
        """
        if not request_body:
            return None
        
        content = request_body.get('content', {})
        
        # Prefer JSON content
        if 'application/json' in content:
            schema = content['application/json'].get('schema', {})
            example = content['application/json'].get('example', {})
            
            return {
                'mode': 'raw',
                'raw': json.dumps(example if example else schema, indent=2),
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

    def _create_postman_request(self, path: str, method: str, operation: Dict, base_url: str) -> Dict:
        """
        Create a Postman request item from OpenAPI operation.
        
        Args:
            path: API endpoint path
            method: HTTP method (GET, POST, etc.)
            operation: OpenAPI operation object
            base_url: Base URL for the API
            
        Returns:
            Postman request item
        """
        # Convert path parameters to Postman format
        postman_path = path
        parameters = operation.get('parameters', [])
        param_dict = self._convert_parameters(parameters)
        
        # Build URL object
        url_parts = base_url.split('/')
        path_parts = [p for p in postman_path.split('/') if p]
        
        url_obj = {
            'raw': f"{base_url}{postman_path}",
            'host': url_parts[:3] if len(url_parts) >= 3 else ['{{baseUrl}}'],
            'path': path_parts,
            'query': param_dict['query']
        }
        
        # Build request object
        request = {
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

    def _create_auth_request(self) -> Dict:
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
            'response': []
        }

    def generate_collection(self) -> str:
        """
        Generate Postman collection from OpenAPI specification.
        
        Returns:
            Path to generated collection file
        """
        if not self.openapi_spec:
            raise Exception("OpenAPI specification not loaded. Call load_openapi_spec() first.")
        
        base_url = self._get_base_url()
        paths = self.openapi_spec.get('paths', {})
        
        # Create authentication folder
        auth_folder = {
            'name': 'Authentication',
            'item': [self._create_auth_request()],
            'description': 'Authentication endpoints'
        }
        
        # Create collection structure
        collection = {
            'info': {
                'name': f"{self.api_title} v{self.api_version}",
                'description': self.openapi_spec.get('info', {}).get('description', ''),
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            'item': [auth_folder],
            'variable': [
                {
                    'key': 'baseUrl',
                    'value': base_url,
                    'type': 'string'
                },
                {
                    'key': 'tenantId',
                    'value': '',
                    'type': 'string'
                },
                {
                    'key': 'clientId',
                    'value': '',
                    'type': 'string'
                },
                {
                    'key': 'clientSecret',
                    'value': '',
                    'type': 'string'
                },
                {
                    'key': 'scope',
                    'value': '',
                    'type': 'string'
                }
            ]
        }
        
        # Group endpoints by tags or create flat structure
        endpoint_folders: Dict[str, List[Dict]] = {}
        
        for path, path_item in paths.items():
            for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                if method in path_item:
                    operation = path_item[method]
                    tags = operation.get('tags', ['Default'])
                    tag = tags[0] if tags else 'Default'
                    
                    if tag not in endpoint_folders:
                        endpoint_folders[tag] = []
                    
                    request_item = self._create_postman_request(path, method, operation, base_url)
                    endpoint_folders[tag].append(request_item)
        
        # Add folders to collection
        for folder_name, requests in endpoint_folders.items():
            collection['item'].append({
                'name': folder_name,
                'item': requests
            })
        
        # Generate filename with version and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.api_title.replace(' ', '_')}_v{self.api_version}_{timestamp}_collection.json"
        file_path = self.output_folder / filename
        
        # Write collection file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        print(f"Generated collection: {file_path}")
        return str(file_path)

    def generate_environment_files(self) -> List[str]:
        """
        Generate Postman environment files for each specified environment.
        
        Returns:
            List of paths to generated environment files
        """
        if not self.openapi_spec:
            raise Exception("OpenAPI specification not loaded. Call load_openapi_spec() first.")
        
        base_url = self._get_base_url()
        generated_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for env_name in self.environments:
            environment = {
                'id': f"{env_name}-{timestamp}",
                'name': f"{self.api_title} - {env_name.capitalize()}",
                'values': [
                    {
                        'key': 'baseUrl',
                        'value': base_url.replace('{{baseUrl}}', f'https://api-{env_name}.example.com'),
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
                        'value': '',
                        'type': 'secret',
                        'enabled': True
                    },
                    {
                        'key': 'clientId',
                        'value': '',
                        'type': 'secret',
                        'enabled': True
                    },
                    {
                        'key': 'clientSecret',
                        'value': '',
                        'type': 'secret',
                        'enabled': True
                    },
                    {
                        'key': 'scope',
                        'value': 'api://.default',
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
            
            # Generate filename with version and timestamp
            filename = f"{self.api_title.replace(' ', '_')}_v{self.api_version}_{timestamp}_{env_name}_environment.json"
            file_path = self.output_folder / filename
            
            # Write environment file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(environment, f, indent=2, ensure_ascii=False)
            
            generated_files.append(str(file_path))
            print(f"Generated environment: {file_path}")
        
        return generated_files

    def convert(self) -> Dict[str, Any]:
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
        
        result = {
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


def main():
    """
    Main function for command-line usage.
    Example usage demonstrating the converter with the Petstore API.
    """
    # Example configuration
    openapi_url = "https://petstore3.swagger.io/api/v3/openapi.json"
    output_folder = "./postman_output"
    environments = ["staging", "production"]
    
    # Create converter instance
    converter = OpenAPIToPostmanConverter(
        openapi_source=openapi_url,
        output_folder=output_folder,
        environments=environments
    )
    
    # Execute conversion
    try:
        result = converter.convert()
        print("\nGenerated files:")
        print(f"  Collection: {result['collection']}")
        for env_file in result['environments']:
            print(f"  Environment: {env_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
