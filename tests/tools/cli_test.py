"""Unit core for the tools file"""

import unittest.mock as mock
import devops_toolset.tools.cli as sut
import subprocess
import devops_toolset.core.log_tools as log_tools
from pyfiglet import Figlet

# region call_subprocess(str)


@mock.patch.object(subprocess, "Popen")
@mock.patch("devops_toolset.core.log_tools")
def test_call_subprocess_given_command_srt_then_calls_popens_with_command(logtools_mock, subprocess_mock, clidata):
    """ Given an str command, then calls subprocess. Popen with that command"""

    # Arrange
    foo_command = clidata.sample_command
    expected_out = clidata.sample_log_message_info
    shell = True
    stdout = subprocess.PIPE
    stderr = subprocess.PIPE
    subprocess_mock.return_value.return_code = 0
    subprocess_mock.return_value.communicate.return_value = (expected_out, expected_out)

    # Act
    sut.call_subprocess(foo_command)

    # Assert
    subprocess_mock.assert_called_once_with(foo_command, shell=shell, stdout=stdout, stderr=stderr)


@mock.patch.object(subprocess, "Popen")
def test_call_subprocess_given_command_srt_when_stdout_has_lines_then_log_info(subprocess_mock, clidata):
    """ Given an str command, then calls subprocess.Popen and must log stdout as info"""

    # Arrange
    foo_command = clidata.sample_command
    expected_log_message = clidata.sample_log_message_info
    log_level = log_tools.LogLevel.info
    subprocess_mock.return_value.return_code = 0
    subprocess_mock.return_value.communicate.return_value = (expected_log_message, b"")

    # Act
    with mock.patch.object(log_tools, "log_stdouterr") as logging_mock:
        sut.call_subprocess(foo_command)
        # Assert
        logging_mock.assert_called_once_with(expected_log_message, log_level)


@mock.patch.object(subprocess, "Popen")
def test_call_subprocess_given_command_srt_when_stderr_has_lines_then_log_error(subprocess_mock, clidata):
    """ Given an str command, then calls subprocess.Popen and must log stderr as error"""

    # Arrange
    foo_command = clidata.sample_command
    expected_log_message = clidata.sample_log_message_error
    log_level = log_tools.LogLevel.error
    subprocess_mock.return_value.return_code = 0
    subprocess_mock.return_value.communicate.return_value = (b"", expected_log_message)

    # Act
    with mock.patch.object(log_tools, "log_stdouterr") as logging_mock:
        sut.call_subprocess(foo_command)

        # Assert
        logging_mock.assert_called_once_with(expected_log_message, log_level)

# endregion call_subprocess(str)

# region call_subprocess_with_result


@mock.patch.object(subprocess, "Popen")
def test_call_subprocess_with_result_logs_stdouterr_when_err_and_log_err_is_enabled(subprocess_mock, clidata):
    """ Given command, logs to stdouterr when command returned error and log_err is enabled """
    # Arrange
    foo_command = clidata.sample_command
    subprocess_mock.return_value.return_code = 0
    subprocess_mock.return_value.communicate.return_value = (b"Some error", b"Some error")

    # Act
    with mock.patch.object(log_tools, "log_stdouterr") as logging_mock:
        sut.call_subprocess_with_result(foo_command, True)
        # Assert
        logging_mock.assert_called()


@mock.patch.object(subprocess, "Popen")
def test_call_subprocess_with_result_returns_err_without_logging_when_log_err_disabled(subprocess_mock, clidata):
    """ Given command, logs to stdouterr when command returned error and log_err is enabled """
    # Arrange
    foo_command = clidata.sample_command
    expected_return = b"Some output"
    subprocess_mock.return_value.return_code = 0
    subprocess_mock.return_value.communicate.return_value = (expected_return, None)

    # Act
    result = sut.call_subprocess_with_result(foo_command)
    # Assert
    assert expected_return.decode("utf-8", errors="backslashreplace") == result

# endregion

# region print_title


@mock.patch("builtins.print")
def test_print_title(print_mock):
    """ Given a text, then prints it using a Figlet instance """
    # Arrange
    text = "Example text"
    f = Figlet()
    title_text = f.renderText(text)
    # Act
    sut.print_title(text)
    # Assert
    print_mock.assert_called_with(title_text)

# endregion print_title
