""" Unit-core for the linux/software-installer.py module"""

from unittest.mock import patch, call, ANY
import pytest
import devops_toolset.project_types.linux.software_installer as sut
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.linux.commands import Commands as LinuxCommands
from devops_toolset.project_types.linux.literals import Literals as LinuxLiterals
from devops_toolset.core.app import App

app: App = App()
literals = LiteralsCore([LinuxLiterals])
commands = CommandsCore([LinuxCommands])

# region check_and_update_instance_software


@patch("devops_toolset.project_types.linux.software_installer.install_package")
def test_check_and_update_instance_software_given_software_config_when_no_content_then_avoid_call_to_install_package(
        install_package_mock):
    """ Given software_config dict, when no content, should not call install_package"""
    # Arrange
    software_dict = {}
    # Act
    sut.check_and_update_instance_software(software_dict)
    # Assert
    install_package_mock.assert_not_called()


@patch("devops_toolset.project_types.linux.software_installer.install_package")
def test_check_and_update_instance_software_given_software_config_then_call_to_install_package(
        install_package_mock):
    """ Given software_config dict should not call install_package"""
    # Arrange
    software_dict = {"software1": "v1.0", "software2": "latest"}
    # Act
    sut.check_and_update_instance_software(software_dict)
    # Assert
    calls = [call("software1", "v1.0"), call("software2", "latest")]
    install_package_mock.assert_has_calls(calls)


# endregion check_and_update_instance_software

# region check_package_installed

@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@pytest.mark.parametrize("value, expected_result", [("/usr/bin/package_that_exists", True), (None, False)])
def test_check_package_installed_given_package_when_package_exist_then_returns_true(call_subprocess_with_result_mock,
                                                                                    value, expected_result):
    """ Given a package name, executes the check command and if package returns a value, then returns True """
    # Arrange
    package = "package_that_exists"
    call_subprocess_with_result_mock.return_value = value
    # Act
    result = sut.check_package_installed(package)
    # Assert
    assert result == expected_result


# endregion check_package_installed

# region convert_version_parameter


@pytest.mark.parametrize("value, expected_result", [(None, ""), ("latest", ""), ("0.1", "--version \"0.1\"")])
def test_convert_version_parameter_given_value_then_return_parameter_value(value, expected_result):
    """ Given value string, when None or "latest", then should return empty string. Version parameter otherwise """
    # Arrange
    # Act
    result = sut.convert_version_parameter(value)
    # Assert
    assert result == expected_result


# endregion convert_version_parameter

# region install_package

@patch("devops_toolset.project_types.linux.software_installer.convert_version_parameter")
@patch("devops_toolset.tools.cli.call_subprocess")
def test_install_package_given_package_and_version_then_calls_deb_package_install_command(
        subprocess_mock, convert_version_parameter_mock):
    """ Given package and version, should call deb_package_install command"""
    # Arrange
    version = "1.0"
    version_parameter = f"--version {version}"
    package = "my_package"
    convert_version_parameter_mock.return_value = version_parameter
    command = commands.get("deb_package_install").format(package=package, version=version_parameter)
    # Act
    sut.install_package(package, version)
    # Assert
    subprocess_mock.assert_called_with(command, log_before_process=ANY, log_after_err=ANY, log_after_out=ANY)


# endregion install_package


