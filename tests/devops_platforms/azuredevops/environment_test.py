"""Unit tests for the environment file"""

from unittest.mock import patch
from io import StringIO
import devops_toolset as sut


# region create_environment_variables()


@patch("logging.error")
@patch("sys.stdout", new_callable=StringIO)
def test_create_environment_variables_given_dict_when_not_empty_writes_to_stdout(
        mock_stdout, logger_mock, platformdata):
    """Given a dictionary, when it is not empty, writes environment variables
    to stdout in the Azure DevOps notation"""

    # Arrange
    environment_variables = platformdata.environment_variables_dict

    # Act
    sut.create_environment_variables(environment_variables)

    # Assert
    assert mock_stdout.tell() > 0


@patch("logging.error")
@patch("sys.stdout.write")
def test_create_environment_variables_given_dict_writes_correct_format_to_stdout(
        mock_stdout_write, logger_mock, platformdata):
    """Given a dictionary, writes environment variables in the correct format
    to stdout in the Azure DevOps notation"""

    # Arrange
    environment_variables = platformdata.environment_variables_dict1
    key = list(environment_variables.keys())[0]
    value = environment_variables[key]

    # Act
    sut.create_environment_variables(environment_variables)

    # Assert
    mock_stdout_write.assert_called_with(f"##vso[task.setvariable variable={key}]{value}\n")

# endregion


# region end_task()

@patch("sys.stdout.write")
@patch("logging.error")
def test_end_task_given_type_and_description_writes_to_stdout(logging_mock, mock_stdout_write, platformdata):
    """Given a type and a description, writes task termination command to
    stdout in the Azure DevOps notation"""

    # Arrange
    result_type = sut.ResultType.fail

    # Act
    sut.end_task(result_type)

    # Assert
    mock_stdout_write.assert_called_with(f"##vso[task.complete result={result_type.value};]DONE\n")

# endregion


# region get_platform_variable_keys()

def test_get_platform_variable_keys_returns_dict():
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
    variable_keys: dict = sut.get_platform_variable_dict()

    # Act
    sut.log_environment_variables(variable_keys)

    # Assert
    log_environment_variables_mock.assert_called()

# endregion
