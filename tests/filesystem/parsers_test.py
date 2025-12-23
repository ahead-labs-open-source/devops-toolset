"""Unit core for the parsers file"""

import devops_toolset.filesystem.parsers as sut
import pathlib
import json
from unittest.mock import patch, mock_open
from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals

app: App = App()
platform_specific = app.load_platform_specific("environment")
wp_literals = LiteralsCore([WordpressLiterals])

# region parse_project_xml_data()


def test_parse_project_xml_data_when_add_environment_variables_is_false_then_return_dict_with_env_variables(paths):
    """When add_environment_variables is false, then return dict with xml data"""

    # Arrange
    expected_result = {"PROJECT_FOO1": "foo1", "PROJECT_FOO2": "foo2", "PROJECT_FOO3": "foo3"}
    with patch.object(pathlib.Path, "joinpath") as joinpath_mock:
        joinpath_mock.return_value = paths.file_foo_xml_project_path
        # Act
        result = sut.parse_project_xml_data(False)
        # Assert
        assert expected_result == result


def test_parse_project_xml_data_when_add_environment_variables_is_true_then_call_create_env_variables(paths):
    """When add_environment_variables is false, then return dict with xml data"""

    # Arrange
    expected_result = {"PROJECT_FOO1": "foo1", "PROJECT_FOO2": "foo2", "PROJECT_FOO3": "foo3"}
    with patch.object(pathlib.Path, "joinpath") as joinpath_mock:
        joinpath_mock.return_value = paths.file_foo_xml_project_path
        with patch.object(sut, "platform_specific") as platform_specific_mock:
            with patch.object(platform_specific_mock, "create_environment_variables") as create_env_vars_mock:
                # Act
                sut.parse_project_xml_data(True)
                # Assert
                create_env_vars_mock.assert_called_once_with(expected_result)


# endregion

# region Parse_json_file()


@patch("builtins.open", new_callable=mock_open, read_data="{}")
def test_parse_json_file_load_json(builtins_open):
    """Given a JSON file path, returns dict with JSON content"""

    # Arrange

    # Act
    result = sut.parse_json_file("file.json")

    # Assert
    assert result == json.loads("{}")

# endregion
