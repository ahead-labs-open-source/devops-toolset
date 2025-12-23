""" Unit tests for the project_types/angular/utils.py module"""

import devops_toolset.project_types.angular.utils as sut
import pathlib
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.angular.commands import Commands as AngularCommands
from devops_toolset.project_types.angular.literals import Literals as AngularLiterals
from devops_toolset.core.app import App
from unittest.mock import patch

app: App = App()
literals = LiteralsCore([AngularLiterals])
commands = CommandsCore([AngularCommands])

# region get_packagejson_project_version()


def test_get_packagejson_project_version_given_path_returns_version_number(angulardata, tmp_path):
    """ Given the package.json file path, returns the version number."""

    # Arrange
    packagejson_file_content = angulardata.packagejson_content
    packagejson_file_path = pathlib.Path.joinpath(tmp_path, "package.json")
    with open(str(packagejson_file_path), "w") as properties_file:
        properties_file.write(packagejson_file_content)

    # Act
    result = sut.get_packagejson_project_version(str(packagejson_file_path))

    # Assert
    assert result == "1.2.3-rc.4"


@patch("logging.info")
def test_get_packagejson_project_version_given_path_creates_environment_variable(log_info_mock, angulardata, tmp_path):
    """ Given only the package.json file path, creates an environment
        variable with the version number."""

    # Arrange
    packagejson_file_content = angulardata.packagejson_content
    packagejson_file_path = pathlib.Path.joinpath(tmp_path, "package.json")
    with open(str(packagejson_file_path), "w") as properties_file:
        properties_file.write(packagejson_file_content)

    # Act
    with patch.object(sut, "platform_specific") as platform_specific_mock:
        with patch.object(platform_specific_mock, "create_environment_variables") as create_env_vars_mock:
            sut.get_packagejson_project_version(str(packagejson_file_path))

            # Assert
            create_env_vars_mock.assert_called()

# endregion get_packagejson_project_version()

# region set_project_version_in_json_file()


@patch("devops_toolset.filesystem.tools.update_json_file_key_text")
def test_set_project_version_in_json_file_all_calls_take_place(update_json_file_key_text_mock):
    """Given a package.json path, calls to all other functions are made."""

    # Arrange
    packagejson_path = "pathto/package.json"
    destination_path = "pathto/destination.json"

    # Act
    with patch.object(sut, "get_packagejson_project_version") as get_packagejson_project_version_mock:
        get_packagejson_project_version_mock.return_value = "1.2.3-rc.4"
        sut.set_project_version_in_json_file(packagejson_path, destination_path)

    # Assert
    get_packagejson_project_version_mock.assert_called_once()
    update_json_file_key_text_mock.assert_called_once()


# endregion set_project_version_in_json_file()
