""" Unit core for the build_wordpress script """

import pytest
import devops_toolset.project_types.wordpress.scripts.build_wordpress as sut

# region main


def test_main_pass():
    """ Should pass when called """

    # Arrange

    # Act
    sut.main()

    # Assert
    assert True

# endregion main
