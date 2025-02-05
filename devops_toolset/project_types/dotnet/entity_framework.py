"""Microsoft Entity Framework utilities"""

from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.dotnet.Literals import Literals as DotnetLiterals
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.project_types.dotnet.commands import Commands as DotnetCommands

import devops_toolset.project_types.dotnet.utils as utils
import devops_toolset.tools.cli as cli
import json
import logging
import pathlib
import re

app: App = App()
platform_specific = app.load_platform_specific("environment")
literals = LiteralsCore([DotnetLiterals])
commands = CommandsCore([DotnetCommands])


def __generate_sql_script(startup_project_path: str, script_path: str, environment: str, migration_from: str = "0",
                          no_build: bool = False, idempotent: bool = True) -> str:
    """ Generates a SQL script to apply ad hoc migrations to DBMS and returns its path

    Args:
        startup_project_path: Path to the startup project.
        script_path: Path where the script will be generated at.
        environment: Name for the environment to generate the script for.
        migration_from: ID / name of the last migration applied, defaults to 0.
        no_build: Skips build if True.
        idempotent: If True it creates an idempotent script.
    """

    logging.info(literals.get("dotnet_ef_migrations_script"))

    cli.call_subprocess(commands.get("dotnet_ef_migrations_script").format(
        migration_from=migration_from,
        path=startup_project_path,
        script_path=script_path,
        no_build="--no-build" if no_build else "",
        idempotent="--idempotent" if idempotent else "",
        env=environment
    ))

    return script_path


def __get_first_migration_not_applied(migrations_list: list) -> ([str, None], [str, None]):
    """ Returns the first migration in the list that has not been applied.

    Args:
        migrations_list: List of migrations

    Returns:
        Tuple with migration name and migration date (migration format) or None
        and None if no migration is found.
    """
    regex_pattern = r"^(\d+)_[\w-]+$"

    for migration in migrations_list:
        if migration["applied"] is False:
            match = re.search(regex_pattern, migration["id"])
            logging.info(literals.get("dotnet_ef_first_migration_not_applied").format(
                migration_name=migration["name"],
                migration_date=match.groups()[0]
            ))
            return migration["name"], match.groups()[0]

    logging.info(literals.get("dotnet_ef_no_pending_migrations"))
    return None, None


def __get_migrations_list(startup_project_path: str, environment: str, no_build: bool = False) -> list:
    """ Gets a list of the migrations applied for a specific environment

    Args:
        startup_project_path: Path to the startup project
        environment: Name for the environment to get the migrations for
        no_build: Skips build if True

    Returns:
        Migrations JSON array
    """

    logging.info(literals.get("dotnet_ef_migrations_list"))

    ef_command: str = commands.get("dotnet_ef_migrations_list").format(
        path=startup_project_path,
        no_build="--no-build" if no_build else "",
        env=environment
    )
    logging.info(literals.get("dotnet_ef_script_executing_command").format(command=ef_command))

    result: str = cli.call_subprocess_with_result(ef_command)
    logging.info(literals.get("dotnet_ef_migrations_list_output").format(output=result))

    migrations: str = ""
    json_lure: bool = False
    for line in result.splitlines():
        if line.startswith("[") and not json_lure:
            json_lure = True
        if json_lure:
            migrations += line

    return json.loads(migrations)


def __parse_data_from_migrations_json_array(migrations_json_array: list) -> (int, int, str):
    """ Parses data from the migrations JSON array

    Arguments:
        migrations_json_array: Migrations JSON array

    Returns:
        Number of migrations, number of applied migrations, last applied
        migration name
    """

    last_applied_migration: str = "0"
    applied_migrations: int = 0
    for migration in migrations_json_array:
        if migration["applied"]:
            last_applied_migration = migration["id"]
            applied_migrations += 1

    logging.info(literals.get("dotnet_ef_migrations_info").format(
        number=len(migrations_json_array),
        applied=applied_migrations,
        name=last_applied_migration
    ))
    return len(migrations_json_array), applied_migrations, last_applied_migration


