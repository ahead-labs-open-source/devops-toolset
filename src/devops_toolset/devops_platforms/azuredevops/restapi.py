"""Azure DevOps REST API functionality"""

from devops_toolset.core.app import App
from devops_toolset.core.commands_core import CommandsCore
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.devops_platforms.azuredevops.literals import Literals as PlatformSpecificLiterals
from devops_toolset.devops_platforms.azuredevops.commands import Commands as PlatformSpecificCommands
import devops_toolset.filesystem.paths
from devops_toolset.tools.xcoding64 import encode
from typing import Union
import logging
import requests


app: App = App()
literals = LiteralsCore([PlatformSpecificLiterals])
commands = CommandsCore([PlatformSpecificCommands])


def generate_authentication_header(user_name: str, access_token: str) -> dict:
    """Generates an authentication header.

    Args:
        user_name: Token name as defined in Azure Devops personal access tokens
        access_token: Token as defined in Azure DevOps personal access tokens.

    Returns:
        Authentication header
    """

    token_base64 = encode(f"{user_name}:{access_token}")
    basic_auth_token = f"Basic {token_base64}"
    return {"Authorization": basic_auth_token}


def call_api(command: str, user_name: str, access_token: str) -> requests.Response:
    """Calls the REST API.

    Args:
        command: Command to be executed.
        user_name: Token name as defined in Azure Devops personal access tokens
        access_token: Token as defined in Azure DevOps personal access tokens.

    Returns:
        Response
    """

    headers = generate_authentication_header(user_name, access_token)

    logging.info(literals.get("azdevops_command").format(command=command))

    response = requests.get(command, headers=headers)
    if response.status_code != 200:
        raise ValueError(literals.get("azdevops_status_code").format(status_code=response.status_code))
    return response


def get_build_list(organization: str, project: str, user_name: str, access_token: str) -> dict:
    """Gets a list of the builds for a project.

    Args:
        organization: Azure DevOps organization. i.e: aheadlabs
        project: Azure DevOps project. i.e: devops-toolset
        user_name: Token name as defined in Azure Devops personal access tokens
        access_token: Token as defined in Azure DevOps personal access tokens

    Returns:
        Build list based on
            https://docs.microsoft.com/en-us/rest/api/azure/devops/build/builds/list#build
    """

    command = commands.get("azdevops_rest_get_build_list").format(organization=organization, project=project)
    return call_api(command, user_name, access_token).json()


def get_last_build_id(organization: str, project: str, user_name: str, access_token: str) -> Union[int, None]:
    """Returns the id of the last build.

    Args:
        organization: Azure DevOps organization. i.e: aheadlabs
        project: Azure DevOps project. i.e: devops-toolset
        user_name: Token name as defined in Azure Devops personal access tokens
        access_token: Token as defined in Azure DevOps personal access tokens

    Returns:
        ID of the build
    """

    build_list = get_build_list(organization, project, user_name, access_token)

    if build_list["count"] > 0:
        return build_list["value"][0]["id"]
    return None


def get_build(organization: str, project: str, build_id: int, artifact_name: str,
              user_name: str, access_token: str) -> dict:
    """Gets a build for a project.

    Args:
        organization: Azure DevOps organization. i.e: aheadlabs
        project: Azure DevOps project. i.e: devops-toolset
        build_id: Build id to obtained
        artifact_name: Name of the artifact to be obtained
        user_name: Token name as defined in Azure Devops personal access tokens
        access_token: Token as defined in Azure DevOps personal access tokens
    """

    command = commands.get("azdevops_rest_get_build").format(
        organization=organization, project=project, build_id=build_id, artifact_name=artifact_name)
    return call_api(command, user_name, access_token).json()


def get_last_build(organization: str, project: str, artifact_name: str,
                   user_name: str, access_token: str) -> dict:
    """Gets a build for a project.

    Args:
        organization: Azure DevOps organization. i.e: aheadlabs
        project: Azure DevOps project. i.e: devops-toolset
        artifact_name: Name of the artifact to be obtained
        user_name: Token name as defined in Azure Devops personal access tokens
        access_token: Token as defined in Azure DevOps personal access tokens
    """

    build_id = get_last_build_id(organization, project, user_name, access_token)
    return get_build(organization, project, build_id, artifact_name, user_name, access_token)


def get_artifact(organization: str, project: str, build_id: int, artifact_name: str, destination_path: str,
                 user_name: str, access_token: str) -> tuple[str | None, str | None]:
    """Gets a build for a project.

    Args:
        organization: Azure DevOps organization. i.e: aheadlabs
        project: Azure DevOps project. i.e: devops-toolset
        build_id: Build id to obtained
        artifact_name: Name of the artifact to be obtained
        destination_path: Path where the artifact will be saved.
        user_name: Token name as defined in Azure Devops personal access tokens
        access_token: Token as defined in Azure DevOps personal access tokens

    Returns:
        Tuple with file name and file path
    """

    build = get_build(organization, project, build_id, artifact_name, user_name, access_token)
    download_url = build["resource"]["downloadUrl"]
    if download_url:
        headers = generate_authentication_header(user_name, access_token)
        return devops_toolset.filesystem.paths.download_file(
            build["resource"]["downloadUrl"], destination_path, f"{artifact_name}.zip", headers)

    return None, None


def get_last_artifact(organization: str, project: str, artifact_name: str, destination_path: str,
                      user_name: str, access_token: str) -> tuple[str | None, str | None]:
    """Gets the last build for a project.

    Args:
        organization: Azure DevOps organization. i.e: aheadlabs
        project: Azure DevOps project. i.e: devops-toolset
        artifact_name: Name of the artifact to be obtained
        destination_path: Path where the artifact will be saved.
        user_name: Token name as defined in Azure Devops personal access tokens
        access_token: Token as defined in Azure DevOps personal access tokens

    Returns:
        Tuple with file name and file path
    """

    last_build_id = get_last_build_id(organization, project, user_name, access_token)
    if last_build_id:
        return \
            get_artifact(organization, project, last_build_id, artifact_name, destination_path, user_name, access_token)

    return None, None


if __name__ == "__main__":
    help(__name__)
