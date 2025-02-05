"""DevOps common commands"""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Commands(ValueDictsBase):
    """Commands for common DevOps code."""

    # Add your commands here
    _commands = {
        "echo": "echo {variable}",
    }
