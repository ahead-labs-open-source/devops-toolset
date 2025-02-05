"""Contains several tools for WordPress"""

import devops_toolset.tools.dicts
import devops_toolset.core.log_tools
import devops_toolset.filesystem.paths as paths
import devops_toolset.filesystem.tools
import devops_toolset.filesystem.zip
import devops_toolset.project_types.wordpress.constants as wp_constants
import devops_toolset.project_types.wordpress.wp_cli as wp_cli
import devops_toolset.project_types.wordpress.wp_theme_tools as wp_theme_tools
import devops_toolset.tools.git as git_tools
import json
import logging
import os
import pathlib
import re
import requests
import shutil
import stat
import sys
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.core.app import App
from devops_toolset.devops_platforms.azuredevops.Literals import Literals as PlatformLiterals
from devops_toolset.project_types.wordpress.Literals import Literals as WordpressLiterals
from devops_toolset.project_types.wordpress.basic_structure_starter import BasicStructureStarter
from devops_toolset.project_types.wordpress.commands import Commands as WordpressCommands
from devops_toolset.project_types.wordpress.constants import ProjectStructureType
from typing import List, Tuple, Union

app: App = App()
platform_specific_restapi = app.load_platform_specific("restapi")
literals = LiteralsCore([WordpressLiterals])
platform_literals = LiteralsCore([PlatformLiterals])
commands = CommandsCore([WordpressCommands])


def add_cloudfront_forwarded_proto_to_config(
        environment_config: dict, wordpress_path: str):
    """ Adds HTTP_CLOUDFRONT_FORWARDED_PROTO snippet to wp-config.php

    Args:
        environment_config: Environment configuration.
        wordpress_path: Path to wordpress installation.
    """

    # Exit if there is no True setting for AWS Cloudfront
    if "aws_cloudfront" not in environment_config["settings"] \
            or environment_config["settings"]["aws_cloudfront"] is False:
        return

    file_path = pathlib.Path.joinpath(pathlib.Path(wordpress_path), "wp-config.php")
    if file_path.exists():
        with open(file_path, "r+") as config:
            config_content = config.read()
            pattern = r'/\*\*.*\nrequire_once.*'
            match = re.search(pattern, config_content)
            if match:
                content_new = re.sub(
                    pattern,
                    get_snippet_cloudfront() + '\n' + match.group(),
                    config_content)
                config.seek(0)
                config.write(content_new)


def add_wp_options(wp_options: dict, wordpress_path: str, debug: bool = False):
    """Adds or updates WordPress options in the wp_options table

    Args:
        wp_options: WordPress options.
        wordpress_path: Path to the WordPress installation.
        debug: If True logs debug information.
    """

    for option in wp_options:
        wp_cli.add_update_option(option, wordpress_path, debug)


def check_wordpress_files_locale(wordpress_path: str, locale: str):
    """Checks if the files in a WordPress directory have a specific locale
    installed and setup.

    Args:
        wordpress_path: Path to the WordPress directory.
        locale: WordPress locale to be checked.
    """

    # Check if $wp_local_package is defined in wp-includes/version.php
    version_file_path = pathlib.Path.joinpath(pathlib.Path(wordpress_path), wp_constants.FileNames.WORDPRESS_VERSION)

    locale_found, match = devops_toolset.filesystem.tools.search_regex_in_text_file(
        wp_constants.Expressions.WORDPRESS_REGEX_VERSION_LOCAL_PACKAGE, str(version_file_path))

    # Check if $wp_local_package value matches locale setting
    if locale_found:
        wordpress_files_locale = match.groups()[0]
        locale_ok = wordpress_files_locale == locale
        if not locale_ok:
            logging.warning(literals.get("wp_wordpress_zip_file_locale_mismatch").format(
                locale=locale,
                wordpress_files_locale=wordpress_files_locale
            ))
    elif not locale_found and locale != wp_constants.DefaultValues.WORDPRESS_DEFAULT_LOCALE:
        logging.warning(literals.get("wp_wordpress_wp_local_package_value_not_set").format(
            version_file_path=wp_constants.FileNames.WORDPRESS_VERSION
        ))

    # Check wp-content/languages directory and <locale>.po and <locale>.mo files exist
    wordpress_path_obj = pathlib.Path(wordpress_path)
    languages_directory_path = pathlib.Path.joinpath(wordpress_path_obj, wp_constants.FileNames.WORDPRESS_LANGUAGES)
    po_file_path = pathlib.Path.joinpath(languages_directory_path, f"{locale}.po")
    mo_file_path = pathlib.Path.joinpath(languages_directory_path, f"{locale}.mo")
    languages_found = \
        os.path.exists(languages_directory_path) and os.path.exists(po_file_path) and os.path.exists(mo_file_path)

    if not languages_found and locale != wp_constants.DefaultValues.WORDPRESS_DEFAULT_LOCALE:
        logging.warning(literals.get("wp_wordpress_zip_file_no_translations").format(locale=locale))


