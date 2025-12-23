""" This script will scaffold a DDDD WebAPI solution in .NET """

import argparse
import devops_toolset.core.log_setup
import devops_toolset.tools.argument_validators
import devops_toolset.tools.cli
import devops_toolset.tools.git
import json
import logging
import os
import pathlib
from devops_toolset.core.app import App
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.dotnet.commands import Commands as DotnetCommands
from devops_toolset.project_types.dotnet.Literals import Literals as DotnetLiterals

app: App = App()
literals = LiteralsCore([DotnetLiterals])
commands = CommandsCore([DotnetCommands])
template_config: dict = {}


def main(root_path: str, solution_name: str, template_name: str, relational_db_engine: str):
    """ Scaffolds a .NET WebAPI solution based on DDDD

    Args:
        root_path: Path to the solution root.
        solution_name: Name of the solution to scaffold.
        template_name: Name of the scaffolding template.
        relational_db_engine: Relational database engine.
    """

    root_path_obj = pathlib.Path(root_path)

    # Create solution
    create_solution(solution_name, root_path)

    # Read configuration template (global converts template_config into a global variable)
    with open(get_configuration(template_name), "r") as config_file:
        global template_config
        template_config = json.load(config_file)

    # Init Git repository
    create_git_repository(root_path_obj)

    # Get a list of projects-layers key-value pairs
    project_layers: dict = get_project_layers(template_config, solution_name)

    # Create projects
    for layer in template_config["layers"]:
        logging.info(literals.get('dotnet_cli_starting_layer').format(layer=layer["name"]))
        layer_path = pathlib.Path.joinpath(root_path_obj, layer["name"])
        os.makedirs(layer_path)

        for project in layer["projects"]:
            project["solution_path"] = root_path
            project["solution_name"] = solution_name
            project["solution_folder"] = layer["name"]
            project["project_path"] = layer_path
            project["project_name"] = f"{project['solution_name']}{project['name']}"
            if "framework" not in project:
                project["framework"] = template_config["settings"]["default_frameworks"][project["template"]]
            create_project(project, str(layer_path), project_layers)


def add_nuget_package(project_path: str, package_name: str, source: str = "https://api.nuget.org/v3/index.json"):
    """Adds a package to a project.

    Args:
        project_path: Path to the project that adds the reference.
        package_name: NuGet package name.
        source: Source feed to get the package from.
    """

    package_info: list[str] = package_name.split("|")

    command: str = commands.get("dotnet_add_package").format(
        project_path=project_path,
        package=package_info[0],
        version=package_info[1],
        nuget_feed=source
    )
    result: str = devops_toolset.tools.cli.call_subprocess_with_result(command)

    log(command, result,
        literals.get('dotnet_cli_project_package_added').format(project=project_path, package=package_name),
        literals.get('dotnet_cli_project_package_exists').format(project=project_path, package=package_name))


def add_project_to_solution(solution_path: str, solution_name: str, project_path: str, project_name: str,
                            solution_folder: str = None):
    """Adds a project to the solution

    Args:
        solution_path: Path to the solution file
        solution_name: Name of the solution without extension
        project_path: Path to the project file
        project_name: Name of the project file without extension
        solution_folder: Solution folder (virtual) name
    """

    command: str = commands.get('dotnet_sln_add').format(
        solution_path=solution_path,
        solution_folder=solution_folder,
        project_path=pathlib.Path.joinpath(pathlib.Path(project_path), project_name)
    )

    result: str = devops_toolset.tools.cli.call_subprocess_with_result(command)

    log(command, result,
        literals.get('dotnet_cli_solution_project_added').format(project=project_name, solution=solution_name),
        literals.get('dotnet_cli_solution_project_not_added').format(project=project_name, solution=solution_name))


def add_project_reference(project_path: str, reference_path: str):
    """Adds a reference to a project.

    Args:
        project_path: Path to the project that adds the reference.
        reference_path: Path to the project to be added as a reference.
    """

    command: str = commands.get("dotnet_add_reference").format(
        project_path=project_path,
        reference_path=reference_path
    )
    result: str = devops_toolset.tools.cli.call_subprocess_with_result(command)

    log(command, result,
        literals.get('dotnet_cli_project_reference_added').format(project=project_path, referenced=reference_path),
        literals.get('dotnet_cli_project_reference_exists').format(project=project_path, referenced=reference_path))


def add_unit_tests(project_config: dict, path: str, project_layers: dict):
    """Adds unit tests to a project

    Args:
        project_config: Project data configuration
        path: Path where to create the project
        project_layers: List of projects-layers key-value pairs"""

    if project_config["unit-test-eligible"] and not template_config["settings"]["skip_unit_tests"]:
        path_obj = pathlib.Path(path)
        project_name = f'{project_config["project_name"]}.Tests'
        framework = template_config["settings"]["default_frameworks"]["xunit"]
        dotnet_new('xunit', project_name, str(pathlib.Path.joinpath(path_obj, project_name)), framework)
        add_project_to_solution(project_config["solution_path"], project_config["solution_name"],
                                project_config["project_path"], project_name, project_config["solution_folder"])


