"""Unit core for the rollback_database file"""

from unittest.mock import patch
import devops_toolset as sut


@patch("devops_toolset.project_types.wordpress.wp_cli.import_database")
@patch("devops_toolset.project_types.wordpress.wp_cli.reset_database")
def test_main(reset_database, import_database):
    """Given arguments, then calls all needed WP CLI commands."""

    # Arrange
    wordpress_path = ""
    database_dump_path = ""
    quiet = True

    # Act
    sut.main(wordpress_path, database_dump_path, quiet)

    # Assert
    reset_database.assert_called()
    import_database.assert_called()
