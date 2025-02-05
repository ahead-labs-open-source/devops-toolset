""" Unit-core for the npm-py module"""
from unittest.mock import patch

import pytest
import devops_toolset as sut
from devops_toolset.core import CommandsCore
from devops_toolset.core import LiteralsCore
from devops_toolset import Commands as NodeCommands
from devops_toolset import Literals as NodeLiterals
from devops_toolset.core import App

app: App = App()
literals = LiteralsCore([NodeLiterals])
commands = CommandsCore([NodeCommands])

# region convert_npm_extra_args


@pytest.mark.parametrize("value, expected",
                         [(["--arg1=arg1value", "--arg2=arg2value"], " -- --arg1=arg1value --arg2=arg2value"),
                          (None, "")])
def test_convert_npm_extra_args_given_args_then_return_extra_args(value, expected):
    """ Given *args, when present, then should compound an -- <extra_args> string, empty string otherwise """
    # Arrange / Act
    if value:
        arg0 = value[0]
        arg1 = value[1]
        result = sut.convert_npm_extra_args(arg0, arg1)
    else:
        result = sut.convert_npm_extra_args(value)
    # Assert
    assert result == expected

# endregion

# region convert_npm_parameter_if_present


@pytest.mark.parametrize("value, expected", [(True, "--if-present"), (False, "")])
def test_convert_npm_parameter_if_present_given_value_then_return_if_present(value, expected):
    """ Given value, when True, then should compound an --if-present string or empty string otherwise """
    # Arrange / Act
    result = sut.convert_npm_parameter_if_present(value)
    # Assert
    assert result == expected

# endregion

# region convert_npm_parameter_silent


@pytest.mark.parametrize("value, expected", [(True, "--silent"), (False, "")])
def test_convert_npm_parameter_silent_given_value_when_true_then_return_silent(value, expected):
    """ Given value, when True, then return --silent, empty string otherwise """
    # Arrange / Act
    result = sut.convert_npm_parameter_silent(value)
    # Assert
    assert result == expected

# endregion

# region run_script


@patch("devops_toolset.tools.cli.call_subprocess")
def test_run_script_given_command_then_calls_subprocess_with_npm_run_command(subprocess_mock):
    """ Given command, then calls subprocess with the npm_run command """
    # Arrange
    sub_command = "test_script"
    silent = ""
    if_present = ""
    extra_args = None
    command = commands.get("npm_run").format(
        command=sub_command,
        silent=silent,
        if_present=if_present,
        extra_args=sut.convert_npm_extra_args(extra_args)
    )
    literal_before = literals.get("npm_run_before").format(task=sub_command)
    literal_after = literals.get("npm_run_after").format(task=sub_command)
    literal_error = literals.get("npm_run_error").format(task=sub_command)
    # Act
    sut.run_script(sub_command, False, False)
    # Assert
    subprocess_mock.assert_called_once_with(
        command,
        log_before_out=[literal_before],
        log_after_out=[literal_after],
        log_after_err=[literal_error]
    )

# endregion

# region install


@patch("devops_toolset.tools.cli.call_subprocess")
def test_install_given_folder_then_calls_subprocess_with_npm_install_command(subprocess_mock):
    """ Given folder, then calls subprocess with the npm_install command """
    # Arrange
    folder = ""
    command = commands.get("npm_install").format(
        folder=folder
    )
    literal_before = literals.get("npm_install_before")
    literal_after = literals.get("npm_install_after")
    literal_error = literals.get("npm_install_error")
    # Act
    sut.install(folder)
    # Assert
    subprocess_mock.assert_called_once_with(
        command,
        log_before_out=[literal_before],
        log_after_out=[literal_after],
        log_after_err=[literal_error])

# endregion
