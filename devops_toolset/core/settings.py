"""Loads settings from the settings.json file"""

import pathlib
import os
import json
import pkg_resources


class Settings(object):
    """Application settings"""

    _DEVOPS: str = "devops_platforms"
    _LOCALES: str = "locales"
    _CORE: str = "core"
    _CONFIG_SETTINGS_FILE_NAME: str = "logging-config.json"
    _SETTINGS_FILE_NAME: str = "settings.json"
    _CURRENT_PATH: str = os.path.dirname(os.path.realpath(__file__))

    # defaults
    root_path: pathlib.Path = pathlib.Path(_CURRENT_PATH).parent.absolute()
    project_xml_path = root_path.parent.parent.absolute()
    devops_path: pathlib.Path = pathlib.Path.joinpath(root_path, _DEVOPS).absolute()
    locales_path: pathlib.Path = pathlib.Path.joinpath(root_path, _LOCALES).absolute()
    log_config_file_path: pathlib.Path = pathlib.Path(pkg_resources.resource_filename
                                                      (__name__, _CONFIG_SETTINGS_FILE_NAME))
    settings_path: pathlib.Path = pathlib.Path(pkg_resources.resource_filename(__name__, _SETTINGS_FILE_NAME))
    language: str = "en"
    platform: str = "azuredevops"
    platform_specific_path: pathlib.Path = pathlib.Path.joinpath(devops_path, platform).absolute()

    def __init__(self):
        """Loads settings"""

        self.load(self.settings_path.as_posix())
        self.platform_specific_path = pathlib.Path.joinpath(self.devops_path, self.platform).absolute()

    @staticmethod
    def read_settings_from_file(path: str):
        """Loads settings from settings.json

        Args:
            path: Path to read settings.json from
        """

        with open(path, "r") as settings_file:
            settings = json.load(settings_file)

        return settings

    def load(self, path: str):
        """Assigns settings"""

        settings = self.read_settings_from_file(path)

        # Add your setting mappings here
        self.language = settings["language"]
        self.platform = settings["platform"]
