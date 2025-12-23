"""Unit tests for the tools/svn module"""

from unittest.mock import patch, ANY

import devops_toolset.tools.svn as sut
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.tools.literals import Literals as ToolsLiterals
from devops_toolset.tools.commands import Commands as ToolsCommands

commands = CommandsCore([ToolsCommands])
literals = LiteralsCore([ToolsLiterals])


# region svn_add()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_svn_add_calls_svnadd_command(call_subprocess_mock, svndata):
    """Checks if svn add command is called as subprocess"""

    # Arrange
    expected_command = commands.get("svn_add").format(files_glob=svndata.glob)

    # Act
    sut.svn_add(svndata.glob)

    # Assert
    call_subprocess_mock.assert_called_with(expected_command,
                                            log_before_process=[ANY],
                                            log_after_err=[ANY])


# endregion

# region svn_checkin()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_svn_checkin_calls_checkin_command(call_subprocess_mock, svndata):
    """Checks if svn check in command is called as subprocess"""

    # Arrange
    expected_command = commands.get("svn_checkin").format(comment=svndata.comment,
                                                          username=svndata.username,
                                                          password=svndata.password)

    # Act
    sut.svn_checkin(svndata.comment, svndata.username, svndata.password)

    # Assert
    call_subprocess_mock.assert_called_with(expected_command,
                                            log_before_process=[ANY],
                                            log_after_err=[ANY])


# endregion

# region svn_checkout()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_svn_checkout_calls_checkout_command(call_subprocess_mock, svndata):
    """Checks if svn check out command is called as subprocess"""

    # Arrange
    expected_command = commands.get("svn_checkout").format(url=svndata.repo_url,
                                                           local_path=svndata.path)

    # Act
    sut.svn_checkout(svndata.repo_url, svndata.path)

    # Assert
    call_subprocess_mock.assert_called_with(expected_command,
                                            log_before_process=[ANY],
                                            log_after_err=[ANY])


# endregion

# region svn_copy()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_svn_copy_calls_copy_command(call_subprocess_mock, svndata):
    """Checks if svn copy command is called as subprocess"""

    # Arrange
    expected_command = commands.get("svn_copy").format(origin=svndata.path,
                                                       destination=svndata.path)

    # Act
    sut.svn_copy(svndata.path, svndata.path)

    # Assert
    call_subprocess_mock.assert_called_with(expected_command,
                                            log_before_process=[ANY],
                                            log_after_err=[ANY])

# endregion
