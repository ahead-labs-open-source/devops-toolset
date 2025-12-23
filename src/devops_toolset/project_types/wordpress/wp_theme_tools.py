"""Contains several tools and utils for WordPress Themes"""

import devops_toolset.filesystem.parsers as parsers
import devops_toolset.filesystem
import devops_toolset.project_types.node.npm as npm
import devops_toolset.filesystem.paths as paths
import devops_toolset.filesystem.tools
import devops_toolset.filesystem.zip
import json
import logging
import os
import pathlib
import devops_toolset.project_types.wordpress.wp_cli as wp_cli
import devops_toolset.project_types.wordpress.constants as wp_constants
import devops_toolset.project_types.wordpress.wptools as wptools
import re
import devops_toolset.tools.git as git_tools

from devops_toolset.core.app import App
from devops_toolset.core.commands_core import CommandsCore
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.devops_platforms.azuredevops.literals import Literals as PlatformLiterals
from devops_toolset.project_types.wordpress.basic_structure_starter import BasicStructureStarter
from devops_toolset.project_types.wordpress.commands import Commands as WordpressCommands
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals
from devops_toolset.tools import cli
from typing import Union

app: App = App()
platform_specific_environment = app.load_platform_specific("environment")
platform_specific_restapi = app.load_platform_specific("restapi")
literals = LiteralsCore([WordpressLiterals])
platform_literals = LiteralsCore([PlatformLiterals])
commands = CommandsCore([WordpressCommands])


def build_theme(theme_config: dict, theme_path: str, root_path: str):
    """ Builds a theme source into a packaged theme distribution using npm tasks

    Args:
        theme_config: Theme configuration.
        theme_path: Path to the theme in the WordPress repository.
        root_path: Path to the project root.
    """

    logging.info(literals.get("wp_looking_for_src_themes"))

    if theme_config == {}:
        # Src theme not present
        logging.info(literals.get("wp_no_src_themes"))
        return

    if 'build' not in theme_config or not theme_config["build"]:
        # Theme will not be build
        logging.info(literals.get("wp_theme_src_will_not_be_built"))
        return

    theme_path_src = pathlib.Path(theme_path, theme_config["source"])
    theme_path_dist = pathlib.Path(theme_path_src, "dist")
    theme_path_zip = pathlib.Path(theme_path, f"{theme_config['name']}.zip")

    if os.path.exists(theme_path_src):

        theme_slug = theme_config["name"]

        # Change to the theme's source directory
        os.chdir(theme_path_src)

        # Run npm install from the package.json path
        npm.install()

        # Run npm run build to execute the task build with the required parameters
        cli.call_subprocess(commands.get("wp_theme_src_build_production"),
                            log_before_out=[literals.get("wp_webpack_build_before").format(theme_slug=theme_slug)],
                            log_after_out=[literals.get("wp_webpack_build_after").format(theme_slug=theme_slug)],
                            log_after_err=[literals.get("wp_webpack_build_error").format(theme_slug=theme_slug)])

        # Zip dist
        devops_toolset.filesystem.zip.zip_directory(
            theme_path_dist.as_posix(), theme_path_zip.as_posix())

        # Replace project.xml version with the one in the package.json file
        package_json_path = str(pathlib.Path.joinpath(pathlib.Path(theme_path_src, "package.json")))
        project_xml_path = str(pathlib.Path.joinpath(pathlib.Path(root_path), "project.xml"))
        package_json = parsers.parse_json_file(package_json_path)
        devops_toolset.filesystem.tools.update_xml_file_entity_text(
            "./version", package_json["version"], project_xml_path)

    else:
        logging.error(literals.get("wp_file_not_found").format(file=theme_path_src))


def check_theme_configuration(theme: dict) -> bool:
    """Checks that the themes configuration is correct.

    Args:
        theme: Themes configuration.

    Returns:
        True if the configuration is correct, False if incorrect.
    """

    # Check if feed-based themes contain feed information
    if theme["source_type"] == "feed" and "feed" not in theme:
        logging.error(literals.get("wp_theme_feed_no_info").format(theme=theme["name"]))
        logging.warning(literals.get("wp_themes_install_manually"))
        return False

    return True


