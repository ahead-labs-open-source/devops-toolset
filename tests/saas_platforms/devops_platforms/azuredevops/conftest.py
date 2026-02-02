"""Test configuration file for azuredevops/restapi module.

Add here whatever you want to pass as a fixture in your core."""

import pytest


class PlatformData(object):
    """Class used to create the platformdata fixture"""
    environment_variables_dict = {"env_var_1": "value1", "env_var_2": "value2"}
    environment_variables_dict1 = {"env_var_1": "value1"}
    description = "Lorem ipsum dolor sit amet"
    user_name = "user_name"
    access_token = "test_token"
    organization = "my_organization"
    project = "my_project"


class ArtifactsData(object):
    """Class used to create the artifactsdata fixture"""
    artifact_name = "my_artifact"
    build_id = "123456"
    artifact_destination_path = "/pathto/artifact/destination"
    feed_content = "{\"name\":\"feed_name\",\"package\":\"package_name\",\"version\":\"1.0.1\"," \
                   "\"organization_url\":\"https://my-organization\"}"


@pytest.fixture
def platformdata():
    """Sample data for testing"""
    return PlatformData()


@pytest.fixture
def artifactsdata():
    """Sample data for testing"""
    return ArtifactsData()


# region Mocks


def mocked_requests_get(url: str, *args, **kwargs):
    """Mock to replace requests.get()"""

    # Default values
    bytes_content = b"sample response in bytes"
    text_content = "sample text response"
    status_code = 200

    # Return instance
    return MockResponse(bytes_content, text_content, status_code)


def mocked_requests_get_ko(url: str, *args, **kwargs):
    """Mock to replace requests.get()"""

    # Default values
    bytes_content = b"bad response in bytes"
    text_content = "sample bad text response"
    status_code = 404

    # Return instance
    return MockResponse(bytes_content, text_content, status_code)


class MockResponse(object):
    """This is the mocked Response object returned by requests.get()"""
    def __init__(self, b_content, text_content, status_code):
        self.content = b_content
        self.text = text_content
        self.status_code = status_code


# endregion Mocks