def create_git_repository(path: pathlib.Path):
    """Creates a Git repository and adds a .gitignore file.

    Args:
        path: Path to create the repository and .gitignore file at.
    """

    # Initialize Git repository
    devops_toolset.tools.git.git_init(str(path), False)

    # Create .gitignore file
    gitignore_path: pathlib.Path = pathlib.Path.joinpath(path, ".gitignore")
    pathlib.Path.touch(gitignore_path)

    # Add exclusions to .gitignore file
    exclusions: list = template_config["settings"]["git_exclusions"]
    for exclusion in exclusions:
        devops_toolset.tools.git.add_gitignore_exclusion(str(gitignore_path), exclusion)


def create_project(project_config: dict, path: str, project_layers: dict):
    """Creates a project for a specific template

    Args:
        project_config: Project data configuration
        path: Path where to create the project
        project_layers: List of projects-layers key-value pairs
    """

    path_obj = pathlib.Path(path)

    # Create project
    template_options: str = project_config["template_options"] if "template_options" in project_config else ""
    dotnet_new(project_config["template"], project_config["project_name"],
               str(pathlib.Path.joinpath(path_obj, project_config["project_name"])),
               project_config["framework"], template_options=template_options)

    # Add project to solution
    add_project_to_solution(project_config["solution_path"], project_config["solution_name"],
                            project_config["project_path"], project_config["project_name"],
                            project_config["solution_folder"])

    project_path_obj: pathlib.Path = pathlib.Path(project_config['project_path'])
    full_project_path: str = pathlib.Path.joinpath(project_path_obj, project_config['project_name'])

    # Add references to other projects
    for reference in project_config["references"]:
        reference_project_path = str(pathlib.Path.joinpath(
            pathlib.Path(project_config["solution_path"]),
            project_layers[f"{project_config['solution_name']}{reference}"],
            f"{project_config['solution_name']}{reference}"
        ))
        add_project_reference(full_project_path, reference_project_path)

    # Add NuGet packages
    for package in project_config["packages"]:
        add_nuget_package(full_project_path, package)

    # Add unit tests
    add_unit_tests(project_config, path, project_layers)


def create_solution(name: str, path: str):
    """Creates a solution in the specified path

    Args:
          name: Name of the solution to be created
          path: Path where to create the solution
    """

    dotnet_new("sln", name, path, None, True)


def dotnet_new(template: str, name: str, path: str, framework: [str, None],
               restore: bool = False, template_options: str = ""):
    """Creates a new .NET project using .NET CLI.

    Args:
        template: Project template name.
        name: Project name.
        path: Path to the project to be created.
        framework: Framework.
        restore: If True it restores all packages.
        template_options: Options for template, usually none.
    """

    if framework is not None:
        command = commands.get("dotnet_new_framework").format(
            template=template,
            template_options=template_options,
            name=name,
            path=path,
            framework=framework
        )
    else:
        command = commands.get("dotnet_new").format(
            template=template,
            template_options=template_options,
            name=name,
            path=path,
            no_restore="--no-restore" if not restore else ""
        )

    result: str = devops_toolset.tools.cli.call_subprocess_with_result(command)

    if template == "classlib" or template.startswith("webapi"):
        ok_message = literals.get('dotnet_cli_project_created').format(name=name)
        ko_message = literals.get('dotnet_cli_project_exists').format(name=name)
    elif template == "sln":
        ok_message = literals.get('dotnet_cli_solution_created').format(name=name)
        ko_message = literals.get('dotnet_cli_solution_exists').format(name=name)
    else:
        ok_message = ""
        ko_message = ""

    log(command, result, ok_message, ko_message)


def get_configuration(template_name: str):
    """Gets the configuration file based on the template name.

    Args:
        template_name: Configuration template name.
    """
    return f"./scaffolding_templates/{template_name}-template.json"


def get_project_layers(template_configuration: dict, solution_name: str) -> dict:
    """Returns a dict with all project folders.

    Args:
        template_configuration: Template configuration.
        solution_name: Name of the solution.
    """

    project_layers: dict = {}
    for layer in template_configuration["layers"]:
        for project in layer["projects"]:
            project_layers[f"{solution_name}{project['name']}"] = layer["name"]

    return project_layers


def log(command: str, result: [str, None], ok_message: str, ko_message: str):
    """ Logs command and results.

    Args:
        command: Command executed.
        result: Result of the command executed.
        ok_message: Message if everything went OK.
        ko_message: Message if things failed.
    """

    if result is not None:
        logging.debug(command)
        logging.info(literals.get('dotnet_cli_log').format(log=result))
        logging.info(ok_message)
    else:
        logging.error(ko_message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project-path", action=devops_toolset.tools.argument_validators.PathValidator)
    parser.add_argument("name")
    parser.add_argument("template_name")
    parser.add_argument("--relational-db-engine", default="mysql")
    args, args_unknown = parser.parse_known_args()
    main(args.project_path, args.name, args.template_name, args.relational_db_engine)

# TODO(team) Move functions related to .NET CLI to cli.py