def check_themes_activation_configuration(themes: dict) -> bool:
    """Checks that the themes configuration is correct.

    Args:
        themes: Themes configuration.

    Returns:
        True if the configuration is correct, False if incorrect.
    """

    # Check if the number of themes is correct
    themes_number = len(themes)
    if themes_number == 0 or themes_number > 2:
        logging.error(literals.get("wp_config_file_bad_themes_number").format(number=themes_number))
        logging.warning(literals.get("wp_themes_install_manually"))
        return False

    # Check if the number of themes to be activated is more or less than one
    themes_to_activate: int = 0
    for theme in themes:
        if theme["activate"]:
            themes_to_activate += 1
    if themes_to_activate == 0 or themes_to_activate > 1:
        logging.error(literals.get("wp_config_file_only_one_activated_theme").format(number=themes_to_activate))
        logging.warning(literals.get("wp_themes_install_manually"))
        return False

    return True


def create_development_theme(site_configuration: dict, root_path: str, constants: dict) -> [dict, None]:
    """ Creates the structure of a development theme.

    Args:
        site_configuration: Site configuration
        root_path: The desired destination path of the theme
        constants: WordPress constants.

    Returns: Theme configuration or None if src theme is not found.
    """

    destination_path = get_themes_path_from_root_path(root_path, constants)

    # Extract theme name from the themes configuration dict
    src_theme = get_src_theme(site_configuration["settings"]["themes"])
    if src_theme is not None:
        theme_slug = src_theme["source"]

        # Check if a structure file is available (should be named as [theme-slug]-wordpress-theme-structure
        structure_file = wp_constants.FileNames.WORDPRESS_DEVELOPMENT_THEME_STRUCTURE_FILE.format(theme_slug=theme_slug)
        structure_file_path = str(pathlib.Path(root_path, structure_file))

        # Create the structure based on the theme_name
        scaffold_basic_theme_structure(destination_path, site_configuration, structure_file_path)

        return src_theme
    else:
        logging.warning(literals.get("wp_src_theme_not_found"))
        return None


def download_wordpress_theme(theme_config: dict, destination_path: str, **kwargs):
    """Downloads a WordPress theme from a feed or a URL.

    NOTE: The URL must download a zip file that contains the theme. If the ZIP
        contains a non-standard inner structure, the calling process will
        produce side effects.

    Args:
        theme_config: Theme configuration.
        destination_path: Path where the theme will be downloaded.
        kwargs: Platform-specific arguments
    """

    source_type: str = theme_config["source_type"]

    if source_type == "feed":
        feed_config = theme_config["feed"]
        matches = re.search(r"https:\/\/dev.azure.com\/(\w+)\/", feed_config["organization_url"])
        organization = matches.group(1)
        if "azdevops_user" in kwargs and "azdevops_token" in kwargs:
            # Download package file
            file_name, file_path = platform_specific_restapi.get_last_artifact(
                organization, feed_config["name"], feed_config["package"], destination_path,
                kwargs["azdevops_user"], kwargs["azdevops_token"])

            # Extract theme zip from package and delete package
            theme_zip_path = f"{theme_config['feed']['package']}/{theme_config['feed']['name']}.zip"
            devops_toolset.filesystem.zip.extract_file_from_zip(file_path, theme_zip_path, destination_path)
            os.remove(file_path)
        else:
            logging.warning(platform_literals.get("azdevops_token_not_found"))
            logging.warning(platform_literals.get("azdevops_download_package_manually"))
    elif source_type == "url":
        paths.download_file(theme_config["source"], destination_path, f"{theme_config['name']}.zip")


def get_environment_by_type(site_configuration: dict, environment: wp_constants.ProjectEnvironmentType) \
        -> Union[dict, None]:
    """Gets an environment node from the site configuration based on its type.

    Args
        site_configuration: Site configuration
        environment: Name of the environment to be retrieved
    """

    environment_name = str(environment.name).lower()
    filtered_environments = list(filter(lambda e: e["type"] == environment_name, site_configuration["environments"]))
    if len(filtered_environments) == 1:
        return filtered_environments[0]
    else:
        raise ValueError(literals.get("wp_environment_of_type_not_found").format(type=environment.name))


def get_src_theme(themes: dict) -> Union[dict, None]:
    """Gets src theme node from the site configuration.

    Args
        themes: Themes node from site configuration

    Returns:
        Src theme configuration or None if not found
    """

    filtered_themes = list(filter(lambda t: t["source_type"] == "src", themes))
    if len(filtered_themes) == 1:
        return filtered_themes[0]
    else:
        logging.warning(literals.get("wp_theme_src_not_found"))
        return None


