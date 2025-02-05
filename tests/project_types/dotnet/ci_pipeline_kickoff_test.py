""" Unit tests for the dotnet/ci_pipeline_kickoff.py module"""

from unittest.mock import patch
import devops_toolset as sut
from devops_toolset.core import CommandsCore
from devops_toolset.core import LiteralsCore
from devops_toolset import Commands as DotnetCommands
from devops_toolset import Literals as DotnetLiterals
from devops_toolset.core import App

app: App = App()
literals = LiteralsCore([DotnetLiterals])
commands = CommandsCore([DotnetCommands])

# region main()


@patch("devops_toolset.configure.main")
def test_main_calls_devops_toolset_configure_main(configure_main_mock):
    """ Given devops_platform argument, calls configure.main method """

    # Arrange
    devops_platform = "platform1"
    language = "en"

    # Act
    sut.main(devops_platform, None, None, None, True)

    # Assert
    configure_main_mock.assert_called_with(devops_platform=devops_platform, language=language)


@patch("devops_toolset.project_types.dotnet.utils.get_csproj_project_version")
def test_main_calls_get_csproj_project_version(get_csproj_project_version_mock):
    """ Given skip_get_public_ip_address argument, should call get_public_ip_method when false method """

    # Arrange
    csproj_path = "pathto/csproj"

    # Act
    sut.main(None, csproj_path, None, None, True)

    # Assert
    get_csproj_project_version_mock.assert_called_with(csproj_path=csproj_path)


@patch("devops_toolset.tools.git.get_current_branch_simplified")
def test_main_calls_get_current_branch_simplified(get_current_branch_mock):
    """ Given skip_get_public_ip_address argument, should call get_public_ip_method when false method """
    # Arrange
    current_branch = "refs/heads/feature/myfeature"

    # Act
    sut.main(None, None, current_branch, None, True)

    # Assert
    get_current_branch_mock.assert_called_with(branch=current_branch)


@patch("devops_toolset.project_types.dotnet.entity_framework.check_branch_suitableness_for_migrations")
@patch("devops_toolset.tools.git.get_current_branch_simplified")
def test_main_calls_check_branch_suitableness_for_migrations(get_current_branch_mock, check_branch_mock):
    """ Given skip_get_public_ip_address argument, should call get_public_ip_method when false method """
    # Arrange
    current_branch = "refs/heads/feature/myfeature"
    current_branch_simplified = "feature/myfeature"
    get_current_branch_mock.return_value = current_branch_simplified
    migrations_suitable_branches = ["dev", "main"]

    # Act
    sut.main(None, None, current_branch, migrations_suitable_branches, True)

    # Assert
    check_branch_mock.assert_called_with(
        current_simplified_branch=current_branch_simplified,
        suitable_branches=migrations_suitable_branches
    )


@patch("devops_toolset.tools.http_protocol.get_public_ip_address")
def test_main_calls_get_public_ip_address(get_public_ip_address_mock):
    """ Given skip_get_public_ip_address argument, should call get_public_ip_method when false method """

    # Arrange

    # Act
    sut.main(None, None, None, None, False)

    # Assert
    get_public_ip_address_mock.assert_called()

# endregion main()
