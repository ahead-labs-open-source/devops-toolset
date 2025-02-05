"""linux module commands"""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Commands(ValueDictsBase):
    """Commands for the linux module."""

    # Add your linux commands dictionaries here
    _commands = {
        "create_env_variable": "export {variable_name}={variable_value}",
        "deb_which": "which {package}",
        "deb_package_install": "sudo apt install -y {package} {version}",
        "edit_in_place": "sed -i 's/{search_for}/{replace_with}/g' {file_path}"
    }
