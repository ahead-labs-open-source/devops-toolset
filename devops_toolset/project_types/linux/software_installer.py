""" This script will hold tools to install and update software in a remote linux host """
from devops_toolset.core.app import App
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.linux.commands import Commands as LinuxCommands
from devops_toolset.project_types.linux.Literals import Literals as LinuxLiterals
from devops_toolset.tools import cli
import argparse
import json

app: App = App()
literals = LiteralsCore([LinuxLiterals])
commands = CommandsCore([LinuxCommands])


def check_and_update_instance_software(software_config: dict):
    """ Checks all software included on the software config dict. If a software doesn't exist or
    needs to be updated, it'll execute the neccessary sub-commands to install/update software required
    Args:
        software_config: Dict containing software configuration of the instance
    """
    for package, version in software_config.items():
        install_package(package, version)


def check_package_installed(package: str) -> bool:
    """ Checks if a concrete package is installed. Returns true if present, false otherwise.
    Args:
        package: The name of the package to be checked: For example: python3,
    """
    result = cli.call_subprocess_with_result(commands.get("deb_which").format(
        package=package))
    return result is not None


def convert_version_parameter(value: str) -> str:
    """ Converts a boolean value to a --silent string."""
    if value is not None and value != "latest":
        return f"--version \"{value}\""
    return ""


def install_package(package: str, version: str = None):
    """ Installs a package
        Omitting version will only check for latest version (by not targeting a concrete version)
     Args:
         package: The package that will be installed
         version: Target a concrete version
     """
    version = convert_version_parameter(version)

    cli.call_subprocess(commands.get("deb_package_install").format(package=package, version=version),
                        log_before_process=[literals.get("deb_package_install_pre").format(package=package)],
                        log_after_err=[literals.get("deb_package_install_err").format(package=package)],
                        log_after_out=[literals.get("deb_package_install_post").format(package=package)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("instance-config-path", action=tools.argument_validators.PathValidator)
    args, args_unknown = parser.parse_known_args()
    with open(args.instance_config_path) as instance_file:
        instance_dict = json.load(instance_file)
        check_and_update_instance_software(instance_dict["software-packages"])



