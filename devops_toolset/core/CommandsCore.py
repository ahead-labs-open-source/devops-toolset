"""Commands for the package."""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class CommandsCore(ValueDictsBase):
    """Core literals for the package.


    1. Create an instance of the CommandsCore class (this class).
    2. Pass as a parameter list all Commands classes you want to include.

        from devops_toolset.core.CommandsCore import CommandsCore
        from wordpress.commands import Commands as WpCommands

        commands = CommandsCore([WpCommands])

    3. Get a command by it's key.

        commands.get("wp_info")
    """

    # Add your core command dictionaries here
    _commands = {}
