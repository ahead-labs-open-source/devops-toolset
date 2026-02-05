"""Contains tools for working with the command line"""

import devops_toolset.core.log_tools
import os
import shlex
import subprocess
from pyfiglet import Figlet
from typing import List, Sequence, Tuple, Union


Command = Union[str, Sequence[str]]


def _command_to_args(command: Command) -> list[str]:
    if isinstance(command, str):
        command = command.strip()
        if not command:
            return []
        return shlex.split(command, posix=(os.name != "nt"))

    if isinstance(command, Sequence):
        args = [str(part).strip() for part in command]
        return [part for part in args if part]

    raise TypeError(f"Unsupported command type: {type(command)!r}")


def _format_args_for_log(args: Sequence[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(list(args))
    try:
        return shlex.join(list(args))
    except AttributeError:
        return " ".join(list(args))


def print_title(text: str):
    """Prints a title in the console"""
    f = Figlet()
    print(f.renderText(text))


def call_subprocess_with_result(command: Command, log_err: bool = False) -> Union[str, Tuple[str, str]]:
    """Calls a subprocess and returns the stdout

        Args:
            command: Command to be executed.
            log_err: If True logs error to stderr.
        """

    args = _command_to_args(command)
    if not args:
        raise ValueError("Command cannot be empty")

    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    process.wait()

    return_out = out.decode("utf-8", errors="backslashreplace") if out else None
    return_err = err.decode("utf-8", errors="backslashreplace") if err else None

    if log_err:
        devops_toolset.core.log_tools.log_stdouterr(err, devops_toolset.core.log_tools.LogLevel.error)

    if err:
        return return_out, return_err

    return return_out


def call_subprocess(command: Command, log_before_process: List[str] = None,
                    log_before_out: List[str] = None, log_after_out: List[str] = None,
                    log_before_err: List[str] = None, log_after_err: List[str] = None):
    """Calls a subprocess.

    Args:
        command: Command to be executed.
        log_before_process: List of strings to log as info before the process
            call.
        log_before_out: List of strings to log as info before the stdout, if
            no errors.
        log_after_out: List of strings to log as info after the stdout, if
            no errors.
        log_before_err: List of strings to log as error before the stderr, if
            errors.
        log_after_err: List of strings to log as error after the stderr, if
            errors.
    """

    args = _command_to_args(command)
    if not args:
        raise ValueError("Command cannot be empty")

    devops_toolset.core.log_tools.log_list([
        _format_args_for_log(args)
    ], devops_toolset.core.log_tools.LogLevel.info)
    devops_toolset.core.log_tools.log_list(log_before_process, devops_toolset.core.log_tools.LogLevel.info)

    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    process.wait()

    if out:
        devops_toolset.core.log_tools.log_list(log_before_out, devops_toolset.core.log_tools.LogLevel.info)
        devops_toolset.core.log_tools.log_stdouterr(out, devops_toolset.core.log_tools.LogLevel.info)
        devops_toolset.core.log_tools.log_list(log_after_out, devops_toolset.core.log_tools.LogLevel.info)

    if err and process.returncode != 0:
        devops_toolset.core.log_tools.log_list(log_before_err, devops_toolset.core.log_tools.LogLevel.error)
        devops_toolset.core.log_tools.log_stdouterr(err, devops_toolset.core.log_tools.LogLevel.error)
        devops_toolset.core.log_tools.log_list(log_after_err, devops_toolset.core.log_tools.LogLevel.error)


if __name__ == "__main__":
    print(__doc__ or "")
