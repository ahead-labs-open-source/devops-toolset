""" Unit tests for the dotnet/entity_framework.py module"""
import pytest

from devops_toolset.core import App
from devops_toolset.core import CommandsCore
from devops_toolset.core import LiteralsCore
from devops_toolset import Commands as DotnetCommands
from devops_toolset import Literals as DotnetLiterals
from devops_toolset import cli
from unittest import mock
from unittest.mock import patch, call

import json
import devops_toolset as sut
import devops_toolset as utils
import pathlib

app: App = App()
literals = LiteralsCore([DotnetLiterals])
commands = CommandsCore([DotnetCommands])

# region __get_first_migration_not_applied()


@patch("logging.info")
def test_get_first_migration_not_applied_returns_name_and_date_from_not_applied_migration_list(
        logging_info_mock, migrationsdata):
    """ Returns date and name for non applied migration """
    # Arrange
    migration_test_data = json.loads(migrationsdata.one_migration_and_applied)
    expected_name = "Second-V2"
    expected_date = "20220529212512"

    # Act
    migration_name, migration_date = sut.__get_first_migration_not_applied(migration_test_data)

    # Assert
    assert migration_name == expected_name and migration_date == expected_date


@patch("logging.info")
def test_get_first_migration_not_applied_returns_none_tuple_when_no_migrations_found(logging_info_mock):
    """ Returns None, None for missing migrations """
    # Arrange
    migration_test_data = json.loads("[]")

    # Act
    migration_name, migration_date = sut.__get_first_migration_not_applied(migration_test_data)

    # Assert
    assert migration_name is None and migration_date is None

# endregion __get_first_migration_not_applied()

# region __generate_sql_script()


@mock.patch.object(cli, "call_subprocess")
@patch("logging.info")
def test_generate_sql_script_calls_subprocess(log_info_mock, call_subprocess_mock):
    """ Calls subprocess once."""

    # Arrange
    startup_project_path: str = ""
    script_path: str = ""
    environment: str = ""

    # Act
    sut.__generate_sql_script(startup_project_path, script_path, environment)

    # Assert
    call_subprocess_mock.assert_called_once()


# endregion __generate_sql_script()

# region __get_migrations_list()


@mock.patch.object(cli, "call_subprocess_with_result")
@patch("logging.info")
def test_get_migrations_list_calls_subprocess(log_info_mock, call_subprocess_with_result_mock, migrationsdata):
    """ Calls subprocess once."""

    # Arrange
    startup_project_path: str = ""
    environment: str = ""
    call_subprocess_with_result_mock.return_value = migrationsdata.migrations_list_command_result

    # Act
    result = sut.__get_migrations_list(startup_project_path, environment)

    # Assert
    call_subprocess_with_result_mock.assert_called_once()
    assert type(result) is list


# endregion __get_migrations_list()

# region __parse_data_from_migrations_json_array()


@patch("logging.info")
def test_parse_data_from_migrations_json_array_given_migrations_list_returns_parsed_data(
        logging_info_mock, migrationsdata):
    """ Given migrations list, returns parsed data."""

    # Arrange
    migrations_list: list = json.loads(migrationsdata.one_migration_and_applied)

    # Act
    migrations, applied_migrations, last_migration_applied = \
        sut.__parse_data_from_migrations_json_array(migrations_list)

    # Assert
    assert migrations == 2
    assert applied_migrations == 1
    assert last_migration_applied == migrations_list[0]["id"]

# endregion __parse_data_from_migrations_json_array()

# region check_branch_suitableness_for_migrations()


@pytest.mark.parametrize("current_branch_simplified, suitable_branches_list, expected", [
    ("dev", ["dev", "main"], True), ("feature/unit-tests", ["dev", "main"], False)
])
def test_check_branch_suitableness_for_migrations_writes_environment_variable(
        current_branch_simplified, suitable_branches_list, expected):
    """Given a Git branch name, writes an environment variable with the boolean
    result."""

    # Arrange
    environment_variable_name = "MY_ENV_VAR"

    # Act
    result = sut.check_branch_suitableness_for_migrations(
        current_branch_simplified, suitable_branches_list, environment_variable_name)

    # Assert
    assert result is expected