def check_wordpress_zip_file_format(zip_file_path: str) -> tuple[bool, Union[str, None]]:
    """Checks if the file name format of the WordPress zip file is correct.

    Args:
        zip_file_path: Path to the zip file.

    Returns:
        True and file version number if format is correct, False and None
        otherwise.
    """

    file_name: str = os.path.basename(zip_file_path)

    matches = re.search(wp_constants.FileNames.WORDPRESS_ZIP_FILE_NAME_REGEX, file_name)

    if matches is not None and matches.group(1):
        version = matches.group(1)
        logging.info(literals.get("wp_wordpress_zip_file_format_ok").format(version=version))
        return True, version
    else:
        logging.error(literals.get("wp_wordpress_zip_file_format_error"))
        return False, None


def convert_wp_config_token(token: str, wordpress_path: str) -> str:
    """ Replaces [] tokens inside configuration parameters using php syntax.
    More info at https://www.php.net/manual/en/datetime.format.php

    Args:
        token: The token to replace (for example: [date|Y.m.d-Hisve])
        wordpress_path: WordPress installation path
    """

    result = token

    # parse token [date|Y.m.d-Hisve]
    if token.find("[date|") != -1:
        date_format = token[token.find("[date|") + 1:token.find("]")]
        date_token = date_format.split("|")[1]
        result = result.replace(
            "[" + date_format + "]", wp_cli.eval_code("echo date('" + date_token + "');", wordpress_path))

    return result


def create_configuration_file(environment_configuration: dict, wordpress_path: str, database_user_password: str):
    """Creates the wp-config-php WordPress configuration file using WP-CLI.

    All parameters are obtained from a site configuration file.

    For more information see:
        https://developer.wordpress.org/cli/commands/config/create/

    Args:
        environment_configuration: Parsed environment configuration.
        wordpress_path: Path to WordPress files.
        database_user_password: Password for the database user configured in at the wp-config.php file.
    """

    wp_cli.create_configuration_file(wordpress_path=wordpress_path,
                                     db_host=environment_configuration["database"]["host"],
                                     db_name=environment_configuration["database"]["db_name"],
                                     db_user=environment_configuration["database"]["db_user"],
                                     db_pass=database_user_password,
                                     db_prefix=environment_configuration["database"]["table_prefix"],
                                     db_charset=environment_configuration["database"]["charset"],
                                     db_collate=environment_configuration["database"]["collate"],
                                     skip_check=environment_configuration["database"]["skip_check"],
                                     debug=environment_configuration["wp_cli_debug"]
                                     )


def create_users(users: list, wordpress_path: str, debug: bool):
    """Creates WordPress users.

    Args:
        users: Users based on #/definitions/user at
            https://dev.aheadlabs.com/schemas/json/wordpress-site-schema.json
        wordpress_path: Path to WordPress files.
        debug: If present, --debug will be added to the command showing all debug trace information.
    """

    for user in users:
        # Create the user if does not exist
        if not wp_cli.user_exists(user["user_login"], wordpress_path, debug):
            wp_cli.create_user(user, wordpress_path, debug)

        # Warn the user I am skipping the creation
        else:
            logging.warning(literals.get("wp_wpcli_user_exists").format(user=user["user_login"]))


