""" Creates an opinionated basic structure for a WordPress project. """

import devops_toolset.filesystem.paths as path_tools
import logging
import os
import pathlib
import requests
from devops_toolset.core.app import App
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals
from typing import Union

app: App = App()
literals = LiteralsCore([WordpressLiterals])


class BasicStructureStarter(object):
    """ Set of methods used to create a basic structure for a Wordpress project """

    def add_item(self, item, base_path_str: str) -> None:
        """ Creates the item (file or dir) in the current filesystem

         Args:
                item: the object containing the type and the value of the content.
                base_path_str: the path which from the structure will be built

        """

        # Set paths
        base_path = pathlib.Path(base_path_str)
        final_path = pathlib.Path.joinpath(base_path, item["name"])
        has_condition = "condition" in item
        if has_condition:
            child_condition = self.condition_met(item, base_path_str)
        else:
            child_condition = True

        # Only if the item DOES NOT exist and condition is met
        if not os.path.exists(final_path) and child_condition and "type" in item:
            # Create item
            if item["type"] == "directory":
                os.mkdir(final_path)
                logging.debug(literals.get("wp_directory_created").format(directory=final_path))
            elif item["type"] == "file":
                with open(final_path, "w", newline="\n") as new_file:
                    if "default_content" in item:
                        default_content = self.get_default_content(item["default_content"], False)
                        new_file.write(default_content)
                    logging.debug(literals.get("wp_file_created").format(file=final_path))
            elif item["type"] == "bfile" and "default_content" in item:
                default_content = self.get_default_content(item["default_content"], True)
                with open(final_path, "wb") as new_file:
                    new_file.write(default_content)
                    logging.debug(literals.get("wp_file_created").format(file=final_path))

        # Iterate through children if any
        if "children" in item:
            for child in item["children"]:
                self.add_item(child, final_path)

    @staticmethod
    def condition_met(item, base_path: str) -> bool:
        """ Returns the result (True of False) of the condition contained on the item

        Args:
            item: the item inspected for conditions
            base_path: parent dir to check
        """

        if "condition" in item and item["condition"] == "when-parent-not-empty":
            return path_tools.is_empty_dir(str(pathlib.Path(base_path)))
        # Default behaviour
        return True

    @staticmethod
    def get_default_content(item, is_binary: bool = False) -> Union[str, bytes]:
        """ Gets the default content of the files based on the json item passed

            Args:
                item : the object containing the type and the value of the default content
                is_binary: if True returns content as bytes, otherwise as str

            Returns:
                Content in text or binary format
        """
        if item["source"] == "raw":
            logging.debug(literals.get("wp_write_default_content").format(
                file="",
                source=f"raw data => {item['source']}"
            ))
            return item["value"]
        elif item["source"] == "from_file":
            with open(item["value"], "r") as default_content_file:
                logging.debug(literals.get("wp_write_default_content").format(
                    file="",
                    source=f"file => {item['source']}"
                ))
                return default_content_file.read()
        elif item["source"] == "from_url":
            logging.debug(literals.get("wp_write_default_content").format(
                file="",
                source=f"URL => {item['source']}"
            ))
            response = requests.get(item["value"])
            return response.content if is_binary else response.text
