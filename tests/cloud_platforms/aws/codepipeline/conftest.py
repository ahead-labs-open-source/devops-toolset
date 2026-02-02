"""Test configuration file for aws module.

Add here whatever you want to pass as a fixture in your core."""

import pytest


class PlatformData(object):
    """Class used to create the platformdata fixture"""
    environment_variables_dict = {"env_var_1": "value1", "env_var_2": "value2"}
    environment_variables_dict1 = {"env_var_1": "value1"}


@pytest.fixture
def platformdata():
    """Sample data for testing"""
    return PlatformData()
