"""Contains several tools and utils for WordPress Plugins"""
import logging
import os.path
import pathlib
import shutil

import devops_toolset.filesystem.paths as paths
import devops_toolset.tools.git as git_tools
import devops_toolset.tools.svn as svn
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.core.app import App
from devops_toolset.devops_platforms.azuredevops.Literals import Literals as PlatformLiterals
from devops_toolset.project_types.wordpress.Literals import Literals as WordpressLiterals
from devops_toolset.project_types.wordpress.basic_structure_starter import BasicStructureStarter
from devops_toolset.project_types.wordpress.commands import Commands as WordpressCommands
from devops_toolset.tools.dicts import replace_string_in_dict

app: App = App()
platform_specific_restapi = app.load_platform_specific("restapi")
literals = LiteralsCore([WordpressLiterals])
platform_literals = LiteralsCore([PlatformLiterals])
commands = CommandsCore([WordpressCommands])


def create_plugin(plugin_config: dict, plugin_structure: dict, plugin_destination_path: str):
    """ Creates a new WordPress plugin based on a configuration json file and a structure file

            Args:
                :param plugin_config: Path which contains.
                :param plugin_structure: Structure for the plugin
                :param plugin_destination_path: Destination path for the plugin being created
    """
    # Check destination path exists before creating structure
    if not os.path.exists(plugin_destination_path):
        logging.error(literals.get("wp_non_valid_dir_path"))
        return

    # Get plugin slug
    plugin_slug = plugin_config["slug"]
    plugin_slug_token = '[plugin-name]'

    # Purge .gitkeep
    git_tools.purge_gitkeep(pathlib.Path(plugin_destination_path).as_posix())

    # Use structure starter to create it based to the plugin structure
    project_starter = BasicStructureStarter({})

    # Iterate through every item recursively
    for item in plugin_structure["items"]:
        # Replace [plugin_name] token inside file structure dict
        item = replace_string_in_dict(item, plugin_slug_token, plugin_slug)
        # Process structure item
        project_starter.add_item(item, plugin_destination_path)

    # Parse plugin data into readme.txt
    parse_plugin_config_in_plugin_file(plugin_config, plugin_destination_path, 'readme.txt')
    # Parse plugin data into README.MD
    parse_plugin_config_in_plugin_file(plugin_config, plugin_destination_path, 'README.md')
    # Parse plugin data into plugin's php code metadata
    parse_plugin_config_in_plugin_file(plugin_config, plugin_destination_path, f'{plugin_slug}.php')


def create_release_tag(plugin_root_path: str, tag_name: str, copy_trunk: bool = True):
    """ Creates the structure for a new tag in a plugin structure

        Args:
            :param plugin_root_path: Source path which contains the plugin code.
            :param tag_name: Tag name to be created. Must not exist
            :param copy_trunk: If True, then the current content on /trunk will be copied
    """

    try:
        # Check plugin root exist
        __check_plugin_path_exists(plugin_root_path)

        # Check tag structure does not exist yet
        plugin_tag_path = pathlib.Path(plugin_root_path).joinpath('tags', tag_name)
        if pathlib.Path.exists(plugin_tag_path):
            logging.warning(literals.get("wp_plugin_tag_already_exists").format(tag_name=tag_name))
            return

        # Create the structure under the plugin root path
        pathlib.Path.mkdir(plugin_tag_path)

        logging.info(literals.get("wp_plugin_tag_path_created").format(plugin_tag_path=plugin_tag_path))

        # If copy_trunk, then copy the content on tag folder
        if copy_trunk:
            plugin_trunk_path: str = str(pathlib.Path(plugin_root_path).joinpath('trunk'))
            __check_plugin_path_exists(plugin_trunk_path)
            shutil.copytree(plugin_trunk_path, str(plugin_tag_path), dirs_exist_ok=True)
            logging.info(literals.get("wp_plugin_trunk_copied").format(plugin_trunk_path=plugin_tag_path))

        return

    except FileNotFoundError as exception:
        logging.exception(exception)
        return


