""" This script will generate and configure a Wordpress site based on the
required configuration files"""

import argparse
import json
import logging
import pathlib
import requests
import devops_toolset.core.log_tools
import devops_toolset.filesystem.paths as paths
import os
import devops_toolset.project_types.wordpress.constants as constants
import devops_toolset.project_types.wordpress.wp_theme_tools as theme_tools
import devops_toolset.project_types.wordpress.wptools
import shutil
import devops_toolset.tools.cli as cli
import devops_toolset.tools.argument_validators
import devops_toolset.tools.devops_toolset_utils
import devops_toolset.tools.git as git_tools
from clint.textui import prompt
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.core.app import App
from devops_toolset.devops_platforms.constants import Urls
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals

app: App = App()
literals = LiteralsCore([WordpressLiterals])


def main(root_path: str, db_user_password: str, db_admin_password: str, wp_admin_password: str,
         environment: str, additional_environments: list, environments_db_user_passwords: dict,
         create_db: bool, skip_partial_dumps: bool, create_development_theme: bool, **kwargs_):
    """Generates a new Wordpress site based on the site configuration file

    Args:
        root_path: Path to the repository root.
        db_user_password: Password for the database user.
        db_admin_password: Password for the database admin user.
        wp_admin_password: Password for the WordPress admin user.
        environment: Name of the environment to be processed.
        additional_environments: Additional environments to create additional
            wp-config.php files.
        environments_db_user_passwords: Additional environment db
            user passwords.
        create_db: If True it creates the database and the user.
        skip_partial_dumps: If True skips partial database dumps
            (after installing WordPress, themes and plugins).
        create_development_theme: If True generates the file structure for a
            development theme
        kwargs_: Platform-specific arguments
    """

    # Get basic settings
    global_constants: dict = devops_toolset.project_types.wordpress.wptools.get_constants()
    database_files_path: str = global_constants["paths"]["database"]
    root_path_obj: pathlib.Path = pathlib.Path(root_path)

    # Look for *site.json files in the project path
    required_files_pattern_suffixes: list = list(map(lambda x: f"*{x[1]}", constants.required_files_suffixes.items()))
    required_files_not_present: list[str] = paths.files_exist_filtered(
        root_path, False, required_files_pattern_suffixes)

    # If there are missing required files, ask for using the default ones from GitHub if quiet flag is activated
    if len(required_files_not_present) > 0:
        devops_toolset.core.log_tools.log_indented_list(literals.get("wp_required_files_not_found_detail")
                                                        .format(path=root_path),
                                                        required_files_not_present,
                                                        devops_toolset.core.log_tools.LogLevel.warning)

        devops_toolset.core.log_tools.log_indented_list(
            literals.get("wp_default_files"),
            [Urls.DEFAULT_SITE_ENVIRONMENTS,
             Urls.DEFAULT_SITE_CONFIG],
            devops_toolset.core.log_tools.LogLevel.info)

        # Ask to use defaults
        use_defaults: bool = prompt.yn(literals.get("wp_use_default_files"))
        # If not using defaults, exit
        if not use_defaults:
            logging.critical(literals.get("wp_required_files_mandatory"))
            raise ValueError(literals.get("wp_required_files_not_found").format(path=root_path))

        # Download defaults from GitHub
        for file in required_files_not_present:
            url = Urls.bootstrap_required_files[file]
            file_name = paths.get_file_name_from_url(url)
            file_path = pathlib.Path.joinpath(root_path_obj, file_name)

            response: requests.Response = requests.get(url)
            with open(file_path, "wb") as fw:
                fw.write(response.content)

    # Determine required file paths
    required_file_paths: tuple = devops_toolset.project_types.wordpress.wptools.get_required_file_paths(
        root_path, required_files_pattern_suffixes)

    # Parse configuration data
    site_config: dict = devops_toolset.project_types.wordpress.wptools.get_site_configuration(required_file_paths[0])
    environment_config = devops_toolset.project_types.wordpress.wptools.get_environment(site_config, environment)

    # Get future paths (from the constants.json file)
    wordpress_path: str = devops_toolset.project_types.wordpress.wptools.get_wordpress_path_from_root_path(
        root_path,
        global_constants)
    wordpress_path_as_posix: str = pathlib.Path(wordpress_path).as_posix()
    themes_path: str = theme_tools.get_themes_path_from_root_path(root_path, global_constants)

    # Create project structure & prepare devops-toolset
    devops_toolset.project_types.wordpress.wptools.start_basic_project_structure(root_path)

    # Check for updates / download devops-toolset
    setup_devops_toolset(root_path)

    # Download WordPress core files
    devops_toolset.project_types.wordpress.wptools.download_wordpress(site_config, wordpress_path,
                                                                      environment_config["wp_cli_debug"])

    # Create development theme (if needed)
    if create_development_theme:
        theme_tools.create_development_theme(site_config["settings"]["themes"], root_path, global_constants)

    # Set development themes / plugins ready
    theme_tools.build_theme(site_config["settings"]["themes"], themes_path, root_path)

    # Configure WordPress site
    devops_toolset.project_types.wordpress.wptools.set_wordpress_config_from_configuration_file(site_config,
                                                                                                environment_config,
                                                                                                wordpress_path,
                                                                                                db_user_password)

    # Create database and users
    if create_db:
        devops_toolset.project_types.wordpress.wptools.setup_database(environment_config, wordpress_path,
                                                                      db_user_password,
                                                                      db_admin_password)

    # Install WordPress site
    devops_toolset.project_types.wordpress.wptools.install_wordpress_site(
        site_config, environment_config, global_constants, root_path, wp_admin_password, skip_partial_dumps)

    # Add / update WordPress options
    devops_toolset.project_types.wordpress.wptools.add_wp_options(
        site_config["settings"]["options"], wordpress_path, environment_config["wp_cli_debug"])

    # Install site theme
    theme_tools.install_themes_from_configuration_file(
        site_config, environment_config, global_constants, root_path, skip_partial_dumps, **kwargs_)

    # Install site plugins
    devops_toolset.project_types.wordpress.wptools.install_plugins_from_configuration_file(
        site_config, environment_config, global_constants, root_path, skip_partial_dumps)

    # Create additional users
    devops_toolset.project_types.wordpress.wptools.create_users(site_config["settings"]["users"], wordpress_path,
                                                                environment_config["wp_cli_debug"])

    # Import wxr content
    if not create_development_theme:
        devops_toolset.project_types.wordpress.wptools.import_content_from_configuration_file(
            site_config, environment_config, root_path, wordpress_path, global_constants)

    # Generate additional wp-config.php files
    generate_additional_wpconfig_files(site_config, site_config["environments"], additional_environments,
                                       environments_db_user_passwords, wordpress_path)

    # Delete sample configuration file
    delete_sample_wp_config_file(wordpress_path)

    # Backup database
    core_dump_path_converted = devops_toolset.project_types.wordpress.wptools.convert_wp_config_token(
        site_config["settings"]["dumps"]["core"], wordpress_path)
    database_core_dump_directory_path = pathlib.Path.joinpath(root_path_obj, database_files_path)
    database_core_dump_path = pathlib.Path.joinpath(database_core_dump_directory_path, core_dump_path_converted)
    devops_toolset.project_types.wordpress.wptools.export_database(
        environment_config, wordpress_path_as_posix, database_core_dump_path.as_posix())
    git_tools.purge_gitkeep(database_core_dump_directory_path.as_posix())

    # Move config files to devops directory
    paths.move_files(
        root_path,
        pathlib.Path.joinpath(root_path_obj, global_constants["paths"]["devops"]).as_posix(),
        "*.json",
        False
    )


