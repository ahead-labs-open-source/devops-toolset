""" Unit tests for the project_types/azure/base.py module"""

from unittest.mock import patch


# region check_resource_group_exists()

@patch('devops_toolset.tools.cli.call_subprocess_with_result')
@patch('logging.info')
def test_check_resource_group_exists_when_resource_group_exists(mock_logging, mock_cli):
    """Tests if check_resource_group_exists returns True when the resource group exists."""
    # Arrange
    mock_cli.return_value = 'true\r\n'

    # Act
    result = base.check_resource_group_exists("existing-group")

    # Assert
    assert result is True


@patch('devops_toolset.tools.cli.call_subprocess_with_result')
@patch('logging.info')
def test_check_resource_group_exists_when_resource_group_does_not_exist(mock_logging, mock_cli):
    """Tests if check_resource_group_exists returns False when the resource group does not exist."""
    # Arrange
    mock_cli.return_value = 'false\r\n'

    # Act
    result = base.check_resource_group_exists("non-existing-group")

    # Assert
    assert result is False

# endregion

# region create_resource_group()

@patch('devops_toolset.project_types.azure.base.check_resource_group_exists')
@patch('devops_toolset.tools.cli.call_subprocess_with_result')
@patch('logging.info')
def test_create_resource_group_when_resource_group_does_not_exist(mock_logging, mock_cli, mock_check):
    """Tests if create_resource_group creates a resource group when it does not exist."""
    # Arrange
    mock_check.return_value = False
    mock_cli.return_value = 'Resource group created'

    # Act
    base.create_resource_group("new-group", "westeurope")

    # Assert
    mock_cli.assert_called_once()


@patch('devops_toolset.project_types.azure.base.check_resource_group_exists')
@patch('devops_toolset.tools.cli.call_subprocess_with_result')
@patch('logging.info')
def test_create_resource_group_when_resource_group_exists(mock_logging, mock_cli, mock_check):
    """Tests if create_resource_group does not create a resource group when it already exists."""
    # Arrange
    mock_check.return_value = True

    # Act
    base.create_resource_group("existing-group", "westeurope")

    # Assert
    mock_cli.assert_not_called()

# endregion

# region for delete_resource_group()


from unittest.mock import patch
from devops_toolset import base

# region delete_resource_group tests


@patch('devops_toolset.project_types.azure.base.check_resource_group_exists')
@patch('devops_toolset.tools.cli.call_subprocess_with_result')
@patch('logging.info')
def test_delete_resource_group_when_resource_group_exists(mock_logging, mock_cli, mock_check):
    """Tests if delete_resource_group deletes a resource group when it exists."""
    # Arrange
    mock_check.return_value = True
    mock_cli.return_value = None

    # Act
    base.delete_resource_group("existing-group")

    # Assert
    mock_cli.assert_called_once()
    mock_logging.assert_called_with(base.literals.get("azure_cli_resource_group_deleted").format(name="existing-group"))


@patch('devops_toolset.project_types.azure.base.check_resource_group_exists')
@patch('devops_toolset.tools.cli.call_subprocess_with_result')
@patch('logging.info')
def test_delete_resource_group_when_resource_group_does_not_exist(mock_logging, mock_cli, mock_check):
    """Tests if delete_resource_group does not delete a resource group when it does not exist."""
    # Arrange
    mock_check.return_value = False

    # Act
    base.delete_resource_group("non-existing-group")

    # Assert
    mock_cli.assert_not_called()


@patch('devops_toolset.project_types.azure.base.check_resource_group_exists')
@patch('devops_toolset.tools.cli.call_subprocess_with_result')
@patch('logging.info')
@patch('logging.error')
def test_delete_resource_group_when_deletion_fails(mock_logging_error, mock_logging_info, mock_cli, mock_check):
    """Tests if delete_resource_group handles failure when deleting a resource group."""
    # Arrange
    mock_check.return_value = True
    mock_cli.return_value = 'Error: Failed to delete resource group'

    # Act
    base.delete_resource_group("existing-group")

    # Assert
    mock_cli.assert_called_once()
    mock_logging_error.assert_called()

# endregion

# endregion
