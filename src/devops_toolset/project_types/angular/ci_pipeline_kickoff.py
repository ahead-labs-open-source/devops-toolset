"""This script kicks off a CI pipeline for Angular projects"""

import argparse
import devops_toolset.configure
import devops_toolset.tools.cli

from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.dotnet.Literals import Literals as DotnetLiterals
from devops_toolset.project_types.angular.utils import get_packagejson_project_version
from devops_toolset.tools.git import get_current_branch_simplified

app: App = App()
literals = LiteralsCore([DotnetLiterals])


def main(devops_platform: [str, None],
         packagejson_path: [str, None],
         current_branch: [str, None]):
    """Kick off the CI pipeline

    Args:
        devops_platform: Name of the DevOps platform to be set.
        packagejson_path: Path to the package.json file.
        current_branch: Name of the current branch
    """

    # Set DevOps current platform
    if devops_platform is not None:
        devops_toolset.configure.main(devops_platform=devops_platform, language="en")

    # Get project version from .csproj file
    if packagejson_path is not None:
        _ = devops_toolset.project_types.angular.utils.get_packagejson_project_version(packagejson_path)

    # Get current branch simplified
    if current_branch is not None:
        _ = devops_toolset.tools.git.get_current_branch_simplified(branch=current_branch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("devops_platform", default=None)
    parser.add_argument("--packagejson-path", default=None)
    parser.add_argument("--current-branch", default=None)
    args, args_unknown = parser.parse_known_args()

    devops_toolset.tools.cli.print_title(literals.get("dotnet_ci_title_pipeline_kickoff"))
    main(args.devops_platform,
         args.packagejson_path,
         args.current_branch)
