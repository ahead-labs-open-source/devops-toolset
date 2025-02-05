""" Unit tests for the angular/ci_pipeline_kickoff.py module"""

from unittest.mock import patch
import devops_toolset as sut
from devops_toolset.core import CommandsCore
from devops_toolset.core import LiteralsCore
from devops_toolset.project_types.angular import Commands as AngularCommands
from devops_toolset.project_types.angular.Literals import Literals as AngularLiterals
from devops_toolset.core import App

app: App = App()
literals = LiteralsCore([AngularLiterals])
commands = CommandsCore([AngularCommands])

# region main()


@patch("devops_toolset.configure.main")
def test_main_calls_devops_toolset_configure_main(configure_main_mock):
    """ Given devops_platform argument, calls configure.main method """

    # Arrange
    devops_platform = "platform1"
    packagejson_path = None
    current_branch = None
    language = "en"

    # Act
    sut.main(devops_platform, packagejson_path, current_branch)

    # Assert
    configure_main_mock.assert_called_with(devops_platform=devops_platform, language=language)


@patch("devops_toolset.project_types.angular.utils.get_packagejson_project_version")
def test_main_calls_devops_toolset_project_types_angular_utils_get_packagejson_project_version(project_version_mock):
    """ Given devops_platform argument, calls configure.main method """

    # Arrange
    devops_platform = None
    packagejson_path = "pathto/package.json"
    current_branch = None

    # Act
    sut.main(devops_platform, packagejson_path, current_branch)

    # Assert
    project_version_mock.assert_called_with(packagejson_path)


@patch("devops_toolset.tools.git.get_current_branch_simplified")
def test_main_calls_devops_toolset_tools_git_get_current_branch_simplified(branch_mock):
    """ Given devops_platform argument, calls configure.main method """

    # Arrange
    devops_platform = None
    packagejson_path = None
    current_branch = "refs/heads/feature/myfeature"

    # Act
    sut.main(devops_platform, packagejson_path, current_branch)

    # Assert
    branch_mock.assert_called_with(branch=current_branch)

# endregion main()
