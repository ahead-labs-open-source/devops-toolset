"""linux module literals"""

from devops_toolset.core.app import App
from devops_toolset.core.ValueDictsBase import ValueDictsBase

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the linux module."""

    _info = {
        "deb_package_install_pre": "Preparing to install: {package}. Please wait...",
        "deb_package_install_post": "Package {package} has been succesfully installed.",
        "edit_in_place_post": "Replaced {search_for}->{replace_with} completed in {path}"
    }
    _errors = {
        "deb_package_install_err": "An error occurred when trying to install {package}. Please check the logs.",
        "file_not_exist_err": "File {path} not found.",
        "edit_in_place_err": "Something went wrong replacing {search_for}->{replace_with} in {path}"
    }
