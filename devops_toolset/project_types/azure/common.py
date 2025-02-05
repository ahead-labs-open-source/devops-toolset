"""Provides common tools for all Azure services"""

from devops_toolset.core.app import App
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.azure.commands import Commands as AzureCommands
from devops_toolset.project_types.azure.Literals import Literals as AzureLiterals
from devops_toolset.tools import cli

import json
import logging


app: App = App()
literals = LiteralsCore([AzureLiterals])
commands = CommandsCore([AzureCommands])


def get_installed_cli_extensions() -> list:
    """Returns a list of the Azure extensions installed.

    Returns:
        List of Azure extensions.
    """

    az_command: str = commands.get("azure_cli_extension_list")
    logging.info(literals.get("azure_cli_executing_command").format(command=az_command))

    result: str = cli.call_subprocess_with_result(az_command)
    logging.info(literals.get("azure_cli_command_output").format(output=result))

    return json.loads(result)


def is_cli_extension_installed(name: str):
    """Checks if the provided Azure CLI extension is installed.

    Args:
        name: Extension name to be checked.
    """

    installed_extensions: list = get_installed_cli_extensions()
    extension_names = map(lambda ext: ext["name"], installed_extensions)

    return name in extension_names


def login_service_principal(user: str, secret: str, tenant: str) -> [list, None]:
    """Log into Azure using az login command.

    Args:
        user: Username for the service principal.
        secret: Secret for the service principal.
        tenant: Azure tenant ID.

    Returns:
        JSON list from Azure login.
    """

    az_command: str = commands.get("azure_cli_login_service_principal").format(
        user=user,
        secret=secret,
        tenant=tenant
    )

    result: str = cli.call_subprocess_with_result(az_command)
    logging.info(literals.get("azure_cli_logging_in_service_principal").format(
        service_principal=user,
        tenant=tenant
    ))

    if result:
        json_result = json.loads(result)
        logging.info(json_result)
        return json_result
    else:
        return None


def logout():
    """Log out from Azure using az logout command."""

    az_command: str = commands.get("azure_cli_logout")
    logging.info(literals.get("azure_cli_executing_command").format(command=az_command))

    cli.call_subprocess(az_command)
    logging.info(literals.get("azure_cli_logging_out"))


if __name__ == "__main__":
    help(__name__)
