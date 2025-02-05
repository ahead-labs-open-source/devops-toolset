""" Unit core for the devops_toolset file """


import pathlib
from unittest.mock import patch, mock_open, call
import devops_toolset as sut
import devops_toolset as constants
from tests.tools.conftest import mocked_requests_get
import os.path


# region get_devops_toolset


@patch("devops_toolset.tools.devops_toolset_utils.ZipFile")
@patch("logging.info")
@patch("os.path.join")
@patch("os.rename")
@patch("os.remove")
@patch("devops_toolset.tools.git.purge_gitkeep")
def test_get_devops_toolset_calls_get_devops_toolset_resource(
        git_mock, remove_mock, rename_mock, path_join_mock, logging_mock, zipfile_mock, paths, mocks):
    """ Given destination path, calls the get request of the devops_toolset_download_resource """
    # Arrange
    destination_path = paths.devops_destination_path
    mocks.requests_get_mock.side_effect = mocked_requests_get
    # Act
    with patch(paths.builtins_open, mock_open()):
        sut.get_devops_toolset(destination_path)
        # Assert
        calls = [call(constants.devops_toolset_download_resource, allow_redirects=True)]
        mocks.requests_get_mock.assert_has_calls(calls, any_order=True)


@patch("devops_toolset.tools.devops_toolset_utils.ZipFile")
@patch("logging.info")
@patch("os.path.join")
@patch("os.rename")
@patch("os.remove")
@patch("devops_toolset.tools.git.purge_gitkeep")
def test_get_devops_toolset_extracts_all_devops_toolset_path_content_into_destination_path(
        git_mock, remove_mock, rename_mock, path_join_mock, logging_mock, zipfile_mock, paths, mocks):
    """ Given destination path, extracts the request content into the destination path """
    # Arrange
    devops_toolset_name = "devops-toolset-master.zip"
    destination_path = paths.devops_destination_path
    mocks.requests_get_mock.side_effect = mocked_requests_get
    zip_file_path = os.path.join(destination_path, devops_toolset_name)
    # Act
    with patch(paths.builtins_open, mock_open()):
        sut.get_devops_toolset(destination_path)
        # Assert
        zipfile_mock.assert_called_once_with(zip_file_path, "r")


@patch("devops_toolset.tools.devops_toolset_utils.ZipFile")
@patch("logging.info")
@patch("os.path.join")
@patch("os.rename")
@patch("os.remove")
@patch("devops_toolset.tools.git.purge_gitkeep")
def test_get_devops_toolset_renames_final_destination_folder(
        git_mock, remove_mock, rename_mock, path_join_mock, logging_mock, zipfile_mock, paths, mocks):
    """ Given destination path, renames the old_destination_folder to the final_destination_folder """
    # Arrange
    destination_path = paths.devops_destination_path
    mocks.requests_get_mock.side_effect = mocked_requests_get
    zip_extension = pathlib.Path(constants.devops_toolset_save_as).suffixes[0]
    destination_file_without_zip_extension = constants.devops_toolset_save_as.replace(zip_extension, '')
    old_folder = os.path.join(destination_path, destination_file_without_zip_extension)
    final_folder = os.path.join(destination_path, constants.devops_toolset_folder)
    # Act
    with patch(paths.builtins_open, mock_open()):
        sut.get_devops_toolset(destination_path)
        # Assert
        rename_mock.assert_called_once_with(old_folder, final_folder)


@patch("devops_toolset.tools.devops_toolset_utils.ZipFile")
@patch("logging.info")
@patch("os.path.join")
@patch("os.rename")
@patch("os.remove")
@patch("devops_toolset.tools.git.purge_gitkeep")
def test_get_devops_toolset_removes_devops_toolset_path_file(
        git_mock, remove_mock, rename_mock, path_join_mock, logging_mock, zipfile_mock, paths, mocks):
    """ Given destination path, removes the devops_toolset_path """
    # Arrange
    destination_path = paths.devops_destination_path
    mocks.requests_get_mock.side_effect = mocked_requests_get
    devops_toolset_path_file = os.path.join(destination_path, constants.devops_toolset_save_as)
    # Act
    with patch(paths.builtins_open, mock_open()):
        sut.get_devops_toolset(destination_path)
        # Assert
        remove_mock.assert_called_once_with(devops_toolset_path_file)


