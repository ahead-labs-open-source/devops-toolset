""" Contains dotnet utilities """

import devops_toolset.tools.cli
from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.dotnet.Literals import Literals as DotnetLiterals
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.project_types.dotnet.commands import Commands as DotnetCommands

app: App = App()
literals = LiteralsCore([DotnetLiterals])
commands = CommandsCore([DotnetCommands])


def build(path: str, configuration: str = "Release", output: str = ".", framework: str = "net5.0",
          runtime: str = "linux-x64", with_restore: bool = False, force: bool = False, debug: bool = False):
    """ Performs a dotnet build in the desired path
    Arguments:
        path: The path where build will be executed.
        configuration: The configuration used for build. Default is "Release".
        output: Adds --output argument. Specifies the output path of the build command. Defaults "."
        framework: The dotnet framework used to build. Default is "net5.0".
        runtime: The runtime used to build. Default is "linux-x64".
        with_restore: Adds --no-restore argument when False. Default to False.
        force: Adds --force argument.
        debug: Enables diagnostic logs to the command.

    More info: https://docs.microsoft.com/es-es/dotnet/core/tools/dotnet-build

    """
    devops_toolset.tools.cli.call_subprocess(commands.get("dotnet_build").format(
        force=convert_force_parameter(force),
        path=path,
        debug=convert_debug_parameter(debug),
        configuration=configuration,
        output=output,
        framework=framework,
        runtime=runtime,
        with_restore=convert_with_restore_parameter(with_restore)),
        log_before_process=[literals.get("dotnet_build_before").format(path=path)],
        log_after_err=[literals.get("dotnet_build_err").format(path=path)])


def convert_debug_parameter(value: bool) -> str:
    """ Converts force boolean into the correspondent parameter
    Arguments:
        value: The value to be converted

    Returns: --force when true, empty value otherwise
    """
    if value:
        return "--verbosity=diagnostic"
    return ""


def convert_force_parameter(value: bool) -> str:
    """ Converts force boolean into the correspondent parameter
    Arguments:
        value: The value to be converted

    Returns: --force when true, empty value otherwise
    """
    if value:
        return "--force"
    return ""


def convert_with_restore_parameter(value: bool) -> str:
    """ Converts with_restore boolean into the correspondent parameter
    Arguments:
        value: The value to be converted

    Returns: --no-restore when false, empty value otherwise
    """
    if not value:
        return "--no-restore"
    return ""


def restore(path: str, force: bool = False, debug: bool = False):
    """ Performs a dotnet restore in the desired path
    Arguments:
        path: The path where restore will be executed.
        force: Adds --force argument.
        debug: Enables diagnostic logs to the command.

    More info: https://docs.microsoft.com/es-es/dotnet/core/tools/dotnet-restore

    """
    devops_toolset.tools.cli.call_subprocess(commands.get("dotnet_restore").format(
        force=convert_force_parameter(force),
        path=path,
        debug=convert_debug_parameter(debug)),
        log_before_process=[literals.get("dotnet_restore_before").format(path=path)],
        log_after_err=[literals.get("dotnet_restore_err").format(path=path)])


if __name__ == "__main__":
    help(__name__)