def create_wp_cli_bat_file(phar_path: str):
    """Creates a .bat file for WP-CLI.

    Args:
        phar_path: Path to the .phar file.
    """

    path = pathlib.Path(phar_path)
    bat_path = pathlib.Path.joinpath(path.parent, "wp.bat")

    with open(bat_path, "w") as bat:
        bat.write("@ECHO OFF\n")
        bat.write(f"php \"{phar_path}\" %*")


def delete_wordpress_content_based_on_settings(wp_content_path: pathlib.Path, site_configuration: dict):
    """Deletes WordPress wp-content directory if skip_content_download is True,
    except themes and plugins that are specified to be installed on the
    settings file.

    Args:
        wp_content_path: Path to wp-content directory.
        site_configuration: Site configuration.
    """

    # Delete all themes that are not specified in settings
    themes_in_settings = list(map(lambda theme: theme["name"], site_configuration["settings"]["themes"]))
    for child in pathlib.Path(wp_content_path, "themes").iterdir():
        if child.name not in themes_in_settings and child.name != "index.php":
            shutil.rmtree(child, ignore_errors=True)

    # Delete all plugins that are not specified in settings
    plugins_in_settings = list(map(lambda plugin: plugin["name"], site_configuration["settings"]["plugins"]))
    for child in pathlib.Path(wp_content_path, "plugins").iterdir():
        name: str = re.search(wp_constants.Expressions.WORDPRESS_FILTER_PLUGIN_NAME, child.name).groups()[0]
        if name not in plugins_in_settings and child.name != "index.php":
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            elif child.is_file():
                os.remove(child)

    logging.warning(literals.get("wp_wordpress_zip_file_removed_wp_content"))


def download_wordpress(site_configuration: dict, destination_path: str, wp_cli_debug: bool = False):
    """ Downloads the latest version of the WordPress core files using a site configuration file.

    For more information see:
        https://developer.wordpress.org/cli/commands/core/download/

    Args:
        site_configuration: parsed site configuration.
        destination_path: Path where WP-CLI will download WordPress.
        wp_cli_debug: True if logging must be verbose.
    """

    if not paths.is_valid_path(destination_path):
        raise ValueError(literals.get("wp_non_valid_dir_path"))

    version = site_configuration["settings"]["version"]
    locale = site_configuration["settings"]["locale"]
    skip_content = site_configuration["settings"]["skip_content_download"]
    wp_cli.download_wordpress(destination_path, version, locale, skip_content, wp_cli_debug)
    git_tools.purge_gitkeep(destination_path)


def download_wordpress_plugin(plugin_config: dict, destination_path: str):
    """Downloads a WordPress plugin from an URL.

    NOTE: The URL must download a zip file that contains the plugin. If the ZIP
        contains a non-standard inner structure, the calling process will
        produce side-effects.

    Args:
        plugin_config: Plugin configuration.
        destination_path: Path where the plugin will be downloaded.
    """

    with open(destination_path, "wb") as file:
        response = requests.get(plugin_config["source"])
        file.write(response.content)


def export_database(environment_config: dict, wordpress_path: str, dump_file_path: str):
    """Exports a WordPress database to a dump file using a site configuration file.

    All parameters are obtained from a site configuration file.

    For more information see:
        https://developer.wordpress.org/cli/commands/db/export/

    Args:
        environment_config: parsed site configuration.
        wordpress_path: Path to WordPress files.
        dump_file_path: Path to the destination dump file.
    """

    wp_cli.export_database(wordpress_path, dump_file_path, environment_config["wp_cli_debug"])


def find_wordpress_zip_file_in_path(path: str) -> Union[str, None]:
    """Finds the path to the WordPress zip file inside a specific directory
    path.

    Args:
        path: Path to the directory where the zip file should be found.
    """

    return devops_toolset.filesystem.paths.get_file_path_from_pattern(
        path, wp_constants.FileNames.WORDPRESS_ZIP_FILE_NAME_FORMAT)


