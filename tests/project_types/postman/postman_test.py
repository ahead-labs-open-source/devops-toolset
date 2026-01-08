"""
Unit tests for the Postman project type module.
Tests the OpenAPI to Postman converter functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from devops_toolset.project_types.postman.openapi_to_postman import OpenAPIToPostmanConverter
from devops_toolset.project_types.postman.deploy_to_workspace import (
    _collection_name_from_export,
    _environment_name_from_export,
    _wrap_collection_for_api,
    _wrap_environment_for_api,
    get_workspace_assets,
    upsert_collection,
    upsert_environment,
)
from devops_toolset.project_types.postman.utils import (
    sanitize_filename,
    is_url,
    extract_path_variables,
    convert_path_to_postman,
    validate_openapi_version,
    generate_postman_variable
)


class TestOpenAPIToPostmanConverter:
    """Test cases for OpenAPIToPostmanConverter class."""

    @pytest.fixture
    def sample_openapi_spec(self):
        """Sample OpenAPI specification for testing."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "A test API"
            },
            "servers": [
                {
                    "url": "https://api.example.com/v1"
                }
            ],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "operationId": "listUsers",
                        "tags": ["Users"],
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "description": "Maximum number of users to return",
                                "required": False,
                                "schema": {
                                    "type": "integer"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Create user",
                        "operationId": "createUser",
                        "tags": ["Users"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string"}
                                        }
                                    },
                                    "example": {
                                        "name": "John Doe",
                                        "email": "john@example.com"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "User created"
                            }
                        }
                    }
                },
                "/users/{userId}": {
                    "get": {
                        "summary": "Get user by ID",
                        "operationId": "getUserById",
                        "tags": ["Users"],
                        "parameters": [
                            {
                                "name": "userId",
                                "in": "path",
                                "required": True,
                                "schema": {
                                    "type": "string"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response"
                            }
                        }
                    }
                }
            }
        }

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create a temporary output directory."""
        output_dir = tmp_path / "postman_output"
        output_dir.mkdir()
        return output_dir

    def test_converter_initialization(self, temp_output_dir):
        """Test converter initialization."""
        converter = OpenAPIToPostmanConverter(
            openapi_source="test.json",
            output_folder=str(temp_output_dir),
            environments=["staging", "production"]
        )
        
        assert converter.openapi_source == "test.json"
        assert converter.output_folder == temp_output_dir
        assert converter.environments == ["staging", "production"]
        assert temp_output_dir.exists()

    def test_load_openapi_spec_from_dict(self, temp_output_dir, sample_openapi_spec):
        """Test loading OpenAPI spec from dictionary."""
        # Create a temporary JSON file
        spec_file = temp_output_dir / "test_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(sample_openapi_spec, f)
        
        converter = OpenAPIToPostmanConverter(
            openapi_source=str(spec_file),
            output_folder=str(temp_output_dir),
            environments=["test"]
        )
        
        converter.load_openapi_spec()
        
        assert converter.openapi_spec == sample_openapi_spec
        assert converter.api_title == "Test API"
        assert converter.api_version == "1.0.0"

    def test_get_base_url(self, temp_output_dir, sample_openapi_spec):
        """Test extracting base URL from OpenAPI spec."""
        spec_file = temp_output_dir / "test_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(sample_openapi_spec, f)
        
        converter = OpenAPIToPostmanConverter(
            openapi_source=str(spec_file),
            output_folder=str(temp_output_dir),
            environments=["test"]
        )
        
        converter.load_openapi_spec()
        base_url = converter._get_base_url()
        
        assert base_url == "https://api.example.com/v1"

    def test_convert_parameters(self, temp_output_dir):
        """Test parameter conversion."""
        converter = OpenAPIToPostmanConverter(
            openapi_source="test.json",
            output_folder=str(temp_output_dir),
            environments=["test"]
        )
        
        parameters = [
            {
                "name": "limit",
                "in": "query",
                "description": "Limit results",
                "required": False
            },
            {
                "name": "Authorization",
                "in": "header",
                "description": "Auth token",
                "required": True
            },
            {
                "name": "userId",
                "in": "path",
                "required": True
            }
        ]
        
        result = converter._convert_parameters(parameters)
        
        assert len(result['query']) == 1
        assert len(result['header']) == 1
        assert len(result['path']) == 1
        assert result['query'][0]['key'] == 'limit'
        assert result['header'][0]['key'] == 'Authorization'
        assert result['path'][0]['key'] == 'userId'

    def test_convert_request_body_json(self, temp_output_dir):
        """Test converting JSON request body."""
        converter = OpenAPIToPostmanConverter(
            openapi_source="test.json",
            output_folder=str(temp_output_dir),
            environments=["test"]
        )
        
        request_body = {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object"
                    },
                    "example": {
                        "name": "Test",
                        "value": 123
                    }
                }
            }
        }
        
        result = converter._convert_request_body(request_body)
        
        assert result is not None
        assert result['mode'] == 'raw'
        assert 'raw' in result
        assert 'Test' in result['raw']

    def test_create_auth_request(self, temp_output_dir):
        """Test creation of JWT auth request."""
        converter = OpenAPIToPostmanConverter(
            openapi_source="test.json",
            output_folder=str(temp_output_dir),
            environments=["test"]
        )
        
        auth_request = converter._create_auth_request()
        
        assert auth_request['name'] == 'Get JWT Token'
        assert auth_request['request']['method'] == 'POST'
        assert 'login.microsoftonline.com' in str(auth_request['request']['url'])
        
        # Check body parameters
        body_params = auth_request['request']['body']['urlencoded']
        param_keys = [p['key'] for p in body_params]
        
        assert 'grant_type' in param_keys
        assert 'client_id' in param_keys
        assert 'client_secret' in param_keys
        assert 'scope' in param_keys

    def test_generate_collection(self, temp_output_dir, sample_openapi_spec):
        """Test collection generation."""
        spec_file = temp_output_dir / "test_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(sample_openapi_spec, f)
        
        converter = OpenAPIToPostmanConverter(
            openapi_source=str(spec_file),
            output_folder=str(temp_output_dir),
            environments=["test"]
        )
        
        converter.load_openapi_spec()
        collection_path = converter.generate_collection()
        
        assert Path(collection_path).exists()
        
        # Load and verify collection
        with open(collection_path, 'r') as f:
            collection = json.load(f)
        
        assert 'info' in collection
        assert collection['info']['name'] == "Test API v1.0.0"
        assert 'item' in collection
        assert len(collection['item']) > 0  # Should have at least auth folder

        # Verify a templated path is converted to Postman format (:var)
        users_folder = next((f for f in collection['item'] if f.get('name') == 'Users'), None)
        assert users_folder is not None
        requests = users_folder.get('item', [])
        get_user = next((r for r in requests if r.get('name') == 'Get user by ID'), None)
        assert get_user is not None
        assert get_user['request']['url']['raw'].endswith('/users/:userId')

        # Verify query parameters are preserved
        list_users = next((r for r in requests if r.get('name') == 'List users'), None)
        assert list_users is not None
        query_keys = [q.get('key') for q in list_users['request']['url'].get('query', [])]
        assert 'limit' in query_keys

    def test_generate_environment_files(self, temp_output_dir, sample_openapi_spec):
        """Test environment file generation."""
        spec_file = temp_output_dir / "test_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(sample_openapi_spec, f)
        
        converter = OpenAPIToPostmanConverter(
            openapi_source=str(spec_file),
            output_folder=str(temp_output_dir),
            environments=["staging", "production"]
        )
        
        converter.load_openapi_spec()
        env_files = converter.generate_environment_files()
        
        assert len(env_files) == 2
        
        # Verify files exist
        for env_file in env_files:
            assert Path(env_file).exists()
            
            # Load and verify environment
            with open(env_file, 'r') as f:
                env = json.load(f)
            
            assert 'name' in env
            assert 'values' in env
            
            # Check required variables
            var_keys = [v['key'] for v in env['values']]
            assert 'baseUrl' in var_keys
            assert 'tenantId' in var_keys
            assert 'clientId' in var_keys
            assert 'clientSecret' in var_keys

    def test_generate_environment_files_includes_extra_x_postman_variables(self, temp_output_dir, sample_openapi_spec):
        """Extra variables in x-postman-environments should be included in environment output."""
        spec = dict(sample_openapi_spec)
        spec['x-postman-environments'] = {
            '_global': {
                'tenantId': 'tenant-1'
            },
            'staging': {
                'ocpApimSubscriptionKey': 'sub-key-1',
                'clientId': 'client-1',
                'clientSecret': 'secret-1',
                'scope': 'api://client-1/.default'
            }
        }

        spec_file = temp_output_dir / "test_spec_with_postman_envs.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f)

        converter = OpenAPIToPostmanConverter(
            openapi_source=str(spec_file),
            output_folder=str(temp_output_dir),
            environments=["staging"]
        )

        converter.load_openapi_spec()
        env_files = converter.generate_environment_files()
        assert len(env_files) == 1

        with open(env_files[0], 'r') as f:
            env = json.load(f)

        values = {v['key']: v for v in env.get('values', [])}
        assert 'ocpApimSubscriptionKey' in values
        assert values['ocpApimSubscriptionKey']['value'] == 'sub-key-1'

    def test_security_schemes_generate_headers(self, temp_output_dir, sample_openapi_spec):
        """apiKey/oAuth2 security schemes should translate to Postman headers."""
        spec = dict(sample_openapi_spec)
        spec['components'] = {
            'securitySchemes': {
                'subscriptionKey': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'Ocp-Apim-Subscription-Key',
                },
                'oauth2': {
                    'type': 'oauth2',
                    'flows': {
                        'clientCredentials': {
                            'tokenUrl': 'https://login.example.com/token',
                            'scopes': {}
                        }
                    }
                }
            }
        }
        spec['security'] = [{'subscriptionKey': [], 'oauth2': []}]

        spec_file = temp_output_dir / "test_spec_with_security.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f)

        converter = OpenAPIToPostmanConverter(
            openapi_source=str(spec_file),
            output_folder=str(temp_output_dir),
            environments=["test"]
        )
        converter.load_openapi_spec()

        collection_path = converter.generate_collection()
        with open(collection_path, 'r') as f:
            collection = json.load(f)

        users_folder = next((it for it in collection.get('item', []) if it.get('name') == 'Users'), None)
        assert users_folder is not None
        any_request = next((r for r in users_folder.get('item', []) if isinstance(r, dict) and 'request' in r), None)
        assert any_request is not None

        headers = any_request['request'].get('header', [])
        header_map = {h.get('key'): h.get('value') for h in headers}
        assert header_map.get('Ocp-Apim-Subscription-Key') == '{{ocpApimSubscriptionKey}}'
        assert header_map.get('Authorization') == 'Bearer {{accessToken}}'


class TestUtils:
    """Test cases for utility functions."""

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("Test API v1.0") == "Test_API_v1.0"
        assert sanitize_filename("API/Test:File") == "APITestFile"
        assert sanitize_filename("Multiple   Spaces") == "Multiple_Spaces"

    def test_is_url(self):
        """Test URL detection."""
        assert is_url("https://example.com/api") is True
        assert is_url("http://localhost:8080") is True
        assert is_url("/local/path/file.json") is False
        assert is_url("file.json") is False

    def test_extract_path_variables(self):
        """Test path variable extraction."""
        path = "/users/{userId}/posts/{postId}"
        variables = extract_path_variables(path)
        
        assert len(variables) == 2
        assert "userId" in variables
        assert "postId" in variables

    def test_convert_path_to_postman(self):
        """Test path conversion to Postman format."""
        openapi_path = "/users/{userId}/posts/{postId}"
        postman_path = convert_path_to_postman(openapi_path)
        
        assert postman_path == "/users/:userId/posts/:postId"

    def test_validate_openapi_version(self):
        """Test OpenAPI version validation."""
        assert validate_openapi_version("3.0.0") is True
        assert validate_openapi_version("3.0.1") is True
        assert validate_openapi_version("3.1.0") is True
        assert validate_openapi_version("2.0.0") is False
        assert validate_openapi_version("4.0.0") is False

    def test_generate_postman_variable(self):
        """Test Postman variable generation."""
        var = generate_postman_variable("apiKey", "12345", "secret", True)
        
        assert var['key'] == "apiKey"
        assert var['value'] == "12345"
        assert var['type'] == "secret"
        assert var['enabled'] is True


class TestIntegration:
    """Integration tests for the complete conversion process."""

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create a temporary output directory."""
        output_dir = tmp_path / "integration_test"
        output_dir.mkdir()
        return output_dir

    def test_full_conversion_workflow(self, temp_output_dir, sample_openapi_spec):
        """Test the complete conversion workflow."""
        # Create OpenAPI spec file
        spec_file = temp_output_dir / "api_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(sample_openapi_spec, f)
        
        # Create converter
        converter = OpenAPIToPostmanConverter(
            openapi_source=str(spec_file),
            output_folder=str(temp_output_dir / "output"),
            environments=["dev", "prod"]
        )
        
        # Execute conversion
        result = converter.convert()
        
        # Verify results
        assert 'collection' in result
        assert 'environments' in result
        assert 'api_version' in result
        assert 'api_title' in result
        
        assert result['api_title'] == "Test API"
        assert result['api_version'] == "1.0.0"
        assert len(result['environments']) == 2
        
        # Verify all files exist
        assert Path(result['collection']).exists()
        for env_file in result['environments']:
            assert Path(env_file).exists()

    @pytest.fixture
    def sample_openapi_spec(self):
        """Sample OpenAPI specification for integration testing."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "A test API for integration testing"
            },
            "servers": [
                {
                    "url": "https://api.example.com/v1"
                }
            ],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "operationId": "listUsers",
                        "tags": ["Users"],
                        "responses": {
                            "200": {
                                "description": "Successful response"
                            }
                        }
                    }
                }
            }
        }


class TestPostmanDeployToWorkspace:
    def test_collection_name_from_export(self):
        assert _collection_name_from_export({"info": {"name": "My API"}}) == "My API"

    def test_environment_name_from_export_export_shape(self):
        assert _environment_name_from_export({"name": "My Env", "values": []}) == "My Env"

    def test_environment_name_from_export_api_shape(self):
        assert _environment_name_from_export({"environment": {"name": "My Env", "values": []}}) == "My Env"

    def test_wrap_collection_for_api(self):
        wrapped = _wrap_collection_for_api({"info": {"name": "My API"}, "item": []})
        assert "collection" in wrapped
        assert wrapped["collection"]["info"]["name"] == "My API"

    def test_wrap_environment_for_api(self):
        wrapped = _wrap_environment_for_api({"name": "My Env", "values": []})
        assert "environment" in wrapped
        assert wrapped["environment"]["name"] == "My Env"

    @patch("devops_toolset.project_types.postman.deploy_to_workspace.requests.request")
    def test_get_workspace_assets_maps_by_name(self, request_mock: Mock):
        resp = Mock()
        resp.ok = True
        resp.status_code = 200
        resp.json.return_value = {
            "workspace": {
                "collections": [{"name": "C1", "uid": "c-uid"}],
                "environments": [{"name": "E1", "uid": "e-uid"}],
            }
        }
        request_mock.return_value = resp

        assets = get_workspace_assets("https://api.postman.com", "k", "w")
        assert assets.collections_by_name["C1"] == "c-uid"
        assert assets.environments_by_name["E1"] == "e-uid"

    @patch("devops_toolset.project_types.postman.deploy_to_workspace.requests.request")
    def test_upsert_collection_updates_when_exists(self, request_mock: Mock):
        # GET workspace then PUT collection
        resp_get = Mock(ok=True, status_code=200)
        resp_get.json.return_value = {"workspace": {"collections": [{"name": "C1", "uid": "c-uid"}]}}

        resp_put = Mock(ok=True, status_code=200)
        resp_put.json.return_value = {"collection": {"uid": "c-uid"}}

        request_mock.side_effect = [resp_get, resp_put]

        action, uid = upsert_collection(
            "https://api.postman.com",
            "k",
            "w",
            {"info": {"name": "C1"}, "item": []},
        )
        assert action == "updated"
        assert uid == "c-uid"

        # Verify last call is PUT /collections/c-uid
        last_call = request_mock.call_args_list[-1].kwargs
        assert last_call["method"] == "PUT"
        assert last_call["url"].endswith("/collections/c-uid")

    @patch("devops_toolset.project_types.postman.deploy_to_workspace.requests.request")
    def test_upsert_environment_creates_when_missing(self, request_mock: Mock):
        # GET workspace then POST environment
        resp_get = Mock(ok=True, status_code=200)
        resp_get.json.return_value = {"workspace": {"environments": []}}

        resp_post = Mock(ok=True, status_code=200)
        resp_post.json.return_value = {"environment": {"uid": "e-new"}}

        request_mock.side_effect = [resp_get, resp_post]

        action, name, uid = upsert_environment(
            "https://api.postman.com",
            "k",
            "w",
            {"name": "Env1", "values": []},
        )
        assert action == "created"
        assert name == "Env1"
        assert uid == "e-new"

        last_call = request_mock.call_args_list[-1].kwargs
        assert last_call["method"] == "POST"
        assert last_call["url"].endswith("/environments")
        assert last_call["params"]["workspace"] == "w"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