def get_themes_path_from_root_path(root_path: str, constants: dict) -> str:
    """ Gets the themes path based on the constants.json from a desired root path

    Args:
        root_path: Full path of the project.
        constants: WordPress constants.
    """

    # Get wordpress path from the constants
    themes_relative_path = constants["paths"]["content"]["themes"]
    themes_path = pathlib.Path.joinpath(pathlib.Path(root_path), themes_relative_path).as_posix()
    logging.info(literals.get("wp_themes_path").format(path=themes_path))

    return themes_path


def install_themes_from_configuration_file(site_configuration: dict, environment_config: dict, global_constants: dict,
                                           root_path: str, skip_partial_dumps: bool, **kwargs):
    """Installs WordPress's theme files (and child themes also) using a site configuration file

    For more information see:
        https://developer.wordpress.org/cli/commands/theme/install/

    Args:
        site_configuration: Parsed site configuration.
        environment_config: Parsed environment configuration.
        global_constants: Global constants ofr WordPress.
        root_path: Path to project root.
        skip_partial_dumps: If True skips database dumps.
    """

    child_theme_config: dict
    parent_theme_config: dict

    # Get data needed in the process
    themes: dict = site_configuration["settings"]["themes"]
    root_path_obj = pathlib.Path(root_path)
    wordpress_path = str(pathlib.Path.joinpath(root_path_obj, global_constants["paths"]["wordpress"]))
    themes_path = pathlib.Path.joinpath(root_path_obj, global_constants["paths"]["content"]["themes"])
    debug_info = environment_config["wp_cli_debug"]

    # Check themes activation configuration
    if not check_themes_activation_configuration(themes):
        return

    for theme in themes:
        # Check if theme is already installed
        if int(wp_cli.theme_list_count(wordpress_path, debug_info, theme["name"])) == 1:
            continue

        logging.info(literals.get("wp_themes_installing_theme").format(theme=theme["name"]))

        # Check theme configuration
        if not check_theme_configuration(theme):
            continue

        # Get theme path
        theme_path = str(pathlib.Path.joinpath(themes_path, f"{theme['name']}.zip"))
        logging.info(literals.get("wp_theme_path").format(path=theme_path))
        theme["source"] = theme_path

        # Download theme if needed
        if theme["source_type"] in ["url", "feed"]:
            download_wordpress_theme(theme, str(themes_path), **kwargs)

        # Get template/framework for the theme if it has one
        style_content: bytes = devops_toolset.filesystem.zip.read_text_file_in_zip(theme_path, "style.css")
        metadata: dict = parse_theme_metadata(style_content.decode("utf-8"))
        theme["template"] = metadata["Template"] \
            if "Template" in metadata and metadata["Template"] is not None else None
        theme["version"] = metadata["Version"]

    # Set child theme and parent theme, or just child theme (the one to be activated)
    parent_theme_config, child_theme_config = triage_themes(themes)

    # Install parent theme
    if parent_theme_config:
        wp_cli.install_theme(wordpress_path, parent_theme_config["source"], parent_theme_config["activate"],
                             debug_info, parent_theme_config["name"])
        purge_theme_zip_installation_file_if_generated(parent_theme_config)

    # Install child / single theme
    wp_cli.install_theme(wordpress_path, child_theme_config["source"], child_theme_config["activate"],
                         debug_info, child_theme_config["name"])
    purge_theme_zip_installation_file_if_generated(child_theme_config)

    # Backup database after theme install
    if not skip_partial_dumps:
        database_path = pathlib.Path.joinpath(root_path_obj, global_constants["paths"]["database"])
        core_dump_path_converted = wptools.convert_wp_config_token(
            site_configuration["database"]["dumps"]["theme"], wordpress_path)
        database_core_dump_path = pathlib.Path.joinpath(database_path, core_dump_path_converted)
        wptools.export_database(site_configuration, wordpress_path, database_core_dump_path.as_posix())

    # Warn the user we are skipping the backup dump
    else:
        logging.warning(literals.get("wp_wpcli_export_db_skipping_as_set").format(dump="theme"))


