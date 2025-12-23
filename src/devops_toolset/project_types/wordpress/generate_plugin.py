""" This script will generate and configure a Wordpress site based on the
required configuration files"""

import argparse
import json
import logging
import os
import pathlib

import requests
from clint.textui import prompt

import devops_toolset.core.log_tools
import devops_toolset.tools.git as git_tools
import devops_toolset.filesystem.paths as paths
import devops_toolset.project_types.wordpress.wptools
import devops_toolset.tools.argument_validators
import devops_toolset.tools.cli as cli
import devops_toolset.tools.devops_toolset_utils
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.core.app import App
from devops_toolset.devops_platforms.constants import Urls
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals
from devops_toolset.project_types.wordpress.wp_plugin_tools import create_plugin

app: App = App()
literals = LiteralsCore([WordpressLiterals])


def main(root_path: str):
    """Generates a new WordPress plugin based on the plugin configuration file

    Args:
        root_path: Path to the root location of the plugin.
    """
    # Check parameters
    if not os.path.exists(root_path):
        raise NotADirectoryError(literals.get("wp_non_valid_dir_path"))

    # Check necessary files using required files engine
    required_files_pattern_suffixes: list = ["*plugin-config.json", "*plugin-structure.json"]
    required_files_not_present: list[str] = paths.files_exist_filtered(
        root_path, False, required_files_pattern_suffixes)

    if len(required_files_not_present) > 0:
        devops_toolset.core.log_tools.log_indented_list(literals.get("wp_required_files_not_found_detail")
                                                        .format(path=root_path),
                                                        required_files_not_present,
                                                        devops_toolset.core.log_tools.LogLevel.warning)

        # Ask to use defaults
        use_defaults: bool = prompt.yn(literals.get("wp_use_default_files"))

        # If not using defaults, exit
        if not use_defaults:
            logging.critical(literals.get("wp_required_files_mandatory"))
            raise ValueError(literals.get("wp_required_files_not_found").format(path=root_path))

        # Download defaults from GitHub
        for file in required_files_not_present:
            url = Urls.plugin_bootstrap_required_files[file]
            file_name = paths.get_file_name_from_url(url)
            file_path = pathlib.Path.joinpath(pathlib.Path(root_path), file_name)

            logging.info(literals.get("wp_downloading_default_file").format(file=file, url=url))
            response: requests.Response = requests.get(url)
            with open(file_path, "wb") as fw:
                fw.write(response.content)

    # Get plugin configuration file and parse it
    plugin_config: dict = get_and_parse_required_plugin_file(root_path, required_files_pattern_suffixes[0])

    # Get structure file and parse it
    plugin_structure: dict = get_and_parse_required_plugin_file(root_path, required_files_pattern_suffixes[1])

    # Call create plugin
    logging.info(literals.get("wp_creating_project_structure"))
    create_plugin(plugin_config, plugin_structure, root_path)
    logging.info(literals.get("wp_created_project_structure"))

    # Move original files to devops directory
    teardown(root_path)


def get_and_parse_required_plugin_file(root_path: str, file_pattern: str) -> dict:
    """ Get and parses a required file from a pattern, and returns its content as a dict
        Args:
            root_path: Path to the root location of the plugin.
            file_pattern: Pattern of the file to search for.
    """

    plugin_file_path: str = paths.get_file_path_from_pattern(root_path, file_pattern, True)

    if not os.path.exists(plugin_file_path):
        raise FileNotFoundError(literals.get("wp_file_not_found").format(file=plugin_file_path))

    with open(plugin_file_path, 'r') as plugin_file:
        logging.info(literals.get("wp_parsing_plugin_config_file").format(file=plugin_file_path))
        plugin_file_data: dict = json.load(plugin_file)
        return plugin_file_data


def teardown(root_path: str):
    """ Executes some tasks before finishing the plugin creation. These are:
        - Moving original required files to .devops folder
        - Purging .gitkeep of .devops folder

    Args:
        root_path: Path to the root location of the plugin.

    """
    devops_path = pathlib.Path.joinpath(pathlib.Path(root_path), '.devops').as_posix()
    paths.move_files(
        root_path,
        devops_path,
        "*.json",
        False
    )
    git_tools.purge_gitkeep(devops_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("plugin-path", action=devops_toolset.tools.argument_validators.PathValidator)
    args, args_unknown = parser.parse_known_args()
    kwargs = {}
    for kwarg in args_unknown:
        splitted = str(kwarg).split("=")
        kwargs[splitted[0]] = splitted[1]

    cli.print_title(literals.get("wp_title_generate_plugin"))
    main(args.plugin_path)
