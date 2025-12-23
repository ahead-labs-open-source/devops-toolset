"""Unit core for the sonarx file"""

import pathlib
import devops_toolset.devops_platforms.sonarx as sut
from unittest.mock import patch
from tests.devops_platforms.conftest import mocked_requests_get
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.devops_platforms.literals import Literals as DevopsLiterals


literals = LiteralsCore([DevopsLiterals])

# region get_quality_gate_status()


@patch("requests.get", side_effect=mocked_requests_get)
@patch("devops_toolset.devops_platforms.sonarx.logging.info")
@patch("devops_toolset.devops_platforms.sonarx.logging.error")
@patch("devops_toolset.devops_platforms.sonarx.read_sonar_properties_file")
@patch("devops_toolset.devops_platforms.sonarx.generate_branch_segment")
def test_get_quality_gate_status_given_branch_then_reads_sonar_config_file(
        branch_function, file_function, logger_error, logger_info, requests_get, sonarxdata):
    """Given the path to the Sonar* config file, it reads its properties"""

    # Arrange
    branch_function.return_value = f"&branch={sonarxdata.branch_feature}"
    file_function.return_value = (sonarxdata.sonar_url, sonarxdata.sonar_project_key, sonarxdata.sonar_organization)

    # Act
    sut.get_quality_gate_status(sonarxdata.properties_file_path, sonarxdata.token, sonarxdata.branch_feature)

    # Assert
    sut.read_sonar_properties_file.assert_called_once_with(sonarxdata.properties_file_path)


@patch("requests.get", side_effect=mocked_requests_get)
@patch("devops_toolset.devops_platforms.sonarx.logging.error")
@patch("devops_toolset.devops_platforms.sonarx.logging.info")
@patch("devops_toolset.devops_platforms.sonarx.read_sonar_properties_file")
@patch("devops_toolset.devops_platforms.sonarx.generate_branch_segment")
def test_get_quality_gate_status_given_branch_when_passing_qg_then_logs_info(
        branch_function, file_function, logging_info, logging_error, requests_get, sonarxdata):
    """Given a branch, when passing the quality gate, logs info"""

    # Arrange
    branch_function.return_value = f"&branch={sonarxdata.branch_feature}"
    file_function.return_value = (sonarxdata.sonar_url, sonarxdata.sonar_project_key_ok, sonarxdata.sonar_organization)

    # Act
    sut.get_quality_gate_status(sonarxdata.properties_file_path, sonarxdata.token, sonarxdata.branch_feature)

    # Assert
    logging_info.assert_called_with(literals.get("sonar_qg_ok"))


@patch("requests.get", side_effect=mocked_requests_get)
@patch("devops_toolset.devops_platforms.sonarx.logging.error")
@patch("devops_toolset.devops_platforms.sonarx.logging.info")
@patch("devops_toolset.devops_platforms.sonarx.read_sonar_properties_file")
def test_get_quality_gate_status_given_branch_when_not_passing_qg_then_logs_errors(
        file_function, logging_info, logging_error, requests_get, sonarxdata):
    """Given a branch, when not passing the quality gate, logs errors"""

    # Arrange
    file_function.return_value = \
        (sonarxdata.sonar_url, sonarxdata.sonar_project_key_error, sonarxdata.sonar_organization)

    # Act
    sut.get_quality_gate_status(sonarxdata.properties_file_path, sonarxdata.token, sonarxdata.branch_feature)

    # Assert
    logging_error.assert_called()


# endregion

# region read_sonar_properties_file()


def test_read_sonar_properties_given_file_returns_tuple(sonarxdata, tmp_path):
    """Given a properties file, it returns a tuple with needed information"""

    # Arrange
    properties_file_path = pathlib.Path.joinpath(tmp_path, sonarxdata.properties_file_name)
    with open(str(properties_file_path), "w") as properties_file:
        properties_file.write(sonarxdata.properties_file_data)

    # Act
    result = sut.read_sonar_properties_file(str(properties_file_path))

    # Assert
    assert result == (sonarxdata.sonar_url, sonarxdata.sonar_project_key, sonarxdata.sonar_organization)

# endregion

# region read_sonar_properties_file()


@patch("devops_toolset.tools.git.simplify_branch_name")
def test_generate_branch_segment_given_branch_when_pr_returns_pr_segment(simplify_function, sonarxdata):
    """Given a branch, when is a PR, it returns a PR compatible segment"""

    # Arrange
    pull_request = True
    simplify_function.return_value = sonarxdata.branch_feature

    # Act
    result = sut.generate_branch_segment(sonarxdata.branch_feature, pull_request)

    # Assert
    assert result == f"&pullRequest={sonarxdata.branch_feature}"


@patch("devops_toolset.tools.git.simplify_branch_name")
def test_generate_branch_segment_given_branch_when_no_pr_returns_no_pr_segment(simplify_function, sonarxdata):
    """Given a branch, when is not a PR, it returns a non PR compatible
    segment"""

    # Arrange
    pull_request = False
    simplify_function.return_value = sonarxdata.branch_feature

    # Act
    result = sut.generate_branch_segment(sonarxdata.branch_feature, pull_request)

    # Assert
    assert result == f"&branch={sonarxdata.branch_feature}"


# endregion
