"""Contains tools for logging"""

import logging
from enum import Enum
from typing import List


class LogLevel(Enum):
    """https://docs.python.org/3/library/logging.html#levels"""
    critical = 50,
    error = 40,
    warning = 30,
    info = 20,
    debug = 10,


def log_list(logs_list: List[str], level: LogLevel = LogLevel.info):
    """Logs a list using the specified level.

    Args:
        logs_list: List of strings to be logged.
        level: Logging level.
    """
    if logs_list:
        for log in logs_list:
            logging.log(level.value[0], log)


def log_stdouterr(output: bytes, level: LogLevel):
    """Logs stdout or stderr outputs.

    It splits lines using the universal line ending and decodes content to
    UTF-8.

    Args:
        output: stdout or stderr output to be logged.
        level: Logging level.
    """

    for line in output.splitlines():
        logging.log(level.value[0], line.decode(encoding="utf-8", errors="ignore"))


def log_indented_list(header: str, list_values: List[str], level: LogLevel):
    """Logs an indented list with a not indented header.

    Args:
        header: String being logged first, not indented.
        list_values: List of values to be logged, intented.
        level: Logging level.
    """

    if list_values:

        logging.log(level.value[0], header)

        for value in list_values:
            logging.log(level.value[0], f"\t{value}")


def get_parameter_value_list(local_values: dict) -> List:
    """Creates a list with all parameter values.

    Args:
        local_values: locals from the function.

    Returns:
        List with argument name and value pairs.
    """

    argument_list = []

    for key, value in local_values.items():
        argument_list.append(f"{key} = {value}")

    return argument_list
