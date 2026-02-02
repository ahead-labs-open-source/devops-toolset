"""Test configuration file for sonarx module.

Add here whatever you want to pass as a fixture in your texts."""

import pytest
import json


class SonarxData(object):
    """Class used to create the sonarxdata fixture"""
    sonar_url = "https://sonarcloud.io"
    sonar_project_key = "devops-toolset"
    sonar_project_key_ok = "devops-toolset-ok"
    sonar_project_key_error = "devops-toolset-error"
    sonar_organization = "ahead-labs"
    properties_file_name = "sonar-project.properties"
    properties_file_path = f"/pathto/{properties_file_name}"
    properties_file_data = \
        f"sonar.host.url={sonar_url}\nsonar.projectKey={sonar_project_key}\nsonar.organization={sonar_organization}"
    token = "0123456789abcdef0123456789abcdef01234567"
    branch_feature = "/feature/branch"
    quality_gate_json_ok = "{\"projectStatus\":{\"status\":\"OK\"}}"
    quality_gate_json_error = "{\"projectStatus\":{\"status\":\"ERROR\",\"ignoredConditions\":false," \
                              "\"conditions\":[{\"status\":\"ERROR\",\"metricKey\":\"new_coverage\"," \
                              "\"comparator\":\"LT\",\"periodIndex\":1,\"errorThreshold\":\"85\"," \
                              "\"actualValue\":\"82.50562381034781\"},{\"status\":\"OK\"," \
                              "\"metricKey\":\"new_sqale_debt_ratio\",\"comparator\":\"GT\"," \
                              "\"periodIndex\":1,\"errorThreshold\":\"5\",\"actualValue\":\"0.65\"}]}}"


@pytest.fixture
def sonarxdata():
    """Sample sonarx data for testing sonarx related functionality"""
    return SonarxData()


# Mocks


def mocked_requests_get(url: str, *args, **kwargs):
    """Mock to replace requests.get()"""

    # Default values
    status_code = 200

    # Determine if passes quality gate
    if url.find(SonarxData.sonar_project_key_ok) != -1:
        json_data = SonarxData.quality_gate_json_ok
    else:
        json_data = SonarxData.quality_gate_json_error

    # Return instance
    return MockResponse(json_data, status_code)


class MockResponse(object):
    """This is the mocked Response object returned by requests.get()"""
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        """When they call <mock>.json() this will be returned"""
        return json.loads(self.json_data)

    def status(self):
        """When they call <mock>.status() this will be returned"""
        return self.status_code
