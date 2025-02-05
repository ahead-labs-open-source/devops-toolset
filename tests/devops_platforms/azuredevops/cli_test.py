"""Unit core for the cli.py file"""

import json
from unittest.mock import patch, call

from devops_toolset.core import App
from devops_toolset.core import CommandsCore
from devops_toolset.core import LiteralsCore
from devops_toolset.devops_platforms.azuredevops import Literals as PlatformSpecificLiterals
from devops_toolset.devops_platforms.azuredevops import Commands as PlatformSpecificCommands

import devops_toolset as sut

app: App = App()
literals = LiteralsCore([PlatformSpecificLiterals])
commands = CommandsCore([PlatformSpecificCommands])

# region download_artifact_from_feed()


@patch("logging.warning")
@patch("logging.error")
def test_download_artifact_from_feed_given_kwargs_when_not_azdevops_token_then_logs(
        logging_err_mock, logging_warn_mock, artifactsdata):
    """Given kwargs, when not azdevops_token present, then should log and return"""
    # Arrange
    kwargs = dict()
    kwargs["not_azdevops_token"] = "some_value"
    feed_config = json.loads(artifactsdata.feed_content)
    destination_path = artifactsdata.artifact_destination_path
    expected_error = literals.get("azdevops_token_not_found")
    # Act
    sut.download_artifact_from_feed(feed_config, destination_path, **kwargs)
    # Assert
    logging_err_mock.assert_called_once_with(expected_error)


@patch("devops_toolset.tools.cli.call_subprocess")
def test_download_artifact_from_feed_given_kwargs_when_azdevops_token_calls_commands(subprocess_mock, artifactsdata):
    """Given kwargs, when azdevops_token present, then calls azdevops_login and azdevops_universal_download"""
    # Arrange
    kwargs = dict()
    kwargs["azdevops_token"] = "my_token"
    feed_config = json.loads(artifactsdata.feed_content)
    destination_path = artifactsdata.artifact_destination_path
    expected_azdevops_login_command = commands.get("azdevops_cli_login")\
        .format(token=kwargs["azdevops_token"], organization=feed_config["organization_url"])
    expected_azdevops_univ_download = commands.get("azdevops_cli_universal_download")\
        .format(feed=feed_config["name"],
                name=feed_config["package"],
                path=f"\"{destination_path}\"",
                version=feed_config["version"],
                organization=feed_config["organization_url"])

    # Act
    sut.download_artifact_from_feed(feed_config, destination_path, **kwargs)
    # Assert
    expected_calls = [call(expected_azdevops_login_command), call(expected_azdevops_univ_download)]
    subprocess_mock.assert_has_calls(expected_calls)

# endregion
