"""Unit core for the restapi file"""
import json
from unittest.mock import patch

import pytest

from devops_toolset.core import App
import devops_toolset as sut
from devops_toolset import encode
from tests.devops_platforms.azuredevops.conftest import mocked_requests_get, mocked_requests_get_ko
from devops_toolset.core import CommandsCore
from devops_toolset.devops_platforms.azuredevops import Commands as PlatformSpecificCommands

app: App = App()
commands = CommandsCore([PlatformSpecificCommands])


# region generate_authentication_header


def test_generate_authentication_header_given_name_and_token_then_generate_header(platformdata):
    """ Given user_name and access_token, then encodes and generates authentication code """
    # Arrange
    user_name = platformdata.user_name
    access_token = platformdata.access_token
    token_base_64 = f"{user_name}:{access_token}"
    basic_auth_token = f"Basic {encode(token_base_64)}"
    expected_auth_token = {"Authorization": basic_auth_token}
    # Act
    result = sut.generate_authentication_header(user_name, access_token)
    # Assert
    assert result == expected_auth_token


# endregion generate_authentication_header

# region call_api

@patch("devops_toolset.devops_platforms.azuredevops.restapi.generate_authentication_header")
@patch("logging.info")
@patch("requests.get", side_effect=mocked_requests_get)
def test_call_api_given_command_and_credentials_when_status_code_is_200_then_return_response(request_get_mock,
                                                                                             logging_mock,
                                                                                             generate_mock,
                                                                                             platformdata):
    """ Given parameters, when request return status code 200, then return the response """
    # Arrange
    headers = "my_headers"
    generate_mock.return_value = headers
    command = "my_command"
    # Act
    sut.call_api(command, platformdata.user_name, platformdata.access_token)
    # Assert
    request_get_mock.assert_called_once_with(command, headers=headers)


@patch("devops_toolset.devops_platforms.azuredevops.restapi.generate_authentication_header")
@patch("logging.info")
@patch("requests.get", side_effect=mocked_requests_get_ko)
def test_call_api_given_command_and_credentials_when_status_code_is_not_200_then_raise_value_error(request_get_mock,
                                                                                             logging_mock,
                                                                                             generate_mock,
                                                                                             platformdata):
    """ Given parameters, when request return status code not 200, then raises a ValueError """
    # Arrange
    headers = "my_headers"
    generate_mock.return_value = headers
    command = "my_command"
    # Act
    with pytest.raises(ValueError):
        sut.call_api(command, platformdata.user_name, platformdata.access_token)
        # Assert
        request_get_mock.assert_called_once_with(command, headers=headers)

# endregion call_api

# region get_build_list


@patch("devops_toolset.devops_platforms.azuredevops.restapi.call_api")
def test_get_build_list_given_args_call_api_with_command_and_credentials(call_api_mock, platformdata):
    """ Given organization and credentials, then retrieves command and calls api """
    # Arrange
    organization = platformdata.organization
    project = platformdata.project
    user_name = platformdata.user_name
    access_token = platformdata.access_token
    command = commands.get("azdevops_rest_get_build_list").format(organization=organization, project=project)
    # Act
    sut.get_build_list(organization, project, user_name, access_token)
    # Assert
    call_api_mock.assert_called_once_with(command, user_name, access_token)

# endregion get_build_list

# region get_build


@patch("devops_toolset.devops_platforms.azuredevops.restapi.call_api")
def test_get_build_given_args_call_api_with_args(call_api_mock, platformdata, artifactsdata):
    """ Given parameters, then retrieves command and calls api """
    # Arrange
    organization = platformdata.organization
    project = platformdata.project
    user_name = platformdata.user_name
    access_token = platformdata.access_token
    artifact_name = artifactsdata.artifact_name
    build_id = artifactsdata.build_id
    command = commands.get("azdevops_rest_get_build").format(
        organization=organization, project=project, build_id=build_id, artifact_name=artifact_name)
    # Act
    sut.get_build(organization, project, build_id, artifact_name, user_name, access_token)
    # Assert
    call_api_mock.assert_called_once_with(command, user_name, access_token)

# endregion get_build

# region get_last_build


