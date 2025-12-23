"""Helper functions for SVN-related task automation."""

# ! python

import devops_toolset.core.app
import devops_toolset.filesystem.paths
import devops_toolset.tools.cli
from devops_toolset.core.commands_core import CommandsCore
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.tools.literals import Literals as ToolsLiterals
from devops_toolset.tools.commands import Commands as ToolsCommands

app: devops_toolset.core.app.App = devops_toolset.core.app.App()
literals = LiteralsCore([ToolsLiterals])
commands = CommandsCore([ToolsCommands])
platform_specific = app.load_platform_specific("environment")


def svn_add(files_glob: str):
    """ Performs a checkout operation for a svn repository
        Args:
            :param files_glob: Glob representing a group of files F.I -> trunk/*
    """
    devops_toolset.tools.cli.call_subprocess(commands.get("svn_add").format(
        files_glob=files_glob
    ),
        log_before_process=[literals.get("svn_add_init")],
        log_after_err=[literals.get("svn_add_err")])


def svn_checkin(comment: str, username: str, password: str):
    """ Performs a checkin operation into a svn repository
        Args:
            :param comment: Comment for the checkin operation
            :param username: Username of the owner of the repository who will perform the operation
            :param password: Password of the owner of the repository who will perform the operation
    """
    devops_toolset.tools.cli.call_subprocess(commands.get("svn_checkin").format(
        comment=comment,
        username=username,
        password=password
    ),
        log_before_process=[literals.get("svn_checkin_init")],
        log_after_err=[literals.get("svn_checkin_err")])


def svn_checkout(repo_url: str, local_path: str = '.'):
    """ Performs a checkout operation for a svn repository
        Args:
            :param repo_url: Full url for the svn repository, F.I -> https://plugins.svn.wordpress.org/your-plugin-name
            :param local_path: Path where the repository will be checked out.
    """
    devops_toolset.tools.cli.call_subprocess(commands.get("svn_checkout").format(
        url=repo_url,
        local_path=local_path
    ),
        log_before_process=[literals.get("svn_checkout_init")],
        log_after_err=[literals.get("svn_checkout_err")])


def svn_copy(origin: str, destination: str = '.'):
    """ Performs a copy operation using svn engine
        Args:
            :param origin: Origin path to copy from
            :param destination: Destination path where the files will be copied to.
    """
    devops_toolset.tools.cli.call_subprocess(commands.get("svn_copy").format(
        origin=origin,
        destination=destination
    ),
        log_before_process=[literals.get("svn_copy_init").format(
            origin=origin,
            destination=destination
        )],
        log_after_err=[literals.get("svn_copy_err").format(
            origin=origin,
            destination=destination
        )])


if __name__ == "__main__":
    help(__name__)