def setup_devops_toolset(root_path: str):
    """ Checks if devops toolset is present and up to date. In case not, it will be downloaded
    Args:
        root_path: Project's root path
    """
    devops_path_constant = devops_toolset.project_types.wordpress.wptools.get_constants()["paths"]["devops"]
    devops_path = pathlib.Path.joinpath(pathlib.Path(root_path), devops_path_constant, "devops-toolset").as_posix()
    logging.info(literals.get("wp_checking_devops_toolset").format(path=devops_path))
    devops_toolset.tools.devops_toolset_utils.update_devops_toolset(devops_path)


def generate_additional_wpconfig_files(site_config: dict, environments: dict, additional_environments: list,
                                       environments_db_user_passwords: dict,
                                       wordpress_path: str):
    """Generates additional wp-config.php files for different environments.

    Args:
        site_config: Parsed site configuration file
        environments: All the available environment configurations.
        additional_environments: Additional environments to generate
            wp-config.php files for.
        environments_db_user_passwords: Additional environment db user
            passwords.
        wordpress_path: Path to the WordPress installation.
    """

    wordpress_path_obj = pathlib.Path(wordpress_path)
    wp_config_path = pathlib.Path.joinpath(wordpress_path_obj, "wp-config.php")
    wp_config_path_temp = pathlib.Path.joinpath(wordpress_path_obj, "wp-config-temp.php")

    # Rename original file
    if paths.is_valid_path(wp_config_path.as_posix(), True):
        shutil.move(wp_config_path, wp_config_path_temp)

    # Filter environments
    filtered_environments = list(filter(lambda environment_x: environment_x["name"] in additional_environments,
                                        environments))

    # Create additional configuration files for the filtered environments
    for environment in filtered_environments:
        devops_toolset.project_types.wordpress.wptools.set_wordpress_config_from_configuration_file(
            site_config,
            environment,
            wordpress_path,
            environments_db_user_passwords[environment["name"]])
        shutil.move(wp_config_path, pathlib.Path.joinpath(wordpress_path_obj, f"wp-config-{environment['name']}.php"))

    # Rename original file
    if paths.is_valid_path(str(wp_config_path_temp), True):
        shutil.move(wp_config_path_temp, wp_config_path)