def parse_theme_metadata(style_css_content: str, add_environment_variables: bool = False):
    """Parses metadata from theme's main style sheet style.css.

    Args:
        style_css_content: Content of style.css file.
        add_environment_variables: If True adds every metadata value as an
            environment variable.

    Returns
        dict with metadata extracted in key-value pairs
    """
    logging.info(literals.get("wp_parsing_theme_metadata"))

    metadata: dict = wp_constants.DefaultValues.WORDPRESS_METADATA_EMPTY
    environment_variables: dict = {}

    for key, value in metadata.items():
        regex = key + wp_constants.Expressions.WORDPRESS_REGEX_THEME_METADATA_PARSE
        logging.debug(literals.get("wp_parsing_theme_regex").format(regex=regex))
        matches = re.search(regex, style_css_content)

        if matches is not None and matches.group(1):
            value = matches.group(1)
            metadata[key] = value
            logging.info(literals.get("wp_parsing_theme_matches_found").format(key=key, value=value))

            if add_environment_variables:
                env_key = f"{wp_constants.DefaultValues.WORDPRESS_ENV_VAR_PREFIX}_" \
                          f"{wp_constants.DefaultValues.WORDPRESS_METADATA_PREFIX}_" \
                          f"{value.upper().replace(' ', '_')}"
                environment_variables[env_key] = value
        else:
            logging.warning(literals.get("wp_parsing_theme_no_matches_found").format(key=key))

    if len(environment_variables) > 0:
        platform_specific_environment.create_environment_variables(environment_variables)

    return metadata


def parse_theme_metadata_from_file(style_css_path: str, add_environment_variables: bool = False):
    """Parses metadata from theme's main style sheet style.css.

    Args:
        style_css_path: Path to file style.css.
        add_environment_variables: If True adds every metadata value as an
            environment variable.

    Returns
        dict with metadata extracted in key-value pairs"""

    with open(style_css_path, "r") as style:
        content = style.read()
        return parse_theme_metadata(content, add_environment_variables)


def purge_theme_zip_installation_file_if_generated(theme_config: dict):
    """Purges the ZIP file used for installing the theme if the ZIP has been
    generated (source_type value is not zip in the theme configuration).

    Args:
        theme_config: Parsed theme configuration.
    """

    if theme_config["source_type"] != "zip" and os.path.exists(theme_config["source"]):
        os.remove(theme_config["source"])
        logging.info(literals.get("wp_file_deleted").format(file=theme_config["source"]))


def replace_theme_meta_data_in_package_file(file_path: str, src_theme_configuration: dict):
    """ From the theme configuration, creates a replacements dict and replaces the file_path
    Args:
        file_path: The path of the file to be replaced.
        src_theme_configuration: Dict containing src theme configuration.
    """
    replacements = {"name": src_theme_configuration["source"], "author": {}}
    if "description" in src_theme_configuration:
        replacements["description"] = src_theme_configuration["description"]
    if "tags" in src_theme_configuration:
        replacements["keywords"] = src_theme_configuration["tags"]
    if "author" in src_theme_configuration:
        replacements["author"]["name"] = src_theme_configuration["author"]
    if "author_uri" in src_theme_configuration:
        replacements["author"]["url"] = src_theme_configuration["author_uri"]

    # Open the package_json file
    with open(file_path, 'r') as package_json_file:
        json_data = json.load(package_json_file)
        for key, value in json_data.items():
            if key in replacements:
                json_data[key] = replacements[key]

    with open(file_path, 'w') as package_json_file:
        json.dump(json_data, package_json_file, indent=2)


def replace_theme_meta_data_in_scss_file(file_path: str, src_theme_configuration: dict):
    """ From the theme configuration, creates a replacements dict and replaces the file_path
    Args:
        file_path: The path of the file to be replaced.
        src_theme_configuration: Dict containing src theme configuration.
        """

    # Create a dict of replacements for the style.scss file based on the content of the src theme configuration
    replacements = {"Theme Name": src_theme_configuration["name"], "Text Domain": src_theme_configuration["source"]}
    if "description" in src_theme_configuration:
        replacements["Description"] = src_theme_configuration["description"]
    if "uri" in src_theme_configuration:
        replacements["Theme URI"] = src_theme_configuration["uri"]
    if "author" in src_theme_configuration:
        replacements["Author"] = src_theme_configuration["author"]
    if "author_uri" in src_theme_configuration:
        replacements["Author URI"] = src_theme_configuration["author_uri"]
    if "tags" in src_theme_configuration:
        replacements["Tags"] = ", ".join(src_theme_configuration["tags"])

    replace_theme_meta_data(file_path, replacements, wp_constants.Expressions.WORDPRESS_REGEX_THEME_METADATA_PARSE)


