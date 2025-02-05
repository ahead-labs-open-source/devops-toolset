"""Unit tests for the common file"""

from devops_toolset.core import CommandsCore
from devops_toolset import Commands as CommonCommands
from unittest.mock import patch
import devops_toolset as sut

commands = CommandsCore([CommonCommands])


# region echo_environment_variable()

@patch("devops_toolset.tools.cli.call_subprocess_with_result")
def test_echo_environment_variable_calls_subprocess(subprocess_mock):
    """Calls"""

    # Arrange
    variable_name: str = "variable1"

    # Act
    _ = sut.echo_environment_variable(variable_name)

    # Assert
    subprocess_mock.assert_called_with(commands.get("echo").format(
        variable=variable_name
    ))

# endregion


# region log_environment_variables()

@patch("logging.info")
def test_log_environment_variables_logs(logging_info_mock):
    """Returns a list of strings"""

    # Arrange
    variables: dict = {
        "key1": "value1"
    }

    # Act
    sut.log_environment_variables(variables)

    # Assert
    logging_info_mock.assert_called()

# endregion