def get_constants() -> dict:
    """Gets all the constants from a WordPress constants resource.

    For more information see:
        https://dev.aheadlabs.com/schemas/json/wordpress-constants-schema.json


    Returns:
        All the constants in a dict object.
    """

    script_directory_path = pathlib.Path(os.path.realpath(__file__)).parent
    wordpress_constants_path = \
        pathlib.Path.joinpath(script_directory_path, wp_constants.FileNames.WORDPRESS_CONSTANTS_JSON)

    with open(wordpress_constants_path, 'r') as wordpress_constants_file:
        data = json.load(wordpress_constants_file)

    return data


def get_environment(site_config: dict, environment_name: str) -> dict:
    """Gets the environment that matches the name passed as a parameter.

    Args:
        site_config: Site configuration.
        environment_name: Name of the environment to be retrieved.
    """

    filtered = filter(lambda environment_x: environment_x['name'] == environment_name, site_config['environments'])
    environment_list = list(filtered)

    if len(environment_list) == 0:
        raise ValueError(literals.get('wp_env_x_not_found').format(environment=environment_name))

    if len(environment_list) > 1:
        logging.warning(literals.get('wp_environment_x_found_multiple').format(environment=environment_name))

    environment = environment_list[0]

    # Update URL constants (with the _url suffix) prepending the base URL
    url_keys = devops_toolset.tools.dicts.filter_keys(environment["wp_config"], "^(content|plugin)_url$")
    for key in url_keys:
        environment["wp_config"][key]["value"] = environment["base_url"] + environment["wp_config"][key]["value"]

    return environment


def get_default_project_structure(structure_type: ProjectStructureType, token_replacements: dict = None) -> dict:
    """Gets the default project structure file path for a WordPress project or
    a development theme project.

    For more information see:
        https://dev.aheadlabs.com/schemas/json/project-structure-schema.json

    Args:
        structure_type: Type of project structure to get.
        token_replacements: Key-value pairs to replace in the project structure file.
            Tokens in the file must be enclosed in double braces but this parameter must
            be braces free. ie: {{token}} in the file and token in the parameter value.

    Returns:
        Project structure as a dict.
    """

    wordpress_directory_path = pathlib.Path(os.path.realpath(__file__)).parent

    if structure_type is structure_type.WORDPRESS:
        project_structure_path = pathlib.Path(
            wordpress_directory_path, "default-files", wp_constants.FileNames.DEFAULT_WORDPRESS_PROJECT_STRUCTURE)
    else:
        # type is type.THEME
        project_structure_path = pathlib.Path(
            wordpress_directory_path, "default-files", wp_constants.FileNames.DEFAULT_WORDPRESS_DEV_THEME_STRUCTURE)

    with open(project_structure_path, 'r') as project_structure_file:
        # Get file content
        content = project_structure_file.read()

        # Replace tokens
        if token_replacements is not None:
            for key in token_replacements:
                content = content.replace("{{" + key + "}}", token_replacements[key])

        # Convert to dict
        data = json.loads(content)

    return data


def get_required_file_paths(path: str, required_file_patterns: List[str]) -> Tuple:
    """Returns file paths in a tuple from the file name patterns.

    Args:
        path: Where to look for the files.
        required_file_patterns: glob patterns of the file names to be found.

    Returns:
        Tuple with the file paths in the following order:
        - site configuration JSON file
        - site environments JSON file
        - project structure JSON file
    """

    result = []
    for required_file_pattern in required_file_patterns:
        result.append(paths.get_file_path_from_pattern(path, required_file_pattern))

    if len(result) == 0:
        logging.info(literals.get("wp_required_file_paths_not_found"))
    else:
        devops_toolset.core.log_tools.log_indented_list(literals.get("wp_required_file_paths_found"),
                                                        result, devops_toolset.core.log_tools.LogLevel.info)

    return tuple(result)


