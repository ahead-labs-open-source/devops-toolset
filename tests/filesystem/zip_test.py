"""Unit core for the zip file"""

from unittest.mock import patch
import devops_toolset as sut


# region download_and_unzip_file

@patch("devops_toolset.filesystem.paths.download_file")
@patch("pathlib.Path.joinpath")
@patch("zipfile.ZipFile")
def test_download_and_unzip_file_given_parameters_then_calls_extract_all(zipfile_mock, joinpath_mock,
                                                                        download_file_mock, paths):
    """ Given parameters, then calls zip.extractall """
    # Arrange
    url = paths.url
    destination = paths.current_path
    temp_extraction_path = paths.test_path
    download_file_mock.return_value = paths.file_name, paths.test_path
    joinpath_mock.return_value = temp_extraction_path
    # Act
    sut.download_and_unzip_file(url, destination, False)
    # Assert
    zipfile_mock.assert_called_once_with(paths.test_path, 'r')


@patch("devops_toolset.filesystem.paths.download_file")
@patch("pathlib.Path.joinpath")
@patch("zipfile.ZipFile")
@patch("os.walk")
@patch("shutil.move")
@patch("os.rmdir")
def test_download_and_unzip_file_given_parameters_when_unzip_root_is_present_then_move_files(
        rmdir_mock, move_mock, walk_mock, zipfile_mock, joinpath_mock, download_file_mock, paths):
    """ Given parameters, when unzip_root is present then walk and move files """
    # Arrange
    url = paths.url
    destination = paths.current_path
    temp_extraction_path = paths.test_path
    download_file_mock.return_value = paths.file_name, paths.test_path
    joinpath_mock.return_value = temp_extraction_path
    walk_mock.return_value = [(paths.test_path, paths.directory_path, paths.file_name)]
    # Act
    sut.download_and_unzip_file(url, destination, False, paths.test_path)
    # Assert
    move_mock.assert_called()
    rmdir_mock.assert_called()


@patch("devops_toolset.filesystem.paths.download_file")
@patch("pathlib.Path.joinpath")
@patch("zipfile.ZipFile")
@patch("os.remove")
def test_download_and_unzip_file_given_parameters_when_delete_after_unzip_is_present_then_remove_file_path(
        remove_mock, zipfile_mock, joinpath_mock, download_file_mock, paths):
    """ Given parameters, when delete_after_unzip is present then call os.remove """
    # Arrange
    url = paths.url
    destination = paths.current_path
    temp_extraction_path = paths.test_path
    download_file_mock.return_value = paths.file_name, paths.test_path
    joinpath_mock.return_value = temp_extraction_path
    # Act
    sut.download_and_unzip_file(url, destination, True)
    # Assert
    remove_mock.assert_called_once_with(paths.test_path)


# endregion download_and_unzip_file

# region zip_directory

@patch("os.walk")
@patch("zipfile.ZipFile")
def test_zip_directory_given_paths_walks_filesystem(zipfile_mock, os_walk_mock):
    """Given ZIP file path and text file path (inside ZIP), reads text file."""

    # Arrange
    directory_path = ""
    file_path = ""
    internal_path_prefix = ""

    # Act
    sut.zip_directory(directory_path, file_path, internal_path_prefix)

    # Assert
    os_walk_mock.assert_called_once()

# endregion zip_directory

# region read_text_file_in_zip


@patch("zipfile.ZipFile")
def test_read_text_file_in_zip_given_paths_reads_text_file(zipfile_mock):
    """Given ZIP file path and text file path (inside ZIP), reads text file."""

    # Arrange
    zip_file_path = ""
    text_file_path = ""

    # Act
    sut.read_text_file_in_zip(zip_file_path, text_file_path)

    # Assert
    zipfile_mock.assert_called_once()

# endregion read_text_file_in_zip