@patch("devops_toolset.devops_platforms.azuredevops.restapi.get_last_build_id")
@patch("devops_toolset.devops_platforms.azuredevops.restapi.get_build")
def test_get_last_build_given_args_retrieves_build_id_and_calls_get_build(get_build_mock, get_last_build_mock,
                                                                          platformdata, artifactsdata):
    """ Given parameters, then retrieves build id and calls get_build """
    # Arrange
    organization = platformdata.organization
    project = platformdata.project
    user_name = platformdata.user_name
    access_token = platformdata.access_token
    artifact_name = artifactsdata.artifact_name
    build_id = artifactsdata.build_id
    get_last_build_mock.return_value = build_id
    # Act
    sut.get_last_build(organization, project, artifact_name, user_name, access_token)
    # Assert
    get_build_mock.assert_called_once_with(organization, project, build_id, artifact_name, user_name, access_token)

# endregion get_last_build

# region get_last_build_id


@patch("devops_toolset.devops_platforms.azuredevops.restapi.get_build_list")
def test_get_last_build_id_given_args_when_build_list_is_empty_then_return_none(get_build_list_mock, platformdata):
    """ Given args, when get_build_list returns no builds, then return None"""
    # Arrange
    organization = platformdata.organization
    project = platformdata.project
    user_name = platformdata.user_name
    access_token = platformdata.access_token
    build_list = json.loads("{\"count\": 0}")
    get_build_list_mock.return_value = build_list
    # Act
    result = sut.get_last_build_id(organization, project, user_name, access_token)
    # Assert
    assert result is None


@patch("devops_toolset.devops_platforms.azuredevops.restapi.get_build_list")
def test_get_last_build_id_given_args_when_build_list_is_not_empty_then_return_first_build_id(get_build_list_mock,
                                                                                              platformdata,
                                                                                              artifactsdata):
    """ Given args, when get_build_list returns builds, then return the first build id"""
    # Arrange
    organization = platformdata.organization
    project = platformdata.project
    user_name = platformdata.user_name
    access_token = platformdata.access_token
    build_list = json.loads("{\"count\": 1, \"value\": [{\"id\": \"123456\"}]}")
    get_build_list_mock.return_value = build_list
    # Act
    result = sut.get_last_build_id(organization, project, user_name, access_token)
    # Assert
    assert result == artifactsdata.build_id

# endregion get_last_build_id

# region get_artifact


@patch("devops_toolset.devops_platforms.azuredevops.restapi.get_build")
@patch("devops_toolset.devops_platforms.azuredevops.restapi.generate_authentication_header")
@patch("devops_toolset.filesystem.paths.download_file")
def test_get_artifact_given_args_when_get_build_returns_download_url_then_calls_download_file(download_file_mock,
    auth_header_mock, get_build_mock, platformdata, artifactsdata):
    """ Given arguments, when get_build retrieves a build with download url, then calls filesystem.download_file """
    # Arrange
    organization = platformdata.organization
    project = platformdata.project
    user_name = platformdata.user_name
    access_token = platformdata.access_token
    build_id = artifactsdata.build_id
    artifact_name = artifactsdata.artifact_name
    destination = "path/to/destination"
    headers = "my_headers"
    build = json.loads("{\"resource\": {\"downloadUrl\": \"my_url\"}}")
    get_build_mock.return_value = build
    auth_header_mock.return_value = headers
    # Act
    sut.get_artifact(organization, project, build_id, artifact_name, destination, user_name, access_token)
    # Assert
    download_file_mock.assert_called_once_with("my_url", destination, f"{artifact_name}.zip", headers)

# endregion get_artifact

# region get_last_artifact

@patch("devops_toolset.devops_platforms.azuredevops.restapi.get_last_build_id")
@patch("devops_toolset.devops_platforms.azuredevops.restapi.get_artifact")
def test_get_last_artifact_given_args_when_last_build_id_retrieved_then_calls_get_artifact(get_artifact_mock,
    get_last_build_id_mock, platformdata, artifactsdata):
    """ Given args, when last build id is retrieved, then calls get_artifact """
    # Arrange
    organization = platformdata.organization
    project = platformdata.project
    user_name = platformdata.user_name
    access_token = platformdata.access_token
    build_id = artifactsdata.build_id
    artifact_name = artifactsdata.artifact_name
    destination = "path/to/destination"
    get_last_build_id_mock.return_value = build_id
    # Act
    sut.get_last_artifact(organization, project, artifact_name, destination, user_name, access_token)
    # Assert
    get_artifact_mock.assert_called_once_with(organization, project, build_id, artifact_name, destination, user_name,
                                              access_token)
# endregion get_last_artifact