# endregion check_branch_suitableness_for_migrations()

# region drop_database()


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("logging.info")
def test_drop_database_calls_subprocess(logging_info_mock, subprocess_mock):
    """ Calls subprocess for executing EF command. """

    # Arrange
    startup_project_path: str = "path/to/project"
    environment: str = "Staging"

    # Act
    sut.drop_database(startup_project_path, environment)

    # Assert
    subprocess_mock.assert_called()

# endregion drop_database()

# region generate_migration_sql_script()


@mock.patch.object(sut, "__get_migrations_list")
@mock.patch.object(sut, "__get_first_migration_not_applied")
@mock.patch.object(sut, "__generate_sql_script")
def test_generate_migration_sql_script_calls_generate_sql_script(
        generate_sql_script_mock, get_first_migration_not_applied_mock, get_migrations_list_mock, migrationsdata):
    """ Calls __generate_sql_script with required data"""

    # Arrange
    startup_project_path: str = ""
    environment: str = ""
    script_path: str = "#date#"
    migration_date: str = "20220529212512"
    migration_name: str = "Second-V2"
    no_build: bool = False
    get_migrations_list_mock.return_value = json.loads(migrationsdata.one_migration_and_applied)
    get_first_migration_not_applied_mock.return_value = migration_name, migration_date
    migrations, applied_migrations, last_migration_applied = \
        sut.__parse_data_from_migrations_json_array(json.loads(migrationsdata.one_migration_and_applied))
    idempotent: bool = True

    # Act
    sut.generate_migration_sql_script(startup_project_path, environment, script_path, idempotent=idempotent)

    # Assert
    generate_sql_script_mock.assert_called_once_with(startup_project_path,
                                                     script_path.replace("#date#", migration_date),
                                                     environment, last_migration_applied, no_build, idempotent)


# endregion generate_migration_sql_script()

# region generate_migration_sql_scripts_for_all_environments()

@patch("logging.info")
@mock.patch.object(sut, "generate_migration_sql_script")
@mock.patch.object(utils, "get_appsettings_environments")
def test_generate_migration_sql_scripts_for_all_environments_calls_generate_migration_sql_script(
        get_appsettings_environments_mock, generate_migration_sql_script_mock, logging_info_mock):
    """ Calls generate_migration_sql_script with required data """
    # Arrange
    environments = ["staging", "production"]
    get_appsettings_environments_mock.return_value = environments
    startup_project_path = ""
    scripts_base_path = "my_path/scripts"
    expected_script_path_0 = pathlib.Path.joinpath(
        pathlib.Path(scripts_base_path), f"database-migration-staging-from-#date#.sql")
    expected_script_path_1 = pathlib.Path.joinpath(
        pathlib.Path(scripts_base_path), f"database-migration-production-from-#date#.sql")
    no_build: bool = True
    idempotent: bool = True
    expected_calls = [
        call(startup_project_path, environments[0], str(expected_script_path_0), no_build, idempotent),
        call(startup_project_path, environments[1], str(expected_script_path_1), no_build, idempotent)
    ]

    # Act
    sut.generate_migration_sql_scripts_for_all_environments(
        startup_project_path, scripts_base_path, False, no_build, idempotent)

    # Assert
    generate_migration_sql_script_mock.assert_has_calls(expected_calls, any_order=True)


# endregion generate_migration_sql_scripts_for_all_environments()

# region reset_database()


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("logging.info")
def test_drop_database_calls_subprocess(logging_info_mock, subprocess_mock):
    """ Calls subprocess for executing EF command. """

    # Arrange
    startup_project_path: str = "path/to/project"
    environment: str = "Staging"

    # Act
    sut.reset_database(startup_project_path, environment)

    # Assert
    subprocess_mock.assert_called()

# endregion drop_database()
