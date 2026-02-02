"""Test configuration file for linux module.

Add here whatever you want to pass as a fixture in your core."""
import pytest


class PathsData:
    """Class used to create the PathsData fixture"""
    file_path = "path/to/file"


@pytest.fixture
def pathsdata():
    """ Sample paths configuration data for testing"""
    yield PathsData()
    # Below code is executed as a TearDown
    print("Teardown finished. ")