@patch("devops_toolset.tools.devops_toolset_utils.ZipFile")
@patch("logging.info")
@patch("os.path.join")
@patch("os.rename")
@patch("os.remove")
@patch("devops_toolset.tools.git.purge_gitkeep")
def test_get_devops_toolset_calls_purge_gitkeep(
        git_mock, remove_mock, rename_mock, path_join_mock, logging_mock, zipfile_mock, paths, mocks):
    """ Given destination path, calls the tools.git purge gitkeep """
    # Arrange
    destination_path = paths.devops_destination_path
    mocks.requests_get_mock.side_effect = mocked_requests_get
    # Act
    with patch(paths.builtins_open, mock_open()):
        sut.get_devops_toolset(destination_path)
        # Assert
        git_mock.assert_called_once_with(destination_path)

# endregion

# region update_devops_toolset


@patch("devops_toolset.tools.devops_toolset_utils.get_devops_toolset")
@patch("shutil.rmtree")
@patch("logging.warning")
@patch("os.path.exists")
@patch("devops_toolset.tools.devops_toolset_utils.compare_devops_toolset_version")
def test_update_devops_toolset_given_toolset_path_calls_compare_devops_toolset_version(
        compare_mock, path_exist_mock, logging_warn_mock, rmtree_mock, get_devops_mock, paths):
    """ Given toolset_path, then calls compare_devops_toolset_version """
    # Arrange
    toolset_path = paths.toolset_path
    compare_mock.return_value = True
    # Act
    sut.update_devops_toolset(toolset_path)
    # Assert
    compare_mock.assert_called_once_with(toolset_path)


@patch("devops_toolset.tools.devops_toolset_utils.get_devops_toolset")
@patch("shutil.rmtree")
@patch("logging.warning")
@patch("os.path.exists")
@patch("devops_toolset.tools.devops_toolset_utils.compare_devops_toolset_version")
def test_update_devops_toolset_given_toolset_path_when_not_latest_version_then_calls_get_devops_toolset(
        compare_mock, path_exist_mock, logging_warn_mock, rmtree_mock, get_devops_mock, paths):
    """ Given toolset_path, when is not latest version, then calls get_devops_toolset"""
    # Arrange
    toolset_path = paths.toolset_path
    compare_mock.return_value = False
    # Act
    sut.update_devops_toolset(toolset_path)
    # Assert
    get_devops_mock.assert_called_once_with(pathlib.Path(toolset_path).parent)


@patch("devops_toolset.tools.devops_toolset_utils.get_devops_toolset")
@patch("shutil.rmtree")
@patch("logging.warning")
@patch("os.path.exists")
@patch("devops_toolset.tools.devops_toolset_utils.compare_devops_toolset_version")
def test_update_devops_toolset_given_toolset_path_when_not_exist_toolset_path_then_calls_shutil_rmtree(
        compare_mock, path_exist_mock, logging_warn_mock, rmtree_mock, get_devops_mock, paths):
    """ Given toolset_path, when is not latest version and toolset_path not exist, then calls shutil_rmtree"""
    # Arrange
    toolset_path = paths.toolset_path
    compare_mock.return_value = False
    path_exist_mock.return_value = True
    # Act
    sut.update_devops_toolset(toolset_path)
    # Assert
    rmtree_mock.assert_called_once_with(toolset_path)


@patch("devops_toolset.tools.devops_toolset_utils.get_devops_toolset")
@patch("shutil.rmtree")
@patch("logging.warning")
@patch("os.path.exists")
@patch("devops_toolset.tools.devops_toolset_utils.compare_devops_toolset_version")
def test_update_devops_toolset_given_toolset_path_when_exist_toolset_path_then_warns(
        compare_mock, path_exist_mock, logging_warn_mock, rmtree_mock, get_devops_mock, paths):
    """ Given toolset_path, when is not latest version and toolset_path exist, then warns message"""
    # Arrange
    toolset_path = paths.toolset_path
    compare_mock.return_value = False
    path_exist_mock.return_value = False
    expected_message = sut.literals.get("wp_devops_toolset_not_found").format(path=toolset_path)
    # Act
    sut.update_devops_toolset(toolset_path)
    # Assert
    logging_warn_mock.assert_called_once_with(expected_message)


# endregion

# TODO (alberto.carbonell) Implement core for this missing method
# region compare_devops_toolset_version
# endregion

