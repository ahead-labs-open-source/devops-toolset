""" This script will hold general purpose utils for a remote linux host """

from devops_toolset.core.app import App
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.linux.commands import Commands as LinuxCommands
from devops_toolset.project_types.linux.Literals import Literals as LinuxLiterals
import logging
import pathlib
import devops_toolset.tools.cli as tools_cli

app: App = App()
literals = LiteralsCore([LinuxLiterals])
commands = CommandsCore([LinuxCommands])


def edit_in_place(search_for: str, replace_with: str, file_path: str):
    """ Performs an edit-in-place operation by replacing a value on a file using sed -i command
    Arguments:
        search_for: The value will be replaced.
        replace_with: The value "search_for" will be replaced for.
        file_path: Path of the destination file to perform the edit operation.

    Raises: FileNotFoundError -> When file_path does not exist
    """

    if not pathlib.Path(file_path).exists():
        message = literals.get("file_not_exist_err").format(path=file_path)
        logging.error(message)
        raise FileNotFoundError()

    tools_cli.call_subprocess(commands.get("edit_in_place").format(
        search_for=search_for,
        replace_with=replace_with,
        file_path=file_path
    ), log_before_out=[literals.get("edit_in_place_post").format(
        search_for=search_for, replace_with=replace_with, path=file_path)],
     log_after_err=[literals.get("edit_in_place_err").format(
         search_for=search_for, replace_with=replace_with, path=file_path)])


def edit_multiple_in_place(replacements: dict, file_path: str):
    """ Performs an edit-in-place operation by replacing a value on a file using sed -i command
    Arguments:
        replacements: Dict containing: key -> string to replace -- value -> replacement
        file_path: Path of the destination file to perform the edit operation.
    """

    for key, value in replacements.items():
        edit_in_place(key, value, file_path)


if __name__ == "__main__":
    help(__name__)
