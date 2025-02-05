"""dotnet module commands"""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Commands(ValueDictsBase):
    """ Commands for the dotnet module."""

    # Add your dotnet commands dictionaries here
    _commands = {
        "dotnet_add_package": "dotnet add \"{project_path}\" package \"{package}\" --version {version} "
                              "--source {nuget_feed} --no-restore",
        "dotnet_add_reference": "dotnet add \"{project_path}\" reference \"{reference_path}\"",
        "dotnet_build":
            "dotnet build {force} {with_restore} --configuration={configuration} --framework={framework} "
            "--runtime={runtime} {debug} {output} {path}",
        "dotnet_ef_database_drop":
            "dotnet ef database drop --force --startup-project {path} {no_build} -- --environment {env}",
        "dotnet_ef_database_reset":
            "dotnet ef database update 0 --startup-project {path} {no_build} -- --environment {env}",
        "dotnet_ef_migrations_list":
            "dotnet ef migrations list --startup-project {path} --json {no_build} -- --environment {env}",
        "dotnet_ef_migrations_script":
            "dotnet ef migrations script {migration_from} --startup-project {path} --output {script_path} {no_build} "
            "{idempotent} -- --environment {env}",
        "dotnet_new": "dotnet new {template} {template_options} --name {name} --output {path} {no_restore}",
        "dotnet_new_framework": "dotnet new {template} {template_options} --name {name} --output \"{path}\" "
                                "--framework {framework} --no-restore",
        "dotnet_restore": "dotnet restore {force} {debug} {path}",
        "dotnet_sln_add": "dotnet sln \"{solution_path}\" add --solution-folder \"{solution_folder}\" "
                          "\"{project_path}\"",
    }
