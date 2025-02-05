"""Unit core for the core.app file"""

from unittest.mock import patch
from devops_toolset.core import App


# region App()

@patch("devops_toolset.core.log_setup.configure")
@patch("devops_toolset.i18n.loader.setup")
def test_app_given_no_parameters_loads_gettext_engine(i18n_loader_setup, log_setup_configure):
    """Given no parameters, gettext engine must be loaded"""

    # Arrange
    skip_i18n = False

    # Act
    App(skip_i18n)

    # Assert
    i18n_loader_setup.assert_called()


@patch("devops_toolset.core.log_setup.configure")
@patch("devops_toolset.i18n.loader.setup")
def test_app_given_skip_i18n_parameter_does_not_load_gettext_engine(i18n_loader_setup, log_setup_configure):
    """Given the --skip-i18n parameter, gettext engine must not be loaded"""

    # Arrange
    skip_i18n = True

    # Act
    App(skip_i18n)

    # Assert
    i18n_loader_setup.assert_not_called()


# endregion
