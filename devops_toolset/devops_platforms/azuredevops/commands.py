"""Azure DevOps module commands"""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Commands(ValueDictsBase):
    """Commands for the Azure DevOps platform module."""

    # Add your Azure DevOps commands here
    _commands = {
        "azdevops_rest_get_build_list": "https://dev.azure.com/{organization}/{project}/_apis/build/builds",
        "azdevops_rest_get_build": "https://dev.azure.com/{organization}/{project}/_apis/build/builds/{build_id}/"
                                   "artifacts?artifactName={artifact_name}",
        "azdevops_cli_login": "{token} | az devops login --organization {organization}",
        "azdevops_cli_universal_download": "az artifacts universal download --feed {feed} --name {name} --path {path} "
                                       "--version {version} --organization {organization}",
    }