def get_site_configuration(path: str) -> dict:
    """Gets the WordPress site configuration from a site configuration file.

    For more information see:
        https://dev.aheadlabs.com/schemas/json/wordpress-site-schema.json

    Args:
        path: Full path to the WordPress project structure file.

    Returns:
        Site configuration in a dict object.
    """

    with open(path, "r", encoding="utf-8") as config_file:
        data = config_file.read()
        return json.loads(data)


def get_snippet_cloudfront():
    """ Gets HTTP_CLOUDFRONT_FORWARDED_PROTO snippet from a default file.

    Returns:
        HTTP_CLOUDFRONT_FORWARDED_PROTO snippet as a string.
    """

    current_path: pathlib.Path = pathlib.Path(os.path.realpath(__file__))
    default_cloudfront_forwarded_proto_php_file_path: pathlib.Path = pathlib.Path.joinpath(
        current_path.parent, "default-files", wp_constants.FileNames.DEFAULT_CLOUDFRONT_FORWARDED_PROTO_PHP)

    if default_cloudfront_forwarded_proto_php_file_path.exists():
        with open(default_cloudfront_forwarded_proto_php_file_path, "r") as file:
            return file.read()
    else:
        logging.error(literals.get("wp_file_not_found").format(file=default_cloudfront_forwarded_proto_php_file_path))


def get_wordpress_path_from_root_path(root_path: str, constants: dict = None) -> str:
    """ Gets the wordpress path based on the constants.json from a desired root path

    Args:
        root_path: Full path of the project.
        constants: WordPress constants.
    """

    logging.info(literals.get("wp_root_path").format(path=root_path))

    # Get constants if not passed
    if constants is None:
        constants = get_constants()

    # Get wordpress path from the constants
    wordpress_relative_path = constants["paths"]["wordpress"]
    wordpress_path = pathlib.Path.joinpath(pathlib.Path(root_path), wordpress_relative_path).as_posix()
    logging.info(literals.get("wp_wordpress_path").format(path=wordpress_path))

    return wordpress_path


def import_content_from_configuration_file(site_configuration: dict, environment_config: dict,
                                           root_path: str, global_constants: dict):
    """ Imports WordPress posts content specified on a site_configuration file.
    NOTE: content entries in the configuration file must be named after post
    types in singular form. Otherwise they will be ignored. ie: post, page.

    Args:
        site_configuration: Parsed site configuration.
        environment_config: Parsed environment configuration.
        root_path: Path to the root repository.
        global_constants: Parsed global constants.
    """

    # If no content to import, then do nothing
    if "content" not in site_configuration:
        return

    # Get paths and parameters
    wxr_path = pathlib.Path.joinpath(pathlib.Path(root_path), global_constants["paths"]["content"]["wxr"])
    wordpress_path = str(pathlib.Path.joinpath(pathlib.Path(root_path), global_constants["paths"]["wordpress"]))
    author_handling = site_configuration["content"]["author_handling"]

    if author_handling == "mapping.csv":
        authors_path = str(pathlib.Path.joinpath(wxr_path, "mapping.csv"))
        authors = authors_path if not devops_toolset.filesystem.tools.is_file_empty(authors_path) else "skip"
    else:
        authors = author_handling

    debug_info = environment_config["wp_cli_debug"]

    for content_type in site_configuration["content"]["sources"]:
        # File name will be the {wxr_path}/{content_type}.xml
        content_path = str(pathlib.Path.joinpath(wxr_path, f"{content_type}.xml"))

        # Delete content before importing (to avoid duplicating content)
        wp_cli.delete_post_type_content(wordpress_path, content_type, debug_info)

        # Import new content
        wp_cli.import_wxr_content(wordpress_path, content_path, authors, debug_info)


