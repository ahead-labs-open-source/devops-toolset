"""Unit tests for the project_types/azure/database.py module"""

from unittest.mock import patch

import devops_toolset as sut
import pytest

# region add_mysql_flexible_server_firewall_rule()


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("logging.info")
def test_add_mysql_flexible_server_firewall_rule(logging_info_mock, subprocess_mock):
    """Calls subprocess with result"""

    # Arrange
    subprocess_mock.return_value = "{}"

    # Act
    _ = sut.add_mysql_flexible_server_firewall_rule("", "", "", "", None)

    # Assert
    subprocess_mock.assert_called()

# endregion add_mysql_flexible_server_firewall_rule

# region execute_mysql_flexible_server_sql_script()


def test_execute_mysql_flexible_server_sql_script_raises_valueerror():
    """Given None for file_path and query, raises ValueError."""

    # Arrange
    file_path = None
    query = None

    # Act and Assert
    with pytest.raises(ValueError):
        sut.execute_mysql_flexible_server_sql_script("", "", "", "", file_path, query)


@patch("pathlib.Path.exists")
@patch("devops_toolset.filesystem.tools.strip_utf8_bom_character_from_file")
@patch("devops_toolset.project_types.azure.common.is_cli_extension_installed")
@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("devops_toolset.tools.cli.call_subprocess")
@patch("logging.info")
def test_execute_mysql_flexible_server_sql_script_installs_extension(
        logging_info_mock, subprocess_mock, subprocess_result_mock, common_mock, tools_mock, path_exists_mock):
    """Calls subprocess with result"""

    # Arrange
    file_path = "pathto/file"
    query = None
    common_mock.return_value = False
    path_exists_mock.return_value = True

    # Act
    _ = sut.execute_mysql_flexible_server_sql_script("", "", "", "", file_path, query)

    # Assert
    subprocess_mock.assert_called()
    subprocess_result_mock.assert_called()


@patch("pathlib.Path.exists")
@patch("devops_toolset.filesystem.tools.strip_utf8_bom_character_from_file")
@patch("devops_toolset.project_types.azure.common.is_cli_extension_installed")
@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("devops_toolset.tools.cli.call_subprocess")
@patch("logging.info")
def test_execute_mysql_flexible_server_sql_script_doesnt_install_extension(
        logging_info_mock, subprocess_mock, subprocess_result_mock, common_mock, tools_mock, path_exists_mock):
    """Calls subprocess with result"""

    # Arrange
    file_path = "pathto/file"
    query = None
    common_mock.return_value = True
    path_exists_mock.return_value = True

    # Act
    _ = sut.execute_mysql_flexible_server_sql_script("", "", "", "", file_path, query)

    # Assert
    subprocess_result_mock.assert_called()


@patch("pathlib.Path.exists")
@patch("devops_toolset.filesystem.tools.strip_utf8_bom_character_from_file")
@patch("devops_toolset.project_types.azure.common.is_cli_extension_installed")
@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("devops_toolset.tools.cli.call_subprocess")
@patch("logging.info")
def test_execute_mysql_flexible_server_sql_script_doesnt_strip_file(
        logging_info_mock, subprocess_mock, subprocess_result_mock, common_mock, tools_mock, path_exists_mock):
    """Calls subprocess with result"""

    # Arrange
    file_path = None
    query = ""
    common_mock.return_value = True
    path_exists_mock.return_value = True

    # Act
    _ = sut.execute_mysql_flexible_server_sql_script("", "", "", "", file_path, query)

    # Assert
    tools_mock.assert_not_called()


@patch("pathlib.Path.exists")
@patch("devops_toolset.filesystem.tools.strip_utf8_bom_character_from_file")
@patch("devops_toolset.project_types.azure.common.is_cli_extension_installed")
@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("devops_toolset.tools.cli.call_subprocess")
@patch("logging.info")
@patch("logging.warning")
def test_execute_mysql_flexible_server_sql_script_skips_when_file_doesnt_exist(
        logging_warn_mock, logging_info_mock, subprocess_mock, subprocess_result_mock, common_mock, tools_mock,
        path_exists_mock):
    """Calls subprocess with result"""

    # Arrange
    file_path = None
    query = ""
    common_mock.return_value = True
    path_exists_mock.return_value = False

    # Act
    _ = sut.execute_mysql_flexible_server_sql_script("", "", "", "", file_path, query)

    # Assert
    subprocess_mock.assert_not_called()

# endregion execute_mysql_flexible_server_sql_script

# region remove_mysql_flexible_server_firewall_rule()


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("logging.info")
def test_remove_mysql_flexible_server_firewall_rule(logging_info_mock, subprocess_mock):
    """Calls subprocess with result"""

    # Arrange

    # Act
    _ = sut.remove_mysql_flexible_server_firewall_rule("", "", "")

    # Assert
    subprocess_mock.assert_called()

# endregion remove_mysql_flexible_server_firewall_rule
