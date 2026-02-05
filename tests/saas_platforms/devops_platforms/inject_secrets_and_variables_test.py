"""Unit tests for inject_secrets_and_variables module"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import devops_toolset.saas_platforms.github.inject_secrets_and_variables as sut


KEY_LITERAL = '"key"'
KEYVAULT_URL = "https://kv-test.vault.azure.net/secrets/my-secret"
REPO_FULL_NAME = "owner/repo"


# region strip_jsonc_comments()

def test_strip_jsonc_comments_removes_line_comments():
    """Removes line comments (// ...)"""
    
    # Arrange
    content = """
    {
        "key": "value" // This is a comment
    }
    """
    
    # Act
    result = sut.strip_jsonc_comments(content)
    
    # Assert
    assert "//" not in result
    assert KEY_LITERAL in result
    assert '"value"' in result


def test_strip_jsonc_comments_removes_block_comments():
    """Removes block comments (/* ... */)"""
    
    # Arrange
    content = """
    {
        /* This is a block comment */
        "key": "value"
    }
    """
    
    # Act
    result = sut.strip_jsonc_comments(content)
    
    # Assert
    assert "/*" not in result
    assert "*/" not in result
    assert KEY_LITERAL in result


def test_strip_jsonc_comments_handles_multiline_block_comments():
    """Removes multiline block comments"""
    
    # Arrange
    content = """
    {
        /*
         * Multiline
         * comment
         */
        "key": "value"
    }
    """
    
    # Act
    result = sut.strip_jsonc_comments(content)
    
    # Assert
    assert "/*" not in result
    assert "*/" not in result
    assert KEY_LITERAL in result

# endregion


# region load_template()

def test_load_template_raises_filenotfound_if_not_exists():
    """Raises FileNotFoundError if template doesn't exist"""
    
    # Arrange
    nonexistent_path = Path("/nonexistent/path.jsonc")
    
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        sut.load_template(nonexistent_path)


def test_load_template_parses_valid_jsonc(tmp_path):
    """Parses valid JSONC template"""
    
    # Arrange
    template_content = """
    {
        // Comment
        "repository": {
            "variables": {
                "VAR1": "value1"
            }
        }
    }
    """
    template_path = tmp_path / "template.jsonc"
    template_path.write_text(template_content, encoding='utf-8')
    
    # Act
    result = sut.load_template(template_path)
    
    # Assert
    assert "repository" in result
    assert result["repository"]["variables"]["VAR1"] == "value1"


def test_load_template_raises_on_invalid_json(tmp_path):
    """Raises ValueError on invalid JSON"""
    
    # Arrange
    template_content = """
    {
        "repository": {
            "variables": {
                "VAR1": "value1"  // Missing closing braces
    """
    template_path = tmp_path / "invalid.jsonc"
    template_path.write_text(template_content, encoding='utf-8')
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid JSON"):
        sut.load_template(template_path)

# endregion


# region is_keyvault_url()

def test_is_keyvault_url_returns_true_for_valid_url():
    """Returns True for valid Key Vault URL"""
    
    # Arrange
    url = KEYVAULT_URL
    
    # Act
    result = sut.is_keyvault_url(url)
    
    # Assert
    assert result is True


def test_is_keyvault_url_returns_true_for_url_with_version():
    """Returns True for Key Vault URL with version"""
    
    # Arrange
    url = "https://kv-test.vault.azure.net/secrets/my-secret/abc123"
    
    # Act
    result = sut.is_keyvault_url(url)
    
    # Assert
    assert result is True


def test_is_keyvault_url_returns_false_for_plain_text():
    """Returns False for plain text"""
    
    # Arrange
    text = "plain-text-secret"
    
    # Act
    result = sut.is_keyvault_url(text)
    
    # Assert
    assert result is False


def test_is_keyvault_url_returns_false_for_other_url():
    """Returns False for non-Key Vault URL"""
    
    # Arrange
    url = "https://example.com/secrets/my-secret"
    
    # Act
    result = sut.is_keyvault_url(url)
    
    # Assert
    assert result is False

# endregion


# region fetch_keyvault_secret()

@patch("subprocess.run")
def test_fetch_keyvault_secret_calls_az_cli(subprocess_mock):
    """Calls Azure CLI with correct parameters"""
    
    # Arrange
    url = KEYVAULT_URL
    subprocess_mock.return_value = MagicMock(stdout="secret-value\n")
    
    # Act
    result = sut.fetch_keyvault_secret(url)
    
    # Assert
    subprocess_mock.assert_called_once()
    call_args = subprocess_mock.call_args[0][0]
    assert "az" in call_args
    assert "keyvault" in call_args
    assert "secret" in call_args
    assert "show" in call_args
    assert "--vault-name" in call_args
    assert "kv-test" in call_args
    assert "--name" in call_args
    assert "my-secret" in call_args
    assert result == "secret-value"


@patch("subprocess.run")
def test_fetch_keyvault_secret_includes_version_if_present(subprocess_mock):
    """Includes version parameter if present in URL"""
    
    # Arrange
    url = "https://kv-test.vault.azure.net/secrets/my-secret/abc123"
    subprocess_mock.return_value = MagicMock(stdout="secret-value\n")
    
    # Act
    result = sut.fetch_keyvault_secret(url)
    
    # Assert
    call_args = subprocess_mock.call_args[0][0]
    assert "--version" in call_args
    assert "abc123" in call_args
    assert result == "secret-value"


@patch("subprocess.run")
def test_fetch_keyvault_secret_raises_on_cli_error(subprocess_mock):
    """Raises RuntimeError on Azure CLI error"""
    
    # Arrange
    url = KEYVAULT_URL
    subprocess_mock.side_effect = sut.subprocess.CalledProcessError(
        1, "az", stderr="Secret not found"
    )
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Failed to fetch secret"):
        sut.fetch_keyvault_secret(url)


def test_fetch_keyvault_secret_raises_on_invalid_url():
    """Raises ValueError on invalid URL"""
    
    # Arrange
    url = "not-a-valid-url"
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid Key Vault URL"):
        sut.fetch_keyvault_secret(url)

# endregion


# region parse_template()

def test_parse_template_extracts_repository_variables():
    """Extracts repository-level variables"""
    
    # Arrange
    template = {
        "repository": {
            "variables": {
                "VAR1": "value1",
                "VAR2": "value2"
            }
        }
    }
    
    # Act
    variables, _ = sut.parse_template(template)
    
    # Assert
    assert len(variables) == 2
    assert any(v.name == "VAR1" and v.value == "value1" and v.scope == "repository" for v in variables)
    assert any(v.name == "VAR2" and v.value == "value2" and v.scope == "repository" for v in variables)


def test_parse_template_extracts_repository_secrets():
    """Extracts repository-level secrets"""
    
    # Arrange
    template = {
        "repository": {
            "secrets": {
                "SECRET1": "plain-text-secret"
            }
        }
    }
    
    # Act
    _, secrets = sut.parse_template(template)
    
    # Assert
    assert len(secrets) == 1
    assert secrets[0].name == "SECRET1"
    assert secrets[0].value == "plain-text-secret"
    assert secrets[0].scope == "repository"


def test_parse_template_extracts_environment_variables():
    """Extracts environment-level variables"""
    
    # Arrange
    template = {
        "environments": {
            "staging": {
                "variables": {
                    "ENV_VAR1": "staging-value"
                }
            },
            "production": {
                "variables": {
                    "ENV_VAR1": "production-value"
                }
            }
        }
    }
    
    # Act
    variables, _ = sut.parse_template(template)
    
    # Assert
    assert len(variables) == 2
    assert any(v.name == "ENV_VAR1" and v.value == "staging-value" and v.scope == "staging" for v in variables)
    assert any(v.name == "ENV_VAR1" and v.value == "production-value" and v.scope == "production" for v in variables)


def test_parse_template_extracts_environment_secrets():
    """Extracts environment-level secrets"""
    
    # Arrange
    template = {
        "environments": {
            "staging": {
                "secrets": {
                    "ENV_SECRET1": "staging-secret"
                }
            }
        }
    }
    
    # Act
    _, secrets = sut.parse_template(template)
    
    # Assert
    assert len(secrets) == 1
    assert secrets[0].name == "ENV_SECRET1"
    assert secrets[0].value == "staging-secret"
    assert secrets[0].scope == "staging"


@patch("devops_toolset.saas_platforms.github.inject_secrets_and_variables.fetch_keyvault_secret")
def test_parse_template_fetches_keyvault_secrets_when_requested(keyvault_mock):
    """Fetches secrets from Key Vault when fetch_from_keyvault=True"""
    
    # Arrange
    template = {
        "repository": {
            "secrets": {
                "SECRET1": KEYVAULT_URL
            }
        }
    }
    keyvault_mock.return_value = "fetched-secret-value"
    
    # Act
    _, secrets = sut.parse_template(template, fetch_from_keyvault=True)
    
    # Assert
    keyvault_mock.assert_called_once_with(KEYVAULT_URL)
    assert secrets[0].value == "fetched-secret-value"


@patch("devops_toolset.saas_platforms.github.inject_secrets_and_variables.fetch_keyvault_secret")
def test_parse_template_skips_keyvault_fetch_when_not_requested(keyvault_mock):
    """Does not fetch from Key Vault when fetch_from_keyvault=False"""
    
    # Arrange
    template = {
        "repository": {
            "secrets": {
                "SECRET1": KEYVAULT_URL
            }
        }
    }
    
    # Act
    _, secrets = sut.parse_template(template, fetch_from_keyvault=False)
    
    # Assert
    keyvault_mock.assert_not_called()
    assert secrets[0].value == KEYVAULT_URL

# endregion


# region set_repository_variable()

@patch("subprocess.run")
def test_set_repository_variable_calls_gh_cli(subprocess_mock):
    """Calls GitHub CLI with correct parameters"""
    
    # Arrange
    repo = REPO_FULL_NAME
    name = "VAR1"
    value = "value1"
    
    # Act
    sut.set_repository_variable(repo, name, value)
    
    # Assert
    subprocess_mock.assert_called_once()
    call_args = subprocess_mock.call_args[0][0]
    assert "gh" in call_args
    assert "variable" in call_args
    assert "set" in call_args
    assert name in call_args
    assert "--repo" in call_args
    assert repo in call_args
    assert "--body" in call_args
    assert value in call_args


@patch("subprocess.run")
def test_set_repository_variable_does_not_execute_in_dry_run(subprocess_mock):
    """Does not execute command in dry run mode"""
    
    # Arrange
    repo = REPO_FULL_NAME
    name = "VAR1"
    value = "value1"
    
    # Act
    sut.set_repository_variable(repo, name, value, dry_run=True)
    
    # Assert
    subprocess_mock.assert_not_called()

# endregion


# region set_environment_variable()

@patch("subprocess.run")
def test_set_environment_variable_calls_gh_cli_with_env(subprocess_mock):
    """Calls GitHub CLI with --env parameter"""
    
    # Arrange
    repo = REPO_FULL_NAME
    env = "staging"
    name = "VAR1"
    value = "value1"
    
    # Act
    sut.set_environment_variable(repo, env, name, value)
    
    # Assert
    call_args = subprocess_mock.call_args[0][0]
    assert "gh" in call_args
    assert "--env" in call_args
    assert env in call_args

# endregion


# region inject_variables_and_secrets()

@patch("devops_toolset.saas_platforms.github.inject_secrets_and_variables.set_repository_variable")
@patch("devops_toolset.saas_platforms.github.inject_secrets_and_variables.set_environment_variable")
@patch("devops_toolset.saas_platforms.github.inject_secrets_and_variables.set_repository_secret")
@patch("devops_toolset.saas_platforms.github.inject_secrets_and_variables.set_environment_secret")
def test_inject_variables_and_secrets_calls_all_functions(
    env_secret_mock, repo_secret_mock, env_var_mock, repo_var_mock
):
    """Calls appropriate functions for each variable/secret type"""
    
    # Arrange
    repo = REPO_FULL_NAME
    variables = [
        sut.Variable(name="REPO_VAR", value="value1", scope="repository"),
        sut.Variable(name="ENV_VAR", value="value2", scope="staging")
    ]
    secrets = [
        sut.Secret(name="REPO_SECRET", value="secret1", scope="repository"),
        sut.Secret(name="ENV_SECRET", value="secret2", scope="production")
    ]
    
    # Act
    sut.inject_variables_and_secrets(repo, variables, secrets)
    
    # Assert
    repo_var_mock.assert_called_once_with(repo, "REPO_VAR", "value1", False)
    env_var_mock.assert_called_once_with(repo, "staging", "ENV_VAR", "value2", False)
    repo_secret_mock.assert_called_once_with(repo, "REPO_SECRET", "secret1", False)
    env_secret_mock.assert_called_once_with(repo, "production", "ENV_SECRET", "secret2", False)

# endregion