def replace_theme_meta_data(path: str, replacements: dict, regex_str: str):
    """ Opens the file path and rewrites it replacing matches from the replacements dict
    Args:
        path: The file path to be replaced.
        replacements: The replacements content.
        regex_str: The regex string used to match and replace the replacements' dict.
    """

    replace_file = open(path, 'r', newline='\n')
    file_content = replace_file.read()

    for key, replacement in replacements.items():
        # Build the regex to retrieve data: This regex would match the lines containing [key]:value.
        # For example, in the string Author: Ahead Labs, S.L -> $1 = Author and $2 = Ahead Labs, S.L
        regex = f'({key}){regex_str}'

        # Search with regex
        matches = re.search(regex, file_content)

        if matches is not None and matches.group(1):
            # Build the replacement string
            target = f'{matches.group(1)}: {replacement}'
            # Apply the replacement
            file_content = file_content.replace(matches.group(0), target)

    # Write replaced content to the file
    with open(path, 'w', newline='\n') as scss_file:
        scss_file.write(file_content)


def replace_theme_slug_in_functions_php(file_path: str, src_theme_configuration: dict):
    """ From the theme configuration, creates a replacements dict and replaces the file_path
    Args:
        file_path: The path of the file to be replaced.
        src_theme_configuration: Dict containing src theme configuration.
    """
    theme_slug = src_theme_configuration["source"]
    core_php_file = open(file_path, 'r')
    file_content = core_php_file.read()

    file_content = re.sub(wp_constants.Expressions.WORDPRESS_REGEX_FUNCTIONS_PHP_MYTHEME, theme_slug, file_content)

    # Write replaced content to the file
    with open(file_path, 'w', newline='\n') as core_php_file:
        core_php_file.write(file_content)


def scaffold_basic_theme_structure(
        path: str, site_configuration: dict, structure_file_path: str = None) -> None:
    """ Creates a basic structure of a wordpress development theme based on its default theme-structure.json

        Args:
            path: Full path where the structure will be created
            site_configuration: Site configuration
            structure_file_path: Optional parameter containing the structure file path to be used. If ignored, the
                default structure file will be used.
        """

    # Get src/development theme
    src_theme = get_src_theme(site_configuration["settings"]["themes"])

    # Parse theme structure configuration
    if pathlib.Path(structure_file_path).exists():
        theme_structure = wptools.get_site_configuration(structure_file_path)
        logging.info(literals.get("wp_theme_structure_creating_from_file").format(
            theme_name=src_theme["name"],
            file_name=structure_file_path))
    else:
        token_replacements: dict = {"mytheme": src_theme["name"]}
        theme_structure = \
            wptools.get_default_project_structure(wp_constants.ProjectStructureType.THEME, token_replacements)
        logging.info(literals.get("wp_theme_structure_creating_from_default_file").format(resource="default file"))

    # Set token replacements
    dev_environment = get_environment_by_type(site_configuration, wp_constants.ProjectEnvironmentType.DEVELOPMENT)
    pro_environment = get_environment_by_type(site_configuration, wp_constants.ProjectEnvironmentType.PRODUCTION)
    project_config = site_configuration["settings"]["project"]
    token_replacements: dict = {
        "development-environment-base-url": dev_environment["base_url"],
        "production-environment-url": pro_environment["wp_config"]["site_url"]["value"],
        "project-name": project_config["name"],
        "project-version": project_config["version"],
        "theme-author": src_theme["author"],
        "theme-description": src_theme["description"],
        "theme-minimum-wordpress-version": src_theme["minimum-wordpress-version"],
        "theme-minimum-wordpress-version-tested": src_theme["minimum-wordpress-version-tested"],
        "theme-minimum-php-version": src_theme["minimum-php-version"],
        "theme-name": src_theme["name"],
        "theme-tags": src_theme["tags"],
        "theme-url": src_theme["url"],
        "theme-version": src_theme["version"],
    }
    project_starter = BasicStructureStarter(token_replacements)

    # Change the main folder's name of the theme to the theme_name
    theme_structure["items"][0]["name"] = src_theme["name"]

    # Iterate through every item recursively
    for item in theme_structure["items"]:
        project_starter.add_item(item, path)

    # Purge .gitkeep
    git_tools.purge_gitkeep(pathlib.Path(path).as_posix())

    logging.info(literals.get("wp_created_theme_structure").format(theme_name=src_theme["name"]))


def triage_themes(themes: dict) -> (dict, dict):
    """triages themes to determine which must be installed and activated.

    Args:
        themes: Themes configuration.

    Return:
        Tuple with parent and child theme configuration.
    """
    child = None
    parent = None
    parent_guess: str = ""

    for theme in themes:
        if not theme["activate"]:
            parent_guess = theme["name"]
        if theme["activate"]:
            child = theme
            if "template" in theme:
                parent_guess = theme["template"]

        if not theme["activate"] and not theme["template"] and theme["name"] == parent_guess:
            parent = theme

    return parent, child


if __name__ == "__main__":
    help(__name__)
