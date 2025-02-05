"""Parses files for getting information from them"""

import json
import logging
import pathlib
from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.filesystem.Literals import Literals as FileSystemLiterals

app: App = App()
platform_specific = app.load_platform_specific("environment")
literals = LiteralsCore([FileSystemLiterals])


def parse_composer_json_data(add_environment_variables: bool = True, composer_json_path: str = None) -> dict:
    """Reads the composer.json file and returns a dict with its data.

    Properties/objects elements are upper cased, underscored and prepended with
        parent name.

    Args:
        add_environment_variables: If True it adds every element of the dict as
            an environment variable.
        composer_json_path: Path to the composer.json file.
    """

    if composer_json_path is None:
        composer_json_path = pathlib.Path.joinpath(app.settings.root_path, "composer.json")
    else:
        composer_json_path = pathlib.Path(composer_json_path)
    logging.info(literals.get("fs_composer_path_is").format(path=composer_json_path))
    with open(composer_json_path, "r") as composer_file:
        data = json.load(composer_file)

    environment_variables = {
        "PROJECT_NAME": data["name"],
        "PROJECT_VERSION": data["version"]
    }

    if add_environment_variables:
        platform_specific.create_environment_variables(environment_variables)

    return environment_variables


if __name__ == "__main__":
    help(__name__)
