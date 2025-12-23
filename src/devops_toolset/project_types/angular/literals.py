"""Angular module literals"""

from devops_toolset.core.app import App
from devops_toolset.core.value_dicts_base import ValueDictsBase

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the Angular module."""

    _info = {
        "angular_project_version": _("The project version is {version}"),
    }
    _errors = {}
