"""This file contains common code for all the platforms"""

from devops_toolset.core.app import App
from devops_toolset.core.commands_core import CommandsCore
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.devops_platforms.commands import Commands as CommonCommands
from devops_toolset.devops_platforms.literals import Literals as CommonLiterals
from devops_toolset.devops_platforms.azuredevops.literals import Literals as AzureDevOpsLiterals
import devops_toolset.tools.cli as cli
import logging

app: App = App()
commands = CommandsCore([CommonCommands])
literals = LiteralsCore([CommonLiterals, AzureDevOpsLiterals])


def echo_environment_variable(environment_variable_name: str) -> str:
    """Echoes an environment variable. This function is common to all and
    limited to operating systems that support the echo command.

    Args:
        environment_variable_name: Name of the environment variable to echo.

    Returns:
        The environment variable value.
    """
    return cli.call_subprocess_with_result(commands.get("echo").format(
        variable=environment_variable_name
    ))


def log_environment_variables(platform_keys: dict):
    """Logs all environment variables for this platform and process.

    Args:
        platform_keys: dict with key-value pairs of platform variables.
    """

    spaces: int = len(max(platform_keys, key=len)) + 5

    for key, value in platform_keys.items():
        logging.info(literals.get("environment_variable_log").format(
            key=str(key).ljust(spaces, "."),
            value=value
        ))


if __name__ == "__main__":
    help(__name__)
