"""Defines constants for the module."""

from enum import Enum


class Directions(Enum):
    """Defines sorting and finding directions"""

    ASCENDING = 1,
    DESCENDING = 2


class FileNames(object):
    """Defines constants for file names.

    Attributes:
        GITIGNORE_FILE: .gitignore file.
        PROJECT_FILE: Project definition file.
        TEMP_DIRECTORY: Temporary directory name.
    """

    GITIGNORE_FILE = ".gitignore"
    PROJECT_FILE = "project.xml"
    TEMP_DIRECTORY = "__temp"


class FileType(Enum):
    """Defines the file type of file to be written.

    To be added to w or b options when using builtins.open().

    e.g:
        To read a text file:
            with.open(file, f"r{FileType.TEXT}")... => r
        To write a binary file:
            with.open(file, f"w{FileType.BINARY}")... => wb

    Attributes:
        TEXT: Text file suffix
        BINARY: Binary file suffix
    """

    TEXT = ""
    BINARY = "b"