def deploy_current_trunk(plugin_root_path: str, commit_message: str, username: str, password: str):
    """ Deploys the current trunk to the SVN central repository

        Args:
            :param plugin_root_path: Source path which contains the plugin code.
            :param commit_message: Comment for the commit that will be created
            :param username: Username of the owner of the repository who will perform the operation
            :param password: Password of the owner of the repository who will perform the operation
    """

    try:
        # Check plugin root exist
        __check_plugin_path_exists(plugin_root_path)

        # Check commit comment, username & password are not empty
        __check_parameters(commit_message, username, password)

        # Call svn_add
        plugin_trunk_path: str = str(pathlib.Path(plugin_root_path).joinpath('trunk'))
        __check_plugin_path_exists(plugin_trunk_path)
        logging.info(literals.get("wp_plugin_add").format(plugin_path=plugin_trunk_path))
        svn.svn_add(f'{plugin_trunk_path}/*')

        # Call svn_checkin
        logging.info(literals.get("wp_plugin_checkin").format(plugin_path=plugin_trunk_path))
        svn.svn_checkin(commit_message, username, password)

    except (FileNotFoundError, ValueError) as exception:
        logging.exception(exception)
        return


def deploy_release_tag(plugin_root_path: str, tag_name: str, commit_message: str, username: str, password: str):
    """ Creates and deploys the current trunk to the SVN central repository as a new tag

        Args:
            :param plugin_root_path: Source path which contains the plugin code.
            :param tag_name: Tag name to be created. Must not exist.
            :param commit_message: Comment for the commit that will be created.
            :param username: Username of the owner of the repository who will perform the operation
            :param password: Password of the owner of the repository who will perform the operation
    """

    try:
        # Check commit comment, username & password are not empty
        __check_parameters(commit_message, username, password)

        # Check plugin root exist
        __check_plugin_path_exists(plugin_root_path)

        # Create release tag if not exist
        create_release_tag(plugin_root_path, tag_name)

        # Add and checkin the new tag created (it will be created on the current trunk)
        plugin_tag_path = pathlib.Path(plugin_root_path).joinpath('tags', tag_name)
        logging.info(literals.get("wp_plugin_add").format(plugin_path=plugin_tag_path))
        svn.svn_add(f'{plugin_tag_path}/*')
        logging.info(literals.get("wp_plugin_checkin").format(plugin_path=plugin_tag_path))
        svn.svn_checkin(commit_message, username, password)

    except (FileNotFoundError, ValueError) as exception:
        logging.exception(exception)
        return


def parse_plugin_config_in_plugin_file(plugin_data: dict, plugin_root_path: str, plugin_file_name: str):
    """ Replaces plugin config values on readme.txt file

        Args:
            :param plugin_data: Plugin config parsed data
            :param plugin_root_path: Plugin's root path.
            :param plugin_file_name: Plugin file name to replace
    """
    # Get readme.txt file
    plugin_file_path: str = paths.get_file_path_from_pattern(plugin_root_path, plugin_file_name, True)
    # Replace data
    with open(plugin_file_path, 'r') as plugin_file:
        file_content = plugin_file.read()
        for key, value in plugin_data.items():
            if isinstance(value, list):
                value = ', '.join(value)
            file_content = file_content.replace(f'[{key}]', value)
    with open(plugin_file_path, 'w') as plugin_replaced_file:
        plugin_replaced_file.write(file_content)


def __check_parameters(commit_message: str, username: str, password: str):
    """ Checks parameters passed and raises an exception if they don't fit the spec

        Args:
            :param commit_message: Comment for the commit that will be created.
            :param username: Username of the owner of the repository who will perform the operation.
            :param password: Password of the owner of the repository who will perform the operation.
    """
    if commit_message is None or commit_message == '':
        raise ValueError(literals.get("wp_mandatory_parameter").format(parameter_name=commit_message))
    if username is None or username == '':
        raise ValueError(literals.get("wp_mandatory_parameter").format(parameter_name=username))
    if password is None or password == '':
        raise ValueError(literals.get("wp_mandatory_parameter").format(parameter_name=password))


def __check_plugin_path_exists(plugin_path: str):
    """ Checks if a plugin relative path exists or not. If not, an exception will be raised.

        Args:
            :param plugin_path: Plugin's relative path to check.
    """
    if not pathlib.Path.exists(pathlib.Path(plugin_path)):
        raise FileNotFoundError(literals.get("wp_non_valid_dir_path"))


if __name__ == "__main__":
    help(__name__)
