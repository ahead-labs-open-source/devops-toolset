""" Contains Angular utilities """

from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.angular.Literals import Literals as AngularLiterals
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.project_types.angular.commands import Commands as AngularCommands

import devops_toolset.filesystem.parsers as parsers
import logging
import devops_toolset.filesystem.tools as filesystem

app: App = App()
platform_specific = app.load_platform_specific("environment")
literals = LiteralsCore([AngularLiterals])
commands = CommandsCore([AngularCommands])


def get_packagejson_project_version(
        packagejson_path: str, environment_variable_name: str = "DT_PROJECT_VERSION") -> str:
    """Gets the version number from a package.json file

    Arguments:
        packagejson_path: Path to the package.json file.
        environment_variable_name: Name of the environment variable to be
            created. Defaults to "DT_PROJECT_VERSION".

    Returns:
        The version number defined in the package.json file.
    """

    package_json: dict = parsers.parse_json_file(packagejson_path)
    version = package_json["version"]

    version_environment_variable = {environment_variable_name: version}
    platform_specific.create_environment_variables(version_environment_variable)

    return version


def set_project_version_in_json_file(packagejson_path: str, destination_file_path: str):
    """Gets the project version from the package.json file and sets its value
        in a custom json file.

    Args:
        packagejson_path: Path to the package.json file.
        destination_file_path: Path to the JSON file.
            with the project version.
    """

    version: str = get_packagejson_project_version(packagejson_path)
    filesystem.update_json_file_key_text(["version"], version, destination_file_path)


if __name__ == "__main__":
    help(__name__)
