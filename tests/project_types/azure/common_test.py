"""Unit tests for the project_types/azure/common.py module"""

from unittest.mock import patch
import devops_toolset as sut
import pytest

# region get_installed_cli_extensions()


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("logging.info")
def test_get_installed_cli_extensions(logging_info_mock, subprocess_result_mock):
    """Calls subprocess with result"""

    # Arrange
    subprocess_result_mock.return_value = "{}"

    # Act
    _ = sut.get_installed_cli_extensions()

    # Assert
    subprocess_result_mock.assert_called()

# endregion get_installed_cli_extensions()

# region is_cli_extension_installed()


@patch("devops_toolset.project_types.azure.common.get_installed_cli_extensions")
def test_is_cli_extension_installed(get_installed_cli_extensions_mock):
    """Calls subprocess with result"""

    # Arrange
    extension_name = "my-extension"
    get_installed_cli_extensions_mock.return_value = [{"name": extension_name}]

    # Act
    result = sut.is_cli_extension_installed(extension_name)

    # Assert
    assert result is True

# endregion is_cli_extension_installed()

# region login_service_principal()


@patch("logging.info")
@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@pytest.mark.parametrize("return_value, expected", [("[]", []), (None, None)])
def test_login_service_principal_returns_result(subprocess_mock, logging_info_mock, return_value, expected):
    """Given service principal login data, when subprocess returns JSON list,
    returns list"""

    # Arrange
    user: str = "service-principal-client-id"
    secret: str = ""
    tenant: str = ""
    subprocess_mock.return_value = return_value

    # Act
    result = sut.login_service_principal(user, secret, tenant)

    # Assert
    assert result == expected

# endregion

# region logout()


@patch("logging.info")
@patch("devops_toolset.tools.cli.call_subprocess")
def test_logout_calls_subprocess(subprocess_mock, login_info_mock):
    """Given service principal login data, when subprocess returns JSON list,
    returns list"""

    # Arrange

    # Act
    sut.logout()

    # Assert
    subprocess_mock.assert_called()

# endregion