def check_branch_suitableness_for_migrations(
        current_simplified_branch: str, suitable_branches: list,
        environment_variable_name: str = "DT_SUITABLE_BRANCH_FOR_MIGRATIONS") -> bool:
    """Checks if the current Git branch is suitable for generating and applying
    SQL migration scripts.

    Args:
        current_simplified_branch: Current simplified Git branch.
        suitable_branches: List of branches that are suitable for migrations.
        environment_variable_name: Name of the environment variable to be
            created. Defaults to "DT_SUITABLE_BRANCH_FOR_MIGRATIONS".

    Returns:
        True if branch is suitable, False otherwise.
    """

    is_suitable = True if current_simplified_branch in suitable_branches else False
    platform_specific.create_environment_variables({environment_variable_name: is_suitable})
    return is_suitable


def drop_database(startup_project_path: str, environment: str, no_build: bool = False):
    """ Drops the database

    Args:
        startup_project_path: Path to the startup project
        environment: Name for the environment to get the migrations for
        no_build: Skips build if True
    """
    logging.info(literals.get("dotnet_ef_database_drop"))

    result: str = cli.call_subprocess_with_result(commands.get("dotnet_ef_database_drop").format(
        path=startup_project_path,
        no_build="--no-build" if no_build else "",
        env=environment
    ))
    logging.info(result)


def generate_migration_sql_script(startup_project_path: str, environment: str, script_path: str,
                                  no_build: bool = False, idempotent: bool = True) -> str:
    """ Generates SQL migration script for a specific environment and returns its path

    Args:
        startup_project_path: Path to the startup project.
        environment: Name for the environment to get the migrations for.
        script_path: Path to the SQL script to be generated.
        no_build: Skips build if True.
        idempotent: If True it creates an idempotent script.
    """

    migrations_list: list = __get_migrations_list(startup_project_path, environment)
    migration_name, migration_date = __get_first_migration_not_applied(migrations_list)
    migrations, applied_migrations, last_migration_applied = __parse_data_from_migrations_json_array(migrations_list)

    if migration_name is not None and migrations != applied_migrations:
        return __generate_sql_script(startup_project_path, script_path.replace("#date#", migration_date), environment,
                                     last_migration_applied, no_build, idempotent)


def generate_migration_sql_scripts_for_all_environments(startup_project_path: str, scripts_base_path: str,
                                                        include_development: bool = False, no_build: bool = False,
                                                        idempotent: bool = True) -> list[str]:
    """ Generates a SQL migration script for every environment configured in
    the appsettings.*.json files and returns a list with the script paths generated

    Args:
        startup_project_path: Path to the startup project.
        scripts_base_path: Path to the directory where all scripts will be
            created at.
        include_development: If True, Development/Dev is included in the list.
        no_build: Skips build if True.
        idempotent: If True it creates an idempotent script.
    """
    script_paths = []
    environments = utils.get_appsettings_environments(startup_project_path, include_development)
    logging.info(literals.get("dotnet_ef_got_environments").format(environments=environments))

    base_path_obj = pathlib.Path(scripts_base_path)

    for environment in environments:
        logging.info(literals.get("dotnet_ef_script_for_environment").format(environment=environment))

        script_path = pathlib.Path.joinpath(base_path_obj, f"database-migration-{environment.lower()}-from-#date#.sql")
        logging.info(literals.get("dotnet_ef_script_being_generated").format(script_path=script_path))

        generated_script_path: str = \
            generate_migration_sql_script(startup_project_path, environment, str(script_path), no_build, idempotent)

        if generated_script_path is not None:
            script_paths.append(generated_script_path)

    return script_paths


def reset_database(startup_project_path: str, environment: str, no_build: bool = False):
    """ Reverts all migrations applied, dropping all tables and truncating
    __efmigrationshistory database

    Args:
        startup_project_path: Path to the startup project.
        environment: Name for the environment to get the migrations for.
        no_build: Skips build if True.
    """
    logging.info(literals.get("dotnet_ef_database_reset"))

    result: str = cli.call_subprocess_with_result(commands.get("dotnet_ef_database_reset").format(
        path=startup_project_path,
        no_build="--no-build" if no_build else "",
        env=environment
    ))
    logging.info(result)


if __name__ == "__main__":
    help(__name__)
