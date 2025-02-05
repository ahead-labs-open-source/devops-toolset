""" Unit tests for the dotnet/utils.py module"""

import devops_toolset as sut
import pathlib
from devops_toolset.core import App
from devops_toolset.core import CommandsCore
from devops_toolset.core import LiteralsCore
from devops_toolset import Commands as DotnetCommands
from devops_toolset import Literals as DotnetLiterals
from unittest.mock import patch

app: App = App()
literals = LiteralsCore([DotnetLiterals])
commands = CommandsCore([DotnetCommands])


# region get_appsettings_environments()

@patch("logging.info")
@patch("pathlib.Path.glob")
def test_get_appsettings_environments_returns_list(glob_mock, logging_info_mock, dotnetdata):
    """ Given the .csproj file path, returns a list of strings."""

    # Arrange
    csproj_path = "path/to/csproj"
    glob_mock.return_value = dotnetdata.get_appsettings_files()

    # Act
    result = sut.get_appsettings_environments(csproj_path)

    # Assert
    assert type(result) is list


@patch("logging.info")
@patch("pathlib.Path.glob")
def test_get_appsettings_environments_given_unmatched_environments_returns_empty_list(
        glob_mock, logging_info_mock, dotnetdata):
    """ Given the .csproj file path and wrong appsettings files, returns an
    empty list."""

    # Arrange
    csproj_path = "path/to/csproj"
    glob_mock.return_value = dotnetdata.get_wrong_appsettings_files()

    # Act
    result = sut.get_appsettings_environments(csproj_path)

    # Assert
    assert result == []


# endregion

# region get_csproj_project_version()


def test_get_csproj_project_version_given_path_returns_version_number(dotnetdata, tmp_path):
    """ Given the .csproj file path , returns the version number."""

    # Arrange
    csproj_file_content = dotnetdata.csproj_file_content
    csproj_file_path = pathlib.Path.joinpath(tmp_path, "my_project.csproj")
    with open(str(csproj_file_path), "w") as properties_file:
        properties_file.write(csproj_file_content)

    # Act
    result = sut.get_csproj_project_version(str(csproj_file_path))

    # Assert
    assert result == "6.6.6"


# endregion

