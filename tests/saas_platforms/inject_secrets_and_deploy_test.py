"""Unit tests for inject_secrets_and_deploy module"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import devops_toolset.saas_platforms.postman.inject_secrets_and_deploy as sut


# region mask_secret_for_github()

def test_mask_secret_for_github_emits_workflow_command(capsys):
    """Emits GitHub Actions ::add-mask:: command"""
    
    # Arrange
    secret = "my-secret-value"
    
    # Act
    sut.mask_secret_for_github(secret)
    
    # Assert
    captured = capsys.readouterr()
    assert "::add-mask::my-secret-value" in captured.out


def test_mask_secret_for_github_handles_empty_secret(capsys):
    """Handles empty secret gracefully"""
    
    # Arrange
    secret = ""
    
    # Act
    sut.mask_secret_for_github(secret)
    
    # Assert
    captured = capsys.readouterr()
    assert captured.out == ""

# endregion


# region inject_secrets_into_environment()

def test_inject_secrets_into_environment_creates_values_array_if_missing():
    """Creates values array if it doesn't exist"""
    
    # Arrange
    env_json = {}
    secrets = {"key1": ("value1", "secret")}
    
    # Act
    result = sut.inject_secrets_into_environment(env_json, secrets)
    
    # Assert
    assert "values" in result
    assert isinstance(result["values"], list)


def test_inject_secrets_into_environment_adds_new_entries():
    """Adds new secret entries"""
    
    # Arrange
    env_json = {"values": []}
    secrets = {
        "ocpApimSubscriptionKey": ("api-key-123", "secret"),
        "tenantId": ("tenant-guid", "default")
    }
    
    # Act
    result = sut.inject_secrets_into_environment(env_json, secrets)
    
    # Assert
    assert len(result["values"]) == 2
    assert any(
        v["key"] == "ocpApimSubscriptionKey" 
        and v["value"] == "api-key-123" 
        and v["type"] == "secret" 
        and v["enabled"] is True
        for v in result["values"]
    )
    assert any(
        v["key"] == "tenantId" 
        and v["value"] == "tenant-guid" 
        and v["type"] == "default"
        for v in result["values"]
    )


def test_inject_secrets_into_environment_updates_existing_entries():
    """Updates existing entries instead of duplicating"""
    
    # Arrange
    env_json = {
        "values": [
            {"key": "ocpApimSubscriptionKey", "value": "old-value", "type": "default", "enabled": False}
        ]
    }
    secrets = {"ocpApimSubscriptionKey": ("new-value", "secret")}
    
    # Act
    result = sut.inject_secrets_into_environment(env_json, secrets)
    
    # Assert
    assert len(result["values"]) == 1
    assert result["values"][0]["key"] == "ocpApimSubscriptionKey"
    assert result["values"][0]["value"] == "new-value"
    assert result["values"][0]["type"] == "secret"
    assert result["values"][0]["enabled"] is True


def test_inject_secrets_into_environment_preserves_other_entries():
    """Preserves other entries that are not being updated"""
    
    # Arrange
    env_json = {
        "values": [
            {"key": "baseUrl", "value": "https://api.example.com", "type": "default", "enabled": True},
            {"key": "apiVersion", "value": "v1", "type": "default", "enabled": True}
        ]
    }
    secrets = {"ocpApimSubscriptionKey": ("api-key", "secret")}
    
    # Act
    result = sut.inject_secrets_into_environment(env_json, secrets)
    
    # Assert
    assert len(result["values"]) == 3
    assert any(v["key"] == "baseUrl" for v in result["values"])
    assert any(v["key"] == "apiVersion" for v in result["values"])
    assert any(v["key"] == "ocpApimSubscriptionKey" for v in result["values"])

# endregion


# region validate_secrets()

def test_validate_secrets_raises_on_missing_apim_key():
    """Raises ValueError if APIM API key is missing"""
    
    # Arrange
    apim_api_key = None
    client_secret = "secret"
    
    # Act & Assert
    with pytest.raises(ValueError, match="APIM_API_KEY"):
        sut.validate_secrets(apim_api_key, client_secret)


def test_validate_secrets_raises_on_empty_apim_key():
    """Raises ValueError if APIM API key is empty"""
    
    # Arrange
    apim_api_key = ""
    client_secret = "secret"
    
    # Act & Assert
    with pytest.raises(ValueError, match="APIM_API_KEY"):
        sut.validate_secrets(apim_api_key, client_secret)


