"""Provides tools for managing the Azure Database service"""
from devops_toolset.core.app import App
from devops_toolset.core.commands_core import CommandsCore
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.project_types.azure.commands import Commands as AzureCommands, Log as Log
from devops_toolset.project_types.azure.literals import Literals as AzureLiterals
from devops_toolset.tools import cli

import devops_toolset.filesystem.tools
import devops_toolset.project_types.azure.common as common
import json
import logging
import re
import pathlib

app: App = App()
literals = LiteralsCore([AzureLiterals])
commands = CommandsCore([AzureCommands])
rule_name_fix_regex = "[^A-Za-z0-9-_]"


def add_mysql_flexible_server_firewall_rule(server_name: str, resource_group: str, rule_name: str,
                                            ip_address: str, end_ip_address: [str, None] = None,
                                            log: Log = Log.OFF) -> dict:
    """Adds a firewall rule to MySQL Flexible server.

    Args:
        server_name: Name of the server we target.
        resource_group: Azure resource group that the server belongs to.
        rule_name: Name of the rule to be created.
        ip_address: Unique IP address to add to the rule if we are not adding a
            range. In case of adding a range, this will be the starting IP
            address of the range.
        end_ip_address: End IP address of the range. If we are adding a unique
            IP address this value must be None.
        log: Log level from OFF, VERBOSE or DEBUG.

    Returns:
        Operation result
    """

    az_command: str = commands.get("azure_cli_db_mysql_flexible_server_firewall_rule_create").format(
        server_name=server_name,
        resource_group=resource_group,
        rule_name=re.sub(rule_name_fix_regex, "-", rule_name),
        start_ip_address=ip_address,
        end_ip_address=ip_address if end_ip_address is None else end_ip_address,
        log="" if log == Log.OFF else f"--{log.name.lower()}"
    )
    logging.info(literals.get("azure_cli_executing_command").format(command=az_command))

    result: str = cli.call_subprocess_with_result(az_command)
    logging.info(literals.get("azure_cli_command_output").format(output=result))

    return json.loads(result)


def execute_mysql_flexible_server_sql_script(admin_user: str, admin_password: str, server_name: str, database_name: str,
                                             file_path: [str, None] = None, query: [str, None] = None,
                                             log: Log = Log.OFF, strip_bom: bool = True) -> [str, None]:
    """Executes a script (file) / query (text) against MySQL Flexible server.

    Args:
        admin_user: Admin user for the server.
        admin_password: Password for the admin user.
        server_name: Name of the server.
        database_name: Name of the database.
        file_path: Path to the SQL file to be executed.
        query: Query text to be executed. If file_path is not None, query will
            be ignored.
        log: Log level from OFF, VERBOSE or DEBUG.
        strip_bom: If True it strips BOM character from the file.
    """

    # Check that parameters are correct
    if file_path is None and query is None:
        raise ValueError(literals.get("azure_cli_db_mysql_flexible_server_execute_file_query_parameters_error"))

    # If file path doesn't exist, then return without doing anything
    if not pathlib.Path.exists(file_path):
        logging.warning(literals.get("azure_mysql_script_not_found").format(file_path=file_path))
        return

    # Install rdbms-connect Azure CLI extension if not already installed
    az_extension: str = "rdbms-connect"
    if not common.is_cli_extension_installed(az_extension):
        az_command: str = commands.get("azure_cli_extension_add").format(name=az_extension)
        logging.info(literals.get("azure_cli_executing_command").format(command=az_command))
        cli.call_subprocess(az_command)

    # Strip UTF-8 BOM from script file
    if file_path is not None and strip_bom:
        devops_toolset.filesystem.tools.strip_utf8_bom_character_from_file(file_path)

    # Compose and execute command
    az_command: str = commands.get("azure_cli_db_mysql_flexible_server_execute").format(
        server_name=server_name,
        admin_user=admin_user,
        admin_password=admin_password,
        database_name=database_name,
        file_path=f"-f \"{file_path}\"" if file_path is not None else "",
        query=f"-q \"{query}\"" if query is not None and file_path is None else "",
        log="" if log == Log.OFF else f"--{log.name.lower()}"
    )
    logging.info(literals.get("azure_cli_executing_command").format(command=az_command))

    result: str = cli.call_subprocess_with_result(az_command)
    logging.info(literals.get("azure_cli_command_output").format(output=result))


def remove_mysql_flexible_server_firewall_rule(server_name: str, resource_group: str, rule_name: str,
                                               log: Log = Log.OFF) -> str:
    """Removes a firewall rule from MySQL Flexible server.

    Args:
        server_name: Name of the server we target.
        resource_group: Azure resource group that the server belongs to.
        rule_name: Name of the rule to be created.
        log: Log level from OFF, VERBOSE or DEBUG.

    Returns:
        Operation result
    """

    az_command: str = commands.get("azure_cli_db_mysql_flexible_server_firewall_rule_delete").format(
        server_name= server_name,
        resource_group=resource_group,
        rule_name=re.sub(rule_name_fix_regex, "-", rule_name),
        log="" if log == Log.OFF else f"--{log.name.lower()}"
    )
    logging.info(literals.get("azure_cli_executing_command").format(command=az_command))

    result: str = cli.call_subprocess_with_result(az_command)
    logging.info(literals.get("azure_cli_command_output").format(output=result))

    return result


if __name__ == "__main__":
    help(__name__)
