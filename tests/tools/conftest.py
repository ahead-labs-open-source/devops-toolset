"""Test configuration file for filesystem module.

Add here whatever you want to pass as a fixture in your texts."""


import pytest
from devops_toolset.core import App
import pathlib

app: App = App()

class GitignoreData(object):
    """Class used to create the gitignoredata fixture"""
    file_contents = "wordpress/wp-content/themes/oldtheme/"
    regex = r"wordpress/wp-content/themes/([\w\-]+)/"
    replace_value = "mytheme"


@pytest.fixture
def gitignoredata():
    """Sample file names for testing file system related functionality"""
    return GitignoreData()


class BranchesData(object):
    """Class used to create the branchesdata fixture"""
    long_master_branch = "refs/heads/master"
    simple_master_branch = "master"
    long_feature_branch = "refs/heads/feature/name"
    simple_feature_branch = "feature/name"
    long_pr_branch = "refs/pull/1/merge"
    simple_pr_branch = "pull/1"
    other_branch = "dev"
    environment_variable_name = "env_variable"


@pytest.fixture
def branchesdata():
    """Sample branch names for testing"""
    return BranchesData()


class CliData(object):
    """ Class used to create CliData fixture containing test data"""
    sample_command = "sample command"
    sample_log_message_info = b"Operation completed successfully."
    sample_log_message_error = b"Something went wrong."
    auth_header = "bearer 1234"


@pytest.fixture()
def clidata():
    """ Sample command line interface data """
    return CliData()


class GitData(object):
    """ Class used to create the gitdata fixture """

    branch = "heads/refs/dev"
    tag = "v1.0.0"
    commit = "fdr564"
    auth_header = "bearer 1234"


@pytest.fixture
def gitdata():
    """Sample data for testing Git functionality"""
    return GitData()


class Paths(object):
    """Class used to create paths fixture"""
    invalid_path = "/invalid/path"
    xml_path = pathlib.Path(app.settings.project_xml_path, "project.xml")
    devops_toolset_path_file = "/devops_toolset/path/file"
    devops_destination_path = "/devops_toolset/destination/path"
    devops_old_destination_path = "/devops_toolset/destination/old"
    devops_final_destination_path = "/devops_toolset/destination/final"
    toolset_path = "/toolset/path"
    builtins_open = 'builtins.open'


@pytest.fixture()
def paths():
    """Sample paths for testing"""
    yield Paths()
    # Below code is executed as a TearDown
    print("Teardown finished.")


def mocked_requests_get(url: str, *args, **kwargs):
    """Mock to replace requests.get()"""

    # Default values
    bytes_content = b"sample response in bytes"
    text_content = "sample text response"

    # Return instance
    return MockResponse(bytes_content, text_content)


def mocked_requests_get_ip(*args, **kwargs):
    """Mock to replace requests.get() returning HTML with an IP address."""

    # Default values
    bytes_content = b"<p>Your IP address is 1.1.1.1</p>"
    text_content = "sample text response"

    # Return instance
    return MockResponse(bytes_content, text_content)


class MockResponse(object):
    """This is the mocked Response object returned by requests.get()"""
    def __init__(self, b_content, text_content):
        self.content = b_content
        self.text = text_content


class SvnData(object):
    """ Class used to create the gitdata fixture """
    glob = "trunk/*"
    comment = "This is a test comment for the check in"
    username = "TestUsername"
    password = "TestPassword"
    repo_url = "https://plugins.svn.wordpress.org/your-plugin-name"
    path = "/test/path"

@pytest.fixture
def svndata():
    """Sample data for testing Git functionality"""
    return SvnData()