def test_validate_secrets_raises_on_missing_client_secret():
    """Raises ValueError if client secret is missing"""
    
    # Arrange
    apim_api_key = "key"
    client_secret = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="ARM_CLIENT_SECRET"):
        sut.validate_secrets(apim_api_key, client_secret)


def test_validate_secrets_raises_on_empty_client_secret():
    """Raises ValueError if client secret is empty"""
    
    # Arrange
    apim_api_key = "key"
    client_secret = ""
    
    # Act & Assert
    with pytest.raises(ValueError, match="ARM_CLIENT_SECRET"):
        sut.validate_secrets(apim_api_key, client_secret)


def test_validate_secrets_passes_with_valid_secrets():
    """Passes validation with valid secrets"""
    
    # Arrange
    apim_api_key = "valid-key"
    client_secret = "valid-secret"
    
    # Act & Assert (should not raise)
    sut.validate_secrets(apim_api_key, client_secret)

# endregion


# region main()

@patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy.upsert_collection")
@patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy.upsert_environment")
@patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy._load_json_file")
def test_main_loads_and_deploys_successfully(
    load_json_mock, upsert_env_mock, upsert_coll_mock, tmp_path
):
    """Successfully loads files and deploys to Postman"""
    
    # Arrange
    collection_path = tmp_path / "collection.json"
    env_path = tmp_path / "environment.json"
    collection_path.write_text("{}", encoding='utf-8')
    env_path.write_text("{}", encoding='utf-8')
    
    load_json_mock.side_effect = [
        {"info": {"name": "Test Collection"}},  # collection
        {"name": "Test Environment", "values": []}  # environment
    ]
    upsert_coll_mock.return_value = ("created", "coll-uid-123")
    upsert_env_mock.return_value = ("created", "Test Environment", "env-uid-456")
    
    argv = [
        "--collection", str(collection_path),
        "--environment", str(env_path),
        "--workspace-id", "workspace-123",
        "--apim-api-key", "apim-key",
        "--tenant-id", "tenant-guid",
        "--client-id", "client-guid",
        "--client-secret", "client-secret",
        "--api-key", "postman-api-key"
    ]
    
    # Act
    result = sut.main(argv)
    
    # Assert
    assert result == 0
    assert load_json_mock.call_count == 2
    upsert_coll_mock.assert_called_once()
    upsert_env_mock.assert_called_once()


@patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy.mask_secret_for_github")
@patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy.upsert_collection")
@patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy.upsert_environment")
@patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy._load_json_file")
def test_main_masks_secrets_when_requested(
    load_json_mock, upsert_env_mock, upsert_coll_mock, mask_mock, tmp_path
):
    """Masks secrets when --mask-secrets flag is used"""
    
    # Arrange
    collection_path = tmp_path / "collection.json"
    env_path = tmp_path / "environment.json"
    collection_path.write_text("{}", encoding='utf-8')
    env_path.write_text("{}", encoding='utf-8')
    
    load_json_mock.side_effect = [
        {"info": {"name": "Test"}},
        {"name": "Test Env", "values": []}
    ]
    upsert_coll_mock.return_value = ("created", "uid")
    upsert_env_mock.return_value = ("created", "name", "uid")
    
    argv = [
        "--collection", str(collection_path),
        "--environment", str(env_path),
        "--workspace-id", "workspace-123",
        "--apim-api-key", "apim-key",
        "--client-secret", "client-secret",
        "--api-key", "postman-key",
        "--mask-secrets"
    ]
    
    # Act
    result = sut.main(argv)
    
    # Assert
    assert result == 0
    assert mask_mock.call_count == 2
    mask_mock.assert_any_call("apim-key")
    mask_mock.assert_any_call("client-secret")


def test_main_returns_error_on_missing_postman_api_key(tmp_path):
    """Returns error code when Postman API key is missing"""
    
    # Arrange
    collection_path = tmp_path / "collection.json"
    env_path = tmp_path / "environment.json"
    collection_path.write_text("{}", encoding='utf-8')
    env_path.write_text("{}", encoding='utf-8')
    
    argv = [
        "--collection", str(collection_path),
        "--environment", str(env_path),
        "--workspace-id", "workspace-123",
        "--apim-api-key", "apim-key",
        "--client-secret", "client-secret"
        # Missing --api-key and no POSTMAN_API_KEY env var
    ]
    
    # Act
    result = sut.main(argv)
    
    # Assert
    assert result == 1


