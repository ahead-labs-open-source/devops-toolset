"""dotnet module literals"""

from devops_toolset.core.app import App
from devops_toolset.core.ValueDictsBase import ValueDictsBase

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the dotnet module."""

    _titles = {
        "dotnet_ci_title_pipeline_kickoff": _(".NET CI pipeline kick off"),
    }
    _info = {
        "dotnet_build_before": "Launching dotnet build inside {path}. Please wait...",
        "dotnet_cli_log": ".NET CLI => {log}",
        "dotnet_cli_project_created": "Project '{name}.csproj' created.",
        "dotnet_cli_project_exists": "Solution '{name}.csproj' already exists. Skipping.",
        "dotnet_cli_project_package_added": "Project \"{project}\" added \"{package}\" as a dependency.",
        "dotnet_cli_project_package_exists": "Project package \"{package}\" exists for project \"{project}\" as a "
                                             "dependency. Skipping.",
        "dotnet_cli_project_reference_added": "Project \"{project}\" added \"{referenced}\" as a reference.",
        "dotnet_cli_project_reference_exists": "Project reference \"{referenced}\" exists for project \"{project}\"."
                                               "Skipping.",
        "dotnet_cli_solution_created": "Solution '{name}.sln' created.",
        "dotnet_cli_solution_exists": "Solution '{name}.sln' already exists. Skipping.",
        "dotnet_cli_solution_project_added": "Project '{project}.csproj' added to solution '{solution}.sln'.",
        "dotnet_cli_solution_project_not_added": "Project '{project}.csproj' already added to solution '{solution}.sln'"
                                                 ". Skipping.",
        "dotnet_cli_starting_layer": "Starting layer '{layer}'.",
        "dotnet_ef_database_drop": "Dropping the database...",
        "dotnet_ef_database_reset": "Reverting all migrations...",
        "dotnet_ef_first_migration_not_applied": "First migration not applied: {migration_name} ({migration_date})",
        "dotnet_ef_got_environments": "I got these environments: {environments}.",
        "dotnet_ef_migrations_info":
            "Number of migrations: {number}, applied migrations: {applied}, last applied migration: {name}",
        "dotnet_ef_migrations_list": "Listing migrations (will take a while)...",
        "dotnet_ef_migrations_list_output": "I got this output getting the migration's list:\n{output}",
        "dotnet_ef_migrations_script": "Generating SQL script (will take a while)...",
        "dotnet_ef_no_pending_migrations": "There are no pending migrations to be applied.",
        "dotnet_ef_script_being_generated": "SQL migration script being generated: {script_path}",
        "dotnet_ef_script_executing_command": "Executing command => {command}",
        "dotnet_ef_script_for_environment": "Generating SQL migration script for {environment} environment...",
        "dotnet_ef_utils_appsettings_dev_environment_skipped":
            "Skipped development environment as include_development is False",
        "dotnet_ef_utils_appsettings_files_matched": "I got these appsettings files matched: {files}",
        "dotnet_ef_utils_appsettings_environment_matched": "Environment {environment} matched on: {filename}",
        "dotnet_ef_utils_appsettings_no_environment_matched": "No environment matched on: {filename}",
        "dotnet_ef_utils_getting_appsettings_files": "Getting appsettings files from: {path}",
        "dotnet_restore_before": "Launching dotnet restore inside {path}. Please wait...",
        "dotnet_project_version": "The project version is {version}",
    }
    _errors = {
        "dotnet_restore_err": "Something went wrong while restoring {path}. Please check the logs and try again.",
        "dotnet_build_err": "Something went wrong while building {path}. Please check the logs and try again.",
    }