def install_plugins_from_configuration_file(site_configuration: dict, environment_config: dict, global_constants: dict,
                                            root_path: str, skip_partial_dumps: bool, skip_file_relocation: bool):
    """Installs WordPress's plugin files using WP-CLI.

       For more information see:
           https://developer.wordpress.org/cli/commands/plugin/install/

       Args:
           site_configuration: Parsed site configuration.
           environment_config: Parsed environment configuration.
           global_constants: Parsed global constants.
           root_path: Path to project root.
           skip_partial_dumps: If True skips database dumps.
           skip_file_relocation: If True skips file relocation.
       """

    # Get data needed in the process
    plugins: dict = site_configuration["settings"]["plugins"]
    root_path_obj = pathlib.Path(root_path)
    wordpress_path = str(pathlib.Path.joinpath(root_path_obj, global_constants["paths"]["wordpress"]))
    plugins_path = str(pathlib.Path.joinpath(root_path_obj, global_constants["paths"]["content"]["plugins"]))
    debug_info = environment_config["wp_cli_debug"]

    for plugin in plugins:
        # Get plugin path
        plugin_path = \
            paths.get_file_path_from_pattern_multiple_paths([plugins_path, root_path], f"{plugin['name']}*.zip")
        logging.info(literals.get("wp_plugin_path").format(path=plugin_path))

        # Download plugin if needed
        if plugin["source_type"] == "url":
            download_wordpress_plugin(plugin, plugin_path)

            # Once downloaded, should have a .zip under plugins' path, so can freely add this source as a .zip one for
            # further installing this plugin as a zip
            plugin["source_type"] = "zip"

        if plugin["source_type"] == "zip":
            plugin["source"] = plugin_path

        wp_cli.install_plugin(plugin["name"], wordpress_path, plugin["activate"], plugin["force"], plugin["source"],
                              debug_info)

        if not skip_file_relocation and plugin["source_type"] == "zip":
            paths.move_files(
                str(pathlib.Path(plugin_path).parent),
                plugins_path,
                f"{plugin['name']}*.zip",
                False
            )

        # Backup database after plugin install
        if not skip_partial_dumps:
            database_path = pathlib.Path.joinpath(root_path_obj, global_constants["paths"]["database"])
            core_dump_path_converted = convert_wp_config_token(
                site_configuration["settings"]["dumps"]["plugins"], wordpress_path)
            database_core_dump_path = pathlib.Path.joinpath(database_path, core_dump_path_converted)
            export_database(site_configuration, wordpress_path, database_core_dump_path.as_posix())

        # Warn the user we are skipping the backup dump
        else:
            logging.warning(literals.get("wp_wpcli_export_db_skipping_as_set").format(dump="plugins"))

    # Purge .gitkeep
    git_tools.purge_gitkeep(plugins_path)


def install_wordpress_core(site_config: dict, environment_config: dict, wordpress_path: str, admin_password: str):
    """Installs WordPress core files using a site configuration file.

        For more information see:
            https://developer.wordpress.org/cli/commands/core/install/

        Args:
            site_config: Parsed site configuration.
            environment_config: Parsed environment configuration.
            wordpress_path: Path to WordPress files.
            admin_password: Password for the WordPress administrator user
        """

    # Set/expand variables before using WP CLI
    admin_user = site_config["settings"]["wp_admin"]["user"]
    admin_email = site_config["settings"]["wp_admin"]["email"]
    skip_email = site_config["settings"]["wp_admin"]["skip_email"]
    title = site_config["settings"]["title"]
    debug_info = environment_config["wp_cli_debug"]
    url = environment_config["wp_config"]["site_url"]["value"]
    wp_cli.install_wordpress_core(wordpress_path, url, title, admin_user, admin_email, admin_password,
                                  skip_email, debug_info)


