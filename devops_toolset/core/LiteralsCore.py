"""Literals for the package."""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class LiteralsCore(ValueDictsBase):
    """Core literals for the package.


    1. Create an instance of the LiteralsCore class (this class).
    2. Pass as a parameter list all Literals classes you want to include.

        from devops_toolset.core.LiteralsCore import LiteralsCore
        from wordpress.Literals import Literals as WpLiterals

        literals = LiteralsCore([WpLiterals])

    3. Get a literal by it's key.

        literals.get("err_1")
    """

    # Add your core literal dictionaries here
    _debug = {
        "function_params": _("Parameters passed to the function:"),
    }
    _info = {}
    _errors = {}
