"""Test configuration file for Angular package.

This code is executed once per unit test session.
Add here whatever you want to pass as a fixture in your core.

    ie: (see FileNames example)
        - Add a class that contains what you want to pass as a fixture in your core.
        - Create a fixture with that same lowered name that returns an instance to that class."""


import pytest


class AngularData(object):
    """Class used to create the angulardata fixture"""

    packagejson_content = "{\"name\":\"my-project\",\"version\":\"1.2.3-rc.4\"}"


@pytest.fixture
def angulardata():
    """Sample data for testing Angular related functionality"""
    return AngularData()
