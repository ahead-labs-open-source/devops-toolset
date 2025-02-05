"""i18n module literals"""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the wordpress module."""

    _titles = {}
    _info = {
        "i18n_mo_file_removed": _("[POT file compilation] File removed: {path}"),
        "i18n_pot_file_path": _("[POT file generation] File path: {path}"),
        "i18n_po_file_list": _("[POT file compilation] Python file list to be compiled:"),
        "i18n_pot_file_list": _("[POT file generation] Python file list to be parsed:"),
        "i18n_pot_file_removed": _("[POT file generation] File removed: {path}"),
        "i18n_pot_script": _("[POT file generation] Script being used: {script}"),
        "i18n_po_command": _("[POT file compilation] Command being called: {command}"),
        "i18n_pot_command": _("[POT file generation] Command being called: {command}"),
    }
    _errors = {}
