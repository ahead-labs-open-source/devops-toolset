"""filesystem module literals"""

from devops_toolset.core.value_dicts_base import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the filesystem module."""

    _titles = {}
    _info = {
        "fs_composer_path_is": _("Composer file path is {path}."),
        "fs_file_content": _("File content => {content}."),
        "fs_file_moving": _("Moving file {origin_file_path} to {destination_file_path}."),
        "fs_file_path": _("File path is: {path}"),
        "fs_file_path_not_valid": _("File path is not valid."),
        "fs_file_path_does_not_exist": _("File path does not exist."),
        "fs_project_path_is": _("Project path is {path}."),
        "fs_strip_bom": _("I am stripping BOM character from file \"{path}\""),
        "fs_writing_file": _("Writing file \"{path}\""),
        "fs_zip_added_file": _("[{zip_file_name}] Added file: {added_file}."),
    }
    _errors = {
        "fs_not_dir": _("Path must be a dir, not a file."),
        "list_length_zero": _("List length is 0."),
        "list_length_higher_than": _("List length is higher than {length} and must be lower."),
    }
