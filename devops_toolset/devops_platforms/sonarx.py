"""sonarcloud.io / SonarQube tools"""

from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.devops_platforms.Literals import Literals as DevopsLiterals
from devops_toolset.tools.xcoding64 import encode
from devops_toolset.devops_platforms.constants import Urls
from devops_toolset.tools.git import simplify_branch_name
import configparser
import devops_toolset.core.log_tools as log_tools
import logging
import requests

app: App = App()
literals = LiteralsCore([DevopsLiterals])
platform_specific = app.load_platform_specific("environment")


def get_quality_gate_status(properties_file_path: str, token: str, branch: str = None, pull_request: bool = False):
    """Gets the status of the quality gate of a project

    Args:
        properties_file_path: Path to sonar-project.properties file. Keys
            sonar.projectKey and sonar.organization are mandatory.
        token: SonarCloud token used for authentication
        branch: Git branch name to get the quality gate for. If None, master
            will be assumed.
        pull_request: True if the analysis was originated by a pull request.
    """

    log_tools.log_indented_list(literals.get("function_params"),
                                log_tools.get_parameter_value_list(locals()),
                                log_tools.LogLevel.debug)

    logging.info(literals.get("sonar_getting_qg").format(branch=branch))
    logging.info(literals.get("sonar_pr_mode").format(pull_request=pull_request))

    logging.info(literals.get("sonar_config_file").format(file=properties_file_path))
    sonar_url, sonar_project_key, sonar_organization = read_sonar_properties_file(properties_file_path)

    get_project_quality_gate_status(sonar_url, sonar_project_key, token, branch, pull_request)


def get_project_quality_gate_status(
        url: str, project_key: str, token: str, branch: str = None, pull_request: bool = False):
    """Gets the status of the quality gate of a project

    Args:
        url: Url base for the SonarX service.
        project_key: SonarX project key to get quality gate from.
        token: SonarX token used for authentication.
        branch: Git branch name to get the quality gate for. If None, master
            will be assumed.
        pull_request: True if the analysis was originated by a pull request.
    """

    log_tools.log_indented_list(literals.get("function_params"),
                                log_tools.get_parameter_value_list(locals()),
                                log_tools.LogLevel.debug)

    token_base64 = encode(f"{token}:")
    basic_auth_token = f"Basic {token_base64}"
    headers = {"Authorization": basic_auth_token}
    branch_segment = generate_branch_segment(branch, pull_request)

    url = f"{url}{Urls.SONAR_QUALITY_GATE_PARTIAL_URL}{project_key}{branch_segment}"
    logging.info(literals.get("sonar_qg_url").format(url=url))

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(literals.get("sonar_unexpected_status_code").format(statusCode=response.status_code))

    quality_gate_data = response.json()
    logging.info(literals.get("sonar_qg_json").format(json=quality_gate_data))

    if quality_gate_data["projectStatus"]["status"] == "OK":
        logging.info(literals.get("sonar_qg_ok"))
    else:
        for condition in quality_gate_data["projectStatus"]["conditions"]:
            if condition["status"] == "ERROR":
                logging.error(literals.get("sonar_invalid_metric").format(
                    metricKey=condition["metricKey"],
                    actualValue=condition["actualValue"],
                    comparator=condition["comparator"],
                    errorThreshold=condition["errorThreshold"]))

        platform_specific.end_task(platform_specific.ResultType.fail)


def read_sonar_properties_file(path: str):
    """Reads a sonar-project.properties file

    It adds a temporary dummy section to be correctly parsed by configParser

    Args:
        path: Path to the sonar-project.properties file

    Returns:
        Tuple containing url, projectKey, organization
    """

    with open(path, "r") as file:
        data = f"[temp]\n{file.read()}"

    properties_file_parser = configparser.ConfigParser()
    properties_file_parser.read_string(data)

    sonar_url = properties_file_parser.get("temp", "sonar.host.url")
    sonar_project_key = properties_file_parser.get("temp", "sonar.projectKey")
    sonar_organization = properties_file_parser.get("temp", "sonar.organization")

    return sonar_url, sonar_project_key, sonar_organization


def generate_branch_segment(branch: str = "master", pull_request: bool = False):
    """Generates the branch segment or the URL used to request the quality gate
    status

    Args:
        branch: Git branch. If None, master will be assumed.
        pull_request: True if the analysis was originated by a pull request
    """

    branch = simplify_branch_name(branch)

    if pull_request:
        branch = branch.replace("pull/", "")
        return f"&pullRequest={branch}"
    else:
        return f"&branch={branch}"


if __name__ == "__main__":
    help(__name__)
