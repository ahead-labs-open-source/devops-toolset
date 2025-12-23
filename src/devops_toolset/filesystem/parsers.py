"""Parses files for getting information from them"""

import json
import logging
import pathlib
import re
import xml.etree.ElementTree as ElementTree
import devops_toolset.project_types.wordpress.constants as wp_constants
from typing import List

from devops_toolset.core.app import App
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.filesystem.literals import Literals as FileSystemLiterals
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals


app: App = App()
platform_specific = app.load_platform_specific("environment")
literals = LiteralsCore([FileSystemLiterals])
wp_literals = LiteralsCore([WordpressLiterals])


def get_xml_file_entity_text(entity_xpath: str, xml_file_path: str) -> dict:
    """Gets the XML entity tag and value that matches the XPath expression.

    Supported XPath syntax is documented here:
    https://docs.python.org/3/library/xml.etree.elementtree.html#supported-xpath-syntax

    Args:
        entity_xpath: Path to the node or attribute to be matched.
        xml_file_path: Path to the XML file.

    Returns:
        Dict with tag and value.
    """
    xml_tree = ElementTree.parse(xml_file_path)
    entity = xml_tree.find(entity_xpath)
    return {entity.tag: entity.text}


def parse_project_xml_data(add_environment_variables: bool = True, project_xml_path: str = None) -> dict:
    """Reads the /project.xml file and returns a dict with its data.

    XML elements are upper cased, underscored and prepended with parent name.

    Args:
        add_environment_variables: If True it adds every element of the dict as
            an environment variable.
        project_xml_path: Path to the project.xml file.
    """

    if project_xml_path is None:
        project_xml_path = pathlib.Path.joinpath(app.settings.project_xml_path, "project.xml")
    else:
        project_xml_path = pathlib.Path(project_xml_path)
    logging.debug(literals.get("fs_project_path_is").format(path=project_xml_path))
    xml = ElementTree.parse(str(project_xml_path)).getroot()

    environment_variables = {}
    for e in xml:
        environment_variables[f"{xml.tag}_{e.tag}".upper()] = e.text

    if add_environment_variables:
        platform_specific.create_environment_variables(environment_variables)

    return environment_variables


def parse_theme_metadata(css_file_content: bytes, tokens: List[str], add_environment_variables: bool = False) -> dict:
    """ Reads a style.css data and returns its metadata as a dict based on the tokens list.
    Args:
        css_file_content: Data content of the style.css file used to retrieve metadata from.
        tokens: List of strings representing parts of the metadata to be retrieved
        add_environment_variables: If True it adds every element of the dict as an environment variable.

    Returns: Metadata content in a dict

    """
    result = dict()
    environment_variables = dict()
    logging.info(wp_literals.get("wp_parsing_theme_metadata"))

    # Convert css binary data to text
    css_str_content = css_file_content.decode("utf-8")

    # For each token in tokens
    for token in tokens:

        # Build the regex to retrieve data
        regex = token + wp_constants.theme_metadata_parse_regex
        logging.debug(wp_literals.get("wp_parsing_theme_regex").format(regex=regex))

        # Search with regex
        matches = re.search(regex, css_str_content)

        if matches is not None and matches.group(1):
            match = matches.group(1)
            logging.info(wp_literals.get("wp_parsing_theme_matches_found").format(
                token=token, content=match))
            result[token] = match

            # If add_environment_variables, then prepare match as an environment variables
            if add_environment_variables:
                environment_variables[f"theme_{token}".upper()] = match

        else:
            logging.warning(wp_literals.get("wp_parsing_theme_no_matches_found").format(token=token))

    # When environment variables present, then create them
    if len(environment_variables) > 0:
        platform_specific.create_environment_variables(environment_variables)

    return result


def parse_json_file(path: str) -> dict:
    """Parses a JSON file as a dict.

    Args:
        path: Path to the JSON file.

    Returns:
        Dictionary with the file contents.
    """

    with open(path, "r") as json_file:
        return json.load(json_file)


if __name__ == "__main__":
    help(__name__)
