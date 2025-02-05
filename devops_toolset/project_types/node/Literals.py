"""node module literals"""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the node module."""

    _info = {
        "npm_run_before": _("Running npm task: {task}..."),
        "npm_run_after": _("npm task: {task} has completed successfully."),
        "npm_install_before": _("Npm install launched. This may take a while..."),
        "npm_install_after": _("Npm install completed successfully.")
    }
    _errors = {
        "npm_run_error": _("An error has occurred while running task {task}. See above log for more details."),
        "npm_install_error": _("Npm install has encountered an error. Please check above logs for more details.")
    }