def install_wp_cli(install_path: str = "/usr/local/bin/wp"):
    """Downloads and installs the latest version of WP-CLI.

    For more information see:
        https://make.wordpress.org/cli/handbook/installing/

    Args:
        install_path: Path where WP-CLI will be installed. It must be in the
            PATH/BIN of the operating system.
    """

    wp_cli_phar = "wp-cli.phar"
    wp_cli_download_url = f"https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/{wp_cli_phar}"
    install_path = pathlib.Path(install_path)
    file_path = str(pathlib.Path.joinpath(install_path, wp_cli_phar))

    if not pathlib.Path.is_dir(install_path):
        raise ValueError(literals.get("wp_not_dir"))

    logging.info(literals.get("wp_wpcli_downloading").format(url=wp_cli_download_url))
    response = requests.get(wp_cli_download_url)

    with open(file_path, "wb") as cli:
        cli.write(response.content)

    file_stat = os.stat(file_path)
    os.chmod(file_path, file_stat.st_mode | stat.S_IEXEC)

    if sys.platform == "win32":
        create_wp_cli_bat_file(file_path)

    wp_cli.wp_cli_info()


def install_wordpress_site(site_configuration: dict, environment_config: dict, global_constants: dict,
                           root_path: str, admin_password: str, skip_partial_dumps: bool = False):
    """Installs WordPress core files using WP-CLI.

    This operation requires cleaning the db and doing a backup after the process.

    For more information see:
        https://developer.wordpress.org/cli/commands/core/install/

    Args:
        site_configuration: Parsed site configuration.
        environment_config: Parsed environment configuration.
        global_constants: Parsed global constants.
        root_path: Path to site installation.
        admin_password: Password for the WordPress administrator user.
        skip_partial_dumps: If True skips database dump.
    """

    database_path = global_constants["paths"]["database"]
    root_path_obj = pathlib.Path(root_path)
    wordpress_path = str(pathlib.Path.joinpath(root_path_obj, global_constants["paths"]["wordpress"]))
    wordpress_path_as_posix = str(pathlib.Path(wordpress_path).as_posix())

    # Install wordpress
    install_wordpress_core(site_configuration, environment_config, wordpress_path_as_posix, admin_password)

    # Update description option
    description = site_configuration["settings"]["description"]
    wp_cli.update_database_option(
        "blogdescription", description, wordpress_path_as_posix, environment_config["wp_cli_debug"])

    # Backup database
    if not skip_partial_dumps:
        core_dump_path_converted = \
            convert_wp_config_token(site_configuration["settings"]["dumps"]["core"], wordpress_path)
        database_core_dump_directory_path = pathlib.Path.joinpath(root_path_obj, database_path)
        database_core_dump_path = pathlib.Path.joinpath(database_core_dump_directory_path, core_dump_path_converted)
        export_database(environment_config, wordpress_path_as_posix, database_core_dump_path.as_posix())
        git_tools.purge_gitkeep(database_core_dump_directory_path.as_posix())

    # Warn the user we are skipping the backup dump
    else:
        logging.warning(literals.get("wp_wpcli_export_db_skipping_as_set").format(dump="core"))


def set_wordpress_config_from_configuration_file(
        environment_config: dict, wordpress_path: str, db_user_password: str) -> None:
    """ Sets all configuration parameters in pristine WordPress core files
    Args:
        environment_config: Environment configuration.
        wordpress_path: Path to wordpress installation.
        db_user_password: Database user password.

    """

    # Create wp-config.php file
    create_configuration_file(environment_config, wordpress_path, db_user_password)

    # Get config properties to set from site configuration
    wp_config_properties = environment_config["wp_config"]
    debug = environment_config["wp_cli_debug"]

    # Foreach variable to set: execute wp config set
    for prop in wp_config_properties.values():
        # This value will place the value as it gets, without quotes
        value = prop.get("value")
        raw = type(value) != str
        wp_cli.set_configuration_value(
            prop.get("name"), value, prop.get("type"),
            wordpress_path, raw, debug)

    # Add cloudfront snippet to wp_config.php if needed
    add_cloudfront_forwarded_proto_to_config(environment_config, wordpress_path)


