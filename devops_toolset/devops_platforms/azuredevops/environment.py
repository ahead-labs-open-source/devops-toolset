"""Environment-related functionality for Azure DevOps"""
import devops_toolset.devops_platforms.common
from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.devops_platforms.Literals import Literals as CommonLiterals
from devops_toolset.devops_platforms.azuredevops.Literals import Literals as AzureDevOpsLiterals
from enum import Enum
import logging
import sys

app: App = App()
literals = LiteralsCore([CommonLiterals, AzureDevOpsLiterals])


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
        sys.stdout.write(f"##vso[task.setvariable variable={key}]{value}\n")


def end_task(result_type: ResultType):
    """Ends the current task

    Args:
        result_type: Result type of the task
    """

    sys.stdout.write(f"##vso[task.complete result={result_type.value};]DONE\n")


def get_platform_variable_dict() -> dict:
    """Gets all keys for the environment variables defined by default in the
    platform. Values are replaced automatically by Azure DevOps before the
    script is executed.

    Note: Since Azure DevOps Pipelines expands variables only on the YAML file,
        you should copy and paste this dict there because calling this function
        will not expand values.

    More info at:
        https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables

    Returns
        List with all variables
    """

    return {
        "Agent.BuildDirectory": "$(Agent.BuildDirectory)",
        "Agent.ContainerMapping": "$(Agent.ContainerMapping)",
        "Agent.HomeDirectory": "$(Agent.HomeDirectory)",
        "Agent.Id": "$(Agent.Id)",
        "Agent.JobName": "$(Agent.JobName)",
        "Agent.JobStatus": "$(Agent.JobStatus)",
        "Agent.MachineName": "$(Agent.MachineName)",
        "Agent.Name": "$(Agent.Name)",
        "Agent.OS": "$(Agent.OS)",
        "Agent.OSArchitecture": "$(Agent.OSArchitecture)",
        "Agent.TempDirectory": "$(Agent.TempDirectory)",
        "Agent.ToolsDirectory": "$(Agent.ToolsDirectory)",
        "Agent.WorkFolder": "$(Agent.WorkFolder)",
        "Build.ArtifactStagingDirectory": "$(Build.ArtifactStagingDirectory)",
        "Build.BuildId": "$(Build.BuildId)",
        "Build.BuildNumber": "$(Build.BuildNumber)",
        "Build.BuildUri": "$(Build.BuildUri)",
        "Build.BinariesDirectory": "$(Build.BinariesDirectory)",
        "Build.ContainerId": "$(Build.ContainerId)",
        "Build.DefinitionName": "$(Build.DefinitionName)",
        "Build.DefinitionVersion": "$(Build.DefinitionVersion)",
        "Build.QueuedBy": "$(Build.QueuedBy)",
        "Build.QueuedById": "$(Build.QueuedById)",
        "Build.Reason": "$(Build.Reason)",
        "Build.Repository.Clean": "$(Build.Repository.Clean)",
        "Build.Repository.Git.SubmoduleCheckout": "$(Build.Repository.Git.SubmoduleCheckout)",
        "Build.Repository.ID": "$(Build.Repository.ID)",
        "Build.Repository.LocalPath": "$(Build.Repository.LocalPath)",
        "Build.Repository.Name": "$(Build.Repository.Name)",
        "Build.Repository.Provider": "$(Build.Repository.Provider)",
        "Build.Repository.Tfvc.Workspace": "$(Build.Repository.Tfvc.Workspace)",
        "Build.Repository.Uri": "$(Build.Repository.Uri)",
        "Build.RequestedFor": "$(Build.RequestedFor)",
        "Build.RequestedForEmail": "$(Build.RequestedForEmail)",
        "Build.RequestedForId": "$(Build.RequestedForId)",
        "Build.SourceBranch": "$(Build.SourceBranch)",
        "Build.SourceBranchName": "$(Build.SourceBranchName)",
        "Build.SourcesDirectory": "$(Build.SourcesDirectory)",
        "Build.SourceVersion": "$(Build.SourceVersion)",
        "Build.SourceVersionMessage": "$(Build.SourceVersionMessage)",
        "Build.StagingDirectory": "$(Build.StagingDirectory)",
        "Build.SourceTfvcShelveset": "$(Build.SourceTfvcShelveset)",
        "Build.TriggeredBy.BuildId": "$(Build.TriggeredBy.BuildId)",
        "Build.TriggeredBy.BuildNumber": "$(Build.TriggeredBy.BuildNumber)",
        "Build.TriggeredBy.DefinitionId": "$(Build.TriggeredBy.DefinitionId)",
        "Build.TriggeredBy.DefinitionName": "$(Build.TriggeredBy.DefinitionName)",
        "Build.TriggeredBy.ProjectID": "$(Build.TriggeredBy.ProjectID)",
        "Checks.StageAttempt": "$(Checks.StageAttempt)",
        "Common.TestResultsDirectory": "$(Common.TestResultsDirectory)",
        "Environment.Id": "$(Environment.Id)",
        "Environment.Name": "$(Environment.Name)",
        "Environment.ResourceId": "$(Environment.ResourceId)",
        "Environment.ResourceName": "$(Environment.ResourceName)",
        "Pipeline.Workspace": "$(Pipeline.Workspace)",
        "Strategy.CycleName": "$(Strategy.CycleName)",
        "Strategy.Name": "$(Strategy.Name)",
        "System.AccessToken": "$(System.AccessToken)",
        "System.Debug": "$(System.Debug)",
        "System.CollectionId": "$(System.CollectionId)",
        "System.CollectionUri": "$(System.CollectionUri)",
        "System.DefaultWorkingDirectory": "$(System.DefaultWorkingDirectory)",
        "System.DefinitionId": "$(System.DefinitionId)",
        "System.HostType": "$(System.HostType)",
        "System.JobAttempt": "$(System.JobAttempt)",
        "System.JobDisplayName": "$(System.JobDisplayName)",
        "System.JobId": "$(System.JobId)",
        "System.JobName": "$(System.JobName)",
        "System.PhaseAttempt": "$(System.PhaseAttempt)",
        "System.PhaseDisplayName": "$(System.PhaseDisplayName)",
        "System.PhaseName": "$(System.PhaseName)",
        "System.StageAttempt": "$(System.StageAttempt)",
        "System.StageDisplayName": "$(System.StageDisplayName)",
        "System.StageName": "$(System.StageName)",
        "System.PullRequest.IsFork": "$(System.PullRequest.IsFork)",
        "System.PullRequest.PullRequestId": "$(System.PullRequest.PullRequestId)",
        "System.PullRequest.PullRequestNumber": "$(System.PullRequest.PullRequestNumber)",
        "System.PullRequest.SourceBranch": "$(System.PullRequest.SourceBranch)",
        "System.PullRequest.SourceRepositoryURI": "$(System.PullRequest.SourceRepositoryURI)",
        "System.PullRequest.TargetBranch": "$(System.PullRequest.TargetBranch)",
        "System.TeamFoundationCollectionUri": "$(System.TeamFoundationCollectionUri)",
        "System.TeamProject": "$(System.TeamProject)",
        "System.TeamProjectId": "$(System.TeamProjectId)",
        "TF_BUILD": "$(TF_BUILD)",
    }


def log_environment_variables(platform_keys: dict):
    """Logs all environment variables for this platform and process.

    Args:
        platform_keys: dict with key-value pairs of platform variables.
    """

    devops_toolset.devops_platforms.common.log_environment_variables(platform_keys)


if __name__ == "__main__":
    help(__name__)
