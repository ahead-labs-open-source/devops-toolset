"""devops_toolset.devops_platforms.aws module literals."""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the devops_toolset.devops_platforms.aws module."""

    # Add your core literal dictionaries here
    _info = {
        "aws_command": _("Command: {command}"),
        "platform_created_ev": _("Created environment variable {key} with value {value}"),
    }
    _errors = {}