def setup_database(environment_config: dict, wordpress_path: str, db_user_password: str, db_admin_password: str = ""):
    """ Uses wp cli create to create a new database from configuration file

    Args:
        environment_config: Parsed environment configuration.
        wordpress_path: Path to WordPress files.
        db_user_password: Password of the database user to be created.
        db_admin_password:  Database administrator user password.
    """

    db_host = environment_config["database"]["host"]
    schema = environment_config["database"]["db_name"]
    db_admin_user = environment_config["database"]["db_admin_user"]
    db_user = environment_config["database"]["db_user"]
    wp_cli_debug = environment_config["wp_cli_debug"]

    wp_cli.create_database(wordpress_path, wp_cli_debug, db_admin_user, db_admin_password, schema)

    wp_cli.create_wordpress_database_user(
        wordpress_path, db_admin_user, db_admin_password, db_user, db_user_password, schema, db_host)


def scaffold_wordpress_basic_project_structure(root_path: str, site_configuration: dict) -> None:
    """ Creates a basic structure of a WordPress project based on a project
    structure file.

    Args:
        root_path: Full path where the structure will be created.
        site_configuration: parsed site configuration.
    """

    logging.info(literals.get("wp_creating_project_structure"))

    # Get src theme if it exists in the configuration
    src_theme: dict = wp_theme_tools.get_src_theme(site_configuration["settings"]["themes"])

    # Get guess file path
    structure_file_path = pathlib.Path.joinpath(pathlib.Path(root_path), "wordpress-project-structure.json")

    # Parse project structure configuration
    if pathlib.Path.exists(structure_file_path):
        project_structure = get_site_configuration(str(structure_file_path))
        logging.info(literals.get("wp_project_structure_creating_from_file").format(file_name=structure_file_path))
    else:
        project_structure = get_default_project_structure(ProjectStructureType.WORDPRESS)
        logging.info(literals.get("wp_project_structure_creating_from_default_file").format(
            resource=wp_constants.FileNames.DEFAULT_WORDPRESS_PROJECT_STRUCTURE
        ))

    token_replacements: dict = {
        "project-name": site_configuration["settings"]["project"]["name"],
        "project-version": site_configuration["settings"]["project"]["version"],
        "theme-name": src_theme["name"] if src_theme is not None else "",
    }
    project_starter = BasicStructureStarter(token_replacements)

    # Iterate through every item recursively
    for item in project_structure["items"]:
        project_starter.add_item(item, root_path)

    logging.info(literals.get("wp_created_project_structure"))


def unzip_wordpress(site_configuration: dict, zip_file_path: str, destination_path: str):
    """Unzips a WordPress wordpress-x.y.z.zip file from the file system.

    Args:
        site_configuration: parsed site configuration.
        zip_file_path: Path to the WordPress zip file.
        destination_path: Path where WordPress will be unpacked (creates
            wordpress directory if the official file is unzipped).
    """

    # Check if file name format is correct
    filename_ok, version = check_wordpress_zip_file_format(zip_file_path)

    # Check if version is correct
    settings_version = site_configuration["settings"]["version"]
    if version == settings_version:
        logging.info(literals.get("wp_wordpress_zip_file_version_ok"))
        version_ok = True
    elif settings_version == "latest":
        logging.warning(literals.get("wp_wordpress_zip_file_version_settings_latest"))
        version_ok = True
    else:
        logging.warning(literals.get("wp_wordpress_zip_file_version_not_valid"))
        version_ok = False

    if not version_ok:
        logging.warning(literals.get("wp_wordpress_zip_file_and_settings_version_mismatch").format(
            version=version,
            settings_version=settings_version
        ))

    # Unzip files
    devops_toolset.filesystem.zip.unzip_file(zip_file_path, destination_path)

    # Check if locale is correct
    wordpress_path = pathlib.Path(pathlib.Path(destination_path), "wordpress")
    check_wordpress_files_locale(str(wordpress_path), site_configuration["settings"]["locale"])

    # Delete wp-content if skip_content_download is True
    delete_wordpress_content_based_on_settings(
        pathlib.Path(wordpress_path, wp_constants.FileNames.WORDPRESS_CONTENT),
        site_configuration
    )


if __name__ == "__main__":
    help(__name__)
