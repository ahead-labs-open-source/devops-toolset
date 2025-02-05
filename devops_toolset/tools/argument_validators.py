"""Contains argument validators"""

import argparse
import devops_toolset.filesystem.paths as paths

from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.tools.Literals import Literals as ToolsLiterals

literals = LiteralsCore([ToolsLiterals])


class PathValidator(argparse.Action):
    """Validates a path"""
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(PathValidator, self).__init__(option_strings, dest.replace("-", "_"), **kwargs)

    def __call__(self, parent_parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

        if not paths.is_valid_path(values):
            raise ValueError(literals.get("val_path_argument_not_valid").format(argument=self.dest))
