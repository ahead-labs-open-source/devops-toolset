"""Unit core for the apache file"""

import devops_toolset as sut
import os
import pathlib

# region generate_htaccess_file_based_basic_auth_file_for_user()


def test_generate_htaccess_file_based_basic_auth_file_for_user_generates_htaccess_file(tmp_path):
    """Generates an .htaccess file in the specified path"""

    # Arrange
    realm_name: str = "realm"
    passwords_file_path: str = "/path/to/passwords"
    user_name: str = "user1"
    htaccess_path: pathlib.Path = tmp_path
    expected: pathlib.Path = pathlib.Path.joinpath(htaccess_path, ".htaccess")

    # Act
    sut.generate_htaccess_file_based_basic_auth_file_for_user(
        realm_name, passwords_file_path, user_name, str(htaccess_path))

    # Assert
    assert os.path.isfile(expected)

# endregion