def test_main_returns_error_on_missing_collection_file(tmp_path):
    """Returns error code when collection file doesn't exist"""
    
    # Arrange
    nonexistent_path = tmp_path / "nonexistent.json"
    env_path = tmp_path / "environment.json"
    env_path.write_text("{}", encoding='utf-8')
    
    argv = [
        "--collection", str(nonexistent_path),
        "--environment", str(env_path),
        "--workspace-id", "workspace-123",
        "--apim-api-key", "apim-key",
        "--client-secret", "client-secret",
        "--api-key", "postman-key"
    ]
    
    # Act
    result = sut.main(argv)
    
    # Assert
    assert result == 1


def test_main_returns_error_on_missing_environment_file(tmp_path):
    """Returns error code when environment file doesn't exist"""
    
    # Arrange
    collection_path = tmp_path / "collection.json"
    collection_path.write_text("{}", encoding='utf-8')
    nonexistent_path = tmp_path / "nonexistent.json"
    
    argv = [
        "--collection", str(collection_path),
        "--environment", str(nonexistent_path),
        "--workspace-id", "workspace-123",
        "--apim-api-key", "apim-key",
        "--client-secret", "client-secret",
        "--api-key", "postman-key"
    ]
    
    # Act
    result = sut.main(argv)
    
    # Assert
    assert result == 1


def test_main_returns_error_on_missing_required_secret(tmp_path):
    """Returns error code when required secret is missing"""
    
    # Arrange
    collection_path = tmp_path / "collection.json"
    env_path = tmp_path / "environment.json"
    collection_path.write_text("{}", encoding='utf-8')
    env_path.write_text("{}", encoding='utf-8')
    
    argv = [
        "--collection", str(collection_path),
        "--environment", str(env_path),
        "--workspace-id", "workspace-123",
        "--apim-api-key", "apim-key",
        # Missing --client-secret
        "--api-key", "postman-key"
    ]
    
    # Act
    result = sut.main(argv)
    
    # Assert
    assert result == 1


@patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy.upsert_collection")
@patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy._load_json_file")
def test_main_injects_all_provided_secrets(load_json_mock, upsert_coll_mock, tmp_path):
    """Injects all provided secrets into environment"""
    
    # Arrange
    collection_path = tmp_path / "collection.json"
    env_path = tmp_path / "environment.json"
    collection_path.write_text("{}", encoding='utf-8')
    env_path.write_text("{}", encoding='utf-8')
    
    env_json_original = {"name": "Test", "values": []}
    load_json_mock.side_effect = [
        {"info": {"name": "Test"}},
        env_json_original.copy()
    ]
    upsert_coll_mock.return_value = ("created", "uid")
    
    # Mock upsert_environment to capture the env_json argument
    with patch("devops_toolset.saas_platforms.postman.inject_secrets_and_deploy.upsert_environment") as upsert_env_mock:
        upsert_env_mock.return_value = ("created", "name", "uid")
        
        argv = [
            "--collection", str(collection_path),
            "--environment", str(env_path),
            "--workspace-id", "workspace-123",
            "--apim-api-key", "apim-key-value",
            "--tenant-id", "tenant-guid-value",
            "--client-id", "client-guid-value",
            "--client-secret", "client-secret-value",
            "--api-key", "postman-key"
        ]
        
        # Act
        result = sut.main(argv)
        
        # Assert
        assert result == 0
        upsert_env_mock.assert_called_once()
        
        # Get the env_json that was passed to upsert_environment
        call_args = upsert_env_mock.call_args
        injected_env = call_args[0][3]  # 4th positional argument
        
        # Verify all secrets were injected
        values = injected_env["values"]
        assert any(v["key"] == "ocpApimSubscriptionKey" and v["value"] == "apim-key-value" for v in values)
        assert any(v["key"] == "tenantId" and v["value"] == "tenant-guid-value" for v in values)
        assert any(v["key"] == "clientId" and v["value"] == "client-guid-value" for v in values)
        assert any(v["key"] == "clientSecret" and v["value"] == "client-secret-value" for v in values)

# endregion
