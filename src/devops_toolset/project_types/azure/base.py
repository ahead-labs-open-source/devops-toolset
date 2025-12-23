"""Provides support for basic operations in Azure."""

import logging

from devops_toolset.core.app import App
from devops_toolset.core.commands_core import CommandsCore
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.project_types.azure.commands import Commands as AzureCommands, Log as Log
from devops_toolset.project_types.azure.literals import Literals as AzureLiterals
from devops_toolset.tools import cli

app: App = App()
literals = LiteralsCore([AzureLiterals])
commands = CommandsCore([AzureCommands])


def check_resource_group_exists(resource_group_name):
    """Checks if a resource group exists."""

    logging.info(literals.get("azure_cli_resource_group_checking").format(name=resource_group_name))
    result = cli.call_subprocess_with_result(commands.get("azure_cli_resource_group_exists")
                                             .format(name=resource_group_name))

    if result.strip() == 'true':
        logging.info(literals.get("azure_cli_resource_group_exists").format(name=resource_group_name))
        return True
    else:
        logging.info(literals.get("azure_cli_resource_group_not_exists").format(name=resource_group_name))
        return False


def create_resource_group(resource_group_name, location):
    """Creates a new resource group."""

    if check_resource_group_exists(resource_group_name):
        return

    logging.info(literals.get("azure_cli_resource_group_creating").format(name=resource_group_name))
    result = cli.call_subprocess_with_result(commands.get("azure_cli_resource_group_create")
                                             .format(name=resource_group_name, location=location))

    logging.info(result)
    logging.info(literals.get("azure_cli_resource_group_created").format(name=resource_group_name))


def delete_resource_group(resource_group_name):
    """Deletes a resource group."""

    if not check_resource_group_exists(resource_group_name):
        return

    logging.info(literals.get("azure_cli_resource_group_deleting").format(name=resource_group_name))
    result = cli.call_subprocess_with_result(commands.get("azure_cli_resource_group_delete")
                                             .format(name=resource_group_name), log_err=True)

    if result is None:
        logging.info(literals.get("azure_cli_resource_group_deleted").format(name=resource_group_name))
    else:
        logging.error(result)
        logging.error(literals.get("azure_cli_resource_group_delete_failed").format(name=resource_group_name))
