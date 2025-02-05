"""Logging configuration"""

import logging as logger
import logging.handlers
from logging.config import dictConfig
from devops_toolset.core.ColorFormatter import ColorFormatter
import devops_toolset.core.settings as settings

import json


def configure(filepath):
    """Configures the Python logging using a dictionary from a json file and adding a default
    fallback configuration with the basics

    Args:
        filepath: Path of the file which contains the configuration
        (See https://docs.python.org/2/library/logging.config.html#logging-config-api)
    """

    try:
        configure_by_file(filepath)
        add_filter_to_console_handler(logger.WARNING)
        add_colored_formatter_to_console_handlers()
    except Exception as err:
        logger.error(f"Cannot configure logger: {format(err)}")
        configure_by_default(logger.INFO)


def configure_by_default(loglevel):
    """ Configures a root logger using a default configuration

    Args:
        logging.level used by default
    """
    log = logger.getLogger()
    log.setLevel(loglevel)
    log.addHandler(logger.StreamHandler())
    log.info("Default configuration loaded successfully.")


def configure_by_file(filepath):
    """Configures the Python logging using a dictionary from a json file

    Args:
        filepath: Path of the file which contains the configuration
        (See https://docs.python.org/2/library/logging.config.html#logging-config-api)

    Raises:
        FileNotFoundError: If filepath doesn't exist.
        OSError: If filepath cannot be opened.
        AttributeError: If json config file content is not well-formed
    """
    with open(filepath, "r") as config_file:
        config = json.load(config_file)
        dictConfig(config["logging"])


def add_filter_to_console_handler(loglevel):
    """Adds a filter to the console in order to drop messages above desired loglevel

    Args:
        loglevel: Logging.loglevel that indicates messages below this level will be logged on this handler

    """
    log = logger.getLogger()
    handler = log.handlers[0]
    handler.addFilter(lambda record: record.levelno <= loglevel)


def add_time_rotated_file_handler(backupcount=10, filepath=".", when='midnight'):
    """Adds a filter to the console in order to drop messages above desired loglevel

     Args:
        backupcount: Number of backup files on rotation (10 files or days by default)
        filepath: Path of the file used to log in.
        when: Defines when to rotate
        (see https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler)

    Raises: FileNotFoundError: When passed filepath doesn't exist
    """
    log = logger.getLogger()
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=filepath, when=when, backupCount=backupcount)
    log.addHandler(file_handler)


def add_colored_formatter_to_console_handlers():
    """ Adds a custom colored formatter to the current console handler """
    log = logger.getLogger()
    for handler in log.handlers:
        color_formatter = ColorFormatter(handler.formatter._fmt)
        handler.setFormatter(color_formatter)


if __name__ == "__main__":
    configure(settings.log_config_file_path)
