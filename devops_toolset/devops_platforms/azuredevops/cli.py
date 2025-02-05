"""Artifacts-related functionality"""

import devops_toolset.tools.cli as cli
from devops_toolset.core.app import App
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.devops_platforms.azuredevops.Literals import Literals as PlatformSpecificLiterals
from devops_toolset.devops_platforms.azuredevops.commands import Commands as PlatformSpecificCommands
import logging


app: App = App()
literals = LiteralsCore([PlatformSpecificLiterals])
commands = CommandsCore([PlatformSpecificCommands])


def download_artifact_from_feed(feed_config: dict, destination_path: str, **kwargs):
    """Downloads an artifact from a feed

    Args:
        feed_config: Feed configuration.
        destination_path: Path where the artifact will be downloaded.
        kwargs: Platform-specific arguments.
    """
    if "azdevops_token" not in kwargs:
        logging.error(literals.get("azdevops_token_not_found"))
        logging.warning(literals.get("azdevops_download_package_manually"))
        return

    azdevops_token = kwargs["azdevops_token"]
    cli.call_subprocess(commands.get("azdevops_cli_login")
                        .format(token=azdevops_token, organization=feed_config["organization_url"]))

    cli.call_subprocess(commands.get("azdevops_cli_universal_download")
                        .format(feed=feed_config["name"],
                                name=feed_config["package"],
                                path=f"\"{destination_path}\"",
                                version=feed_config["version"],
                                organization=feed_config["organization_url"]))


if __name__ == "__main__":
    help(__name__)