def delete_sample_wp_config_file(wordpress_path: str):
    """Deletes the wp-config-sample.php file.

    Args:
        wordpress_path: Path to WordPress.
    """
    file_path = pathlib.Path.joinpath(pathlib.Path(wordpress_path), "wp-config-sample.php")
    if file_path.exists():
        os.remove(str(file_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project-path", action=devops_toolset.tools.argument_validators.PathValidator)
    parser.add_argument("--db-user-password", required=True)
    parser.add_argument("--db-admin-password", required=True)
    parser.add_argument("--wp-admin-password", required=True)
    parser.add_argument("--environment", default="localhost")
    parser.add_argument("--additional-environments", default="")
    parser.add_argument("--additional-environment-db-user-passwords", default={})
    parser.add_argument("--create-db", action="store_true", default=False)
    parser.add_argument("--skip-partial-dumps", action="store_true", default=False)
    parser.add_argument("--create-development-theme", action="store_true", default=False)
    args, args_unknown = parser.parse_known_args()
    kwargs = {}
    for kwarg in args_unknown:
        splited = str(kwarg).split("=")
        kwargs[splited[0]] = splited[1]

    # Parse long attributes to avoid lines longer that 120 characters
    additional_environment_db_user_passwords = args.additional_environment_db_user_passwords.split(",") \
        if args.additional_environment_db_user_passwords != "" else []

    cli.print_title(literals.get("wp_title_generate_wordpress"))
    main(args.project_path, args.db_user_password, args.db_admin_password, args.wp_admin_password,
         args.environment,
         args.additional_environments.split(",") if args.additional_environments != "" else [],
         json.loads(args.additional_environment_db_user_passwords),
         args.create_db,
         args.skip_partial_dumps,
         args.create_development_theme,
         **kwargs)
