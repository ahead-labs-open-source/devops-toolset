""" Unit tests for the dotnet/cli.py module"""

import pytest

import devops_toolset as sut
from devops_toolset.core import CommandsCore
from devops_toolset.core import LiteralsCore
from devops_toolset import Commands as DotnetCommands
from devops_toolset import Literals as DotnetLiterals
from devops_toolset.core import App

app: App = App()
literals = LiteralsCore([DotnetLiterals])
commands = CommandsCore([DotnetCommands])


# region convert_debug_parameter()

@pytest.mark.parametrize("value,expected", [(False, ""), (True, "--verbosity=diagnostic")])
def test_convert_debug_parameter_returns_conversion_argument(value, expected):
    """ Given value argument, should test the two possibilities and return desired value """
    # Arrange
    # Act
    result = sut.convert_debug_parameter(value)
    # Assert
    assert result == expected

# endregion convert_debug_parameter()

# region convert_force_parameter()


@pytest.mark.parametrize("value,expected", [(False, ""), (True, "--force")])
def test_convert_force_parameter_returns_conversion_argument(value, expected):
    """ Given value argument, should test the two possibilities and return desired value """
    # Arrange
    # Act
    result = sut.convert_force_parameter(value)
    # Assert
    assert result == expected

# endregion convert_force_parameter()

# region convert_with_restore_parameter()


@pytest.mark.parametrize("value,expected", [(False, "--no-restore"), (True, "")])
def test_convert_with_restore_parameter_returns_conversion_argument(value, expected):
    """ Given value argument, should test the two possibilities and return desired value """
    # Arrange
    # Act
    result = sut.convert_with_restore_parameter(value)
    # Assert
    assert result == expected

# endregion convert_with_restore_parameter()

# region restore()

# endregion restore()

# region build()

# endregion build()
