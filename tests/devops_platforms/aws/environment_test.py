"""Unit tests for the environment file"""

from devops_toolset.core import CommandsCore
from devops_toolset import Commands as LinuxCommands
from unittest.mock import patch
import devops_toolset as sut
import os
import pytest

linux_commands = CommandsCore([LinuxCommands])


# region create_environment_variables()

@patch("logging.info")
def test_create_environment_variables_given_dict_when_not_empty_calls_to_create_env_variables_command(
        logger_mock, platformdata):
    """Given a dictionary, when it is not empty, creates environment variables"""

    # Arrange
    environment_variables = platformdata.environment_variables_dict

    # Act
    sut.create_environment_variables(environment_variables)

    # Assert
    for key in environment_variables.keys():
        assert key in os.environ
        # Cleanup: We need to remove the example values from the env variables.
        del os.environ[key]

# endregion


# region end_task()

def test_end_task_given_result_when_fail_then_raises_error():
    """ Given result type, when fail, then should raise an EnvironmentError """
    # Arrange
    result_type = sut.ResultType.fail
    # Act and Assert
    with pytest.raises(EnvironmentError):
        sut.end_task(result_type)


def test_end_task_given_result_when_success_then_do_nothing():
    """ Given result type, when success, then should not raise anything """
    # Arrange
    result_type = sut.ResultType.success
    # Act and Assert
    sut.end_task(result_type)

# endregion


# region get_platform_variable_keys()

def test_get_platform_variable_dict_returns_dict():
    """Returns a list of strings"""

    # Arrange

    # Act
    result = sut.get_platform_variable_dict()

    # Assert
    assert type(result) is dict

# endregion


# region log_environment_variables()

@patch("devops_toolset.devops_platforms.common.log_environment_variables")
def test_log_environment_variables_logs(log_environment_variables_mock):
    """Returns a list of strings"""

    # Arrange
    variables: dict = sut.get_platform_variable_dict()

    # Act
    sut.log_environment_variables(variables)

    # Assert
    log_environment_variables_mock.assert_called()

# endregion
