"""Environment-related functionality for Aws"""

from enum import Enum
from devops_toolset.core.app import App
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.devops_platforms.Literals import Literals as CommonLiterals
from devops_toolset.devops_platforms.aws.Literals import Literals as AwsLiterals
from devops_toolset.project_types.linux.commands import Commands as LinuxCommands
import devops_toolset.devops_platforms.common
import logging
import os

app: App = App()
literals = LiteralsCore([CommonLiterals, AwsLiterals])
linux_commands = CommandsCore([LinuxCommands])


class ResultType(Enum):
    """Result types for a task"""
    success = "Succeeded"
    partial_success = "SucceededWithIssues"
    fail = "Failed"


def create_environment_variables(key_value_pairs: dict):
    """Creates environment variables

    Args:
        key_value_pairs: Key-value pair dictionary
    """

    for key, value in key_value_pairs.items():
        logging.info(literals.get("platform_created_ev").format(key=key, value=value))
        os.environ[key] = value


def end_task(result_type: ResultType):
    """Ends the current task

    Args:
        result_type: Result type of the task
    """

    if result_type == ResultType.fail:
        raise EnvironmentError()


def get_platform_variable_dict() -> dict:
    """Gets all keys for the environment variables defined by default in the
    platform. Values are replaced automatically by AWS before the script is
    executed.

    More info at:
        https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-variables.html#reference-variables-list

    Returns
        List with all variables
    """

    return {
        "BuildVariables.EnvVar": "#{BuildVariables.EnvVar}",
        "codepipeline.PipelineExecutionId": "#{codepipeline.PipelineExecutionId}",
        "DeployVariables.OperationId": "#{DeployVariables.OperationId}",
        "DeployVariables.StackName": "#{DeployVariables.StackName}",
        "DeployVariables.StackSetId": "#{DeployVariables.StackSetId}",
        "SourceVariables.AuthorDate": "#{SourceVariables.AuthorDate}",
        "SourceVariables.BranchName": "#{SourceVariables.BranchName}",
        "SourceVariables.CommitId": "#{SourceVariables.CommitId}",
        "SourceVariables.CommitMessage": "#{SourceVariables.CommitMessage}",
        "SourceVariables.CommitterDate": "#{SourceVariables.CommitterDate}",
        "SourceVariables.CommitUrl": "#{SourceVariables.CommitUrl}",
        "SourceVariables.ConnectionArn": "#{SourceVariables.ConnectionArn}",
        "SourceVariables.ETag": "#{SourceVariables.ETag}",
        "SourceVariables.FullRepositoryName": "#{SourceVariables.FullRepositoryName}",
        "SourceVariables.ImageDigest": "#{SourceVariables.ImageDigest}",
        "SourceVariables.ImageTag": "#{SourceVariables.ImageTag}",
        "SourceVariables.ImageURI": "#{SourceVariables.ImageURI}",
        "SourceVariables.RegistryId": "#{SourceVariables.RegistryId}",
        "SourceVariables.RepositoryName": "#{SourceVariables.RepositoryName}",
        "SourceVariables.VersionId": "#{SourceVariables.VersionId}",
        "TestVariables.testRunId": "#{TestVariables.testRunId}",
    }


def log_environment_variables(platform_keys: dict):
    """Logs all environment variables for this platform and process.

    Args:
        platform_keys: List of platform variables.
    """

    devops_toolset.devops_platforms.common.log_environment_variables(platform_keys)


if __name__ == "__main__":
    help(__name__)
