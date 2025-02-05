""" Dotnet utilities """

import devops_toolset.filesystem.parsers as parsers
import logging
import os.path
import pathlib
import re
from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.dotnet.Literals import Literals as DotnetLiterals
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.project_types.dotnet.commands import Commands as DotnetCommands


app: App = App()
platform_specific = app.load_platform_specific("environment")
literals = LiteralsCore([DotnetLiterals])
commands = CommandsCore([DotnetCommands])


def get_appsettings_environments(csproj_directory_path: str, include_development: bool = False) -> list[str]:
    """Gets a list of all environments configured in the solution.

    Args:
        csproj_directory_path: Path to directory that contains the csproj file.
        include_development: If True, Development/Dev is included in the list.

    Returns:
        List with all appsettings.*.json environment names.
    """

    path = pathlib.Path(csproj_directory_path)
    glob_pattern = "appsettings.*.json"
    regex_pattern = r'^appsettings\.([A-Za-z]+)\.json$'
    environments: list[str] = []

    logging.info(literals.get("dotnet_ef_utils_getting_appsettings_files").format(path=path))

    files = list(path.glob(glob_pattern))
    logging.info(literals.get("dotnet_ef_utils_appsettings_files_matched").format(files=files))
    for file in files:
        filename = os.path.basename(file)

        match = re.search(regex_pattern, filename)
        if match is None:
            logging.info(literals.get("dotnet_ef_utils_appsettings_no_environment_matched").format(filename=filename))
            continue

        logging.info(literals.get("dotnet_ef_utils_appsettings_environment_matched")
                     .format(filename=filename, environment=match.groups()[0]))
        environment = match.groups()[0]
        if (environment == "Development" or environment == "Dev") and not include_development:
            logging.info(literals.get("dotnet_ef_utils_appsettings_dev_environment_skipped"))
            continue
        environments.append(environment)

    return environments


def get_csproj_project_version(csproj_path: str, environment_variable_name: str = "DT_PROJECT_VERSION") -> str:
    """ Gets the version number from a .csproj file

    Arguments:
        csproj_path: Path to the .csproj file.
        environment_variable_name: Name of the environment variable to be
            created. Defaults to "DT_PROJECT_VERSION".

    Returns:
        The version number defined in the .csproj file.
    """

    version = parsers.get_xml_file_entity_text("./PropertyGroup/Version", csproj_path)

    version_environment_variable = {environment_variable_name: version["Version"]}
    platform_specific.create_environment_variables(version_environment_variable)

    return version["Version"]


if __name__ == "__main__":
    help(__name__)
