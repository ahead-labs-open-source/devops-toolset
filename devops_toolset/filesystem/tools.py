"""Tools for editing files"""

import json
import logging
import os
import pathlib
import re
import xml.etree.ElementTree as ElementTree
from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.filesystem.Literals import Literals as FileSystemLiterals
from devops_toolset.project_types.wordpress.Literals import Literals as WordpressLiterals
from re import Match
from typing import Union


app: App = App()
platform_specific = app.load_platform_specific("environment")
literals = LiteralsCore([FileSystemLiterals])
wp_literals = LiteralsCore([WordpressLiterals])


def is_file_empty(path: str) -> bool:
    """Checks if a file is empty.

    Args:
        path: Path to the file to be checked.

    Returns:
        True if file is empty.
    """

    return os.path.getsize(path) == 0


def strip_utf8_bom_character_from_file(path: str):
    """Removes byte-order-mark character from the beginning of the UTF8 file"""

    logging.info(literals.get("fs_strip_bom").format(path=path))

    with open(path, "r", encoding="utf-8-sig") as file:
        content = file.read()
        logging.info(literals.get("fs_file_content").format(content=content))

        with open(path, "w", encoding="utf-8") as file_w:
            logging.info(literals.get("fs_writing_file").format(path=path))
            file_w.write(content)


def update_json_file_key_text(key_path: list, key_value: str, json_file_path: str):
    """Updates a JSON file with the given value.

    Args:
        key_path: Path to the key to be updated. Each element of the list is a
            level in the nested key structure.
        key_value: CValue to be set.
        json_file_path: Path to the JSON file.
    """

    if len(key_path) == 0:
        raise ValueError(literals.get("list_length_zero"))

    if len(key_path) > 3:
        raise ValueError(literals.get("list_length_higher_than").format(length=3))

    content: dict = {}
    json_file_path_obj: pathlib.Path = pathlib.Path(json_file_path)

    with open(json_file_path_obj, "r") as json_file:
        content = json.load(json_file)

    if len(key_path) == 1:
        content[key_path[0]] = key_value

    if len(key_path) == 2:
        content[key_path[0]][key_path[1]] = key_value

    if len(key_path) == 3:
        content[key_path[0]][key_path[1]][key_path[2]] = key_value

    with open(json_file_path_obj, "w") as json_file:
        json.dump(content, json_file)

    # TODO(ivan.sainz) Refactor this code using reduce()


def update_xml_file_entity_text(entity_xpath: str, entity_value: str, xml_file_path: str):
    """Updates an XML file with the given value.

    Supported XPath syntax is documented here:
    https://docs.python.org/3/library/xml.etree.elementtree.html#supported-xpath-syntax

    Args:
        entity_xpath: Path to the node or attribute to be updated.
        entity_value: Value to be set.
        xml_file_path: Path to the XML file.
    """

    xml_tree = ElementTree.parse(xml_file_path)
    entity = xml_tree.find(entity_xpath)
    entity.text = entity_value
    xml_tree.write(xml_file_path)


def search_regex_in_text_file(regex: str, file_path: str) -> tuple[bool, Union[Match[str], None]]:
    """Searches a regular expression inside a text file.

    Args:
        regex: Regex to be searched in the text file.
        file_path: Path to the file.

    Returns:
        True if the regex is found inside the text file and match.
    """

    with open(file_path, "r") as file:
        match = re.search(regex, file.read())

        if match is None:
            return False, None
        else:
            return True, match


if __name__ == "__main__":
    help(__name__)
