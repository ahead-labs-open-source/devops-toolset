"""Bootstraps everything

Args:
    --skip-i18n: If present it will skip loading gettext
"""

import importlib.util
import pathlib
from devops_toolset.core.settings import Settings
import devops_toolset.i18n.loader
import devops_toolset.core.log_setup


class App(object):
    """App object that contains core settings and functionalities."""

    # Initialize settings
    settings: Settings = Settings()

    def __init__(self, skip_i18n: bool = False):
        """
        Args:
            skip_i18n: If True it does not load the gettext engine
        """

        # Load gettext
        if not skip_i18n:
            devops_toolset.i18n.loader.setup(self.settings)

        # Configure logging
        devops_toolset.core.log_setup.configure(self.settings.log_config_file_path)

    def load_platform_specific(self, name: str):
        module_path = pathlib.Path.joinpath(self.settings.platform_specific_path, f"{name}.py")
        spec = importlib.util.spec_from_file_location(name, module_path)
        platform_specific = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(platform_specific)
        return platform_specific


if __name__ == "__main__":
    help(__name__)
