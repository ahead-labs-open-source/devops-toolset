"""Unit core for the paths file"""

import devops_toolset as sut
import os
import pathlib
import pytest
from tests.conftest import FileNames as FileNameFixtures
from tests.filesystem.conftest import Paths
from devops_toolset import Directions, FileNames
from unittest.mock import patch

# region files_exist()


def test_files_exist_given_empty_list_returns_empty_list(paths):
    """Given an empty list, returns an empty list"""

    # Arrange
    path = paths.directory_path
    file_names = []

    # Act
    result = sut.files_exist(path, file_names)

    # Assert
    assert result == []


@patch("pathlib.Path.rglob")
@pytest.mark.parametrize("rglob_response, expected", [
    ([], [("file1.txt", False), ("file2.txt", False)]),
    (["file1.txt"], [("file1.txt", True), ("file1.txt", True)]),
    (["file1.txt", "file1.txt"], [("file1.txt", True), ("file1.txt", True), ("file1.txt", True), ("file1.txt", True)])
])
def test_files_exist_given_list_returns_list_tuple(rglob_mock, rglob_response, expected, paths):
    """Given a list, returns a list of tuples with boolean values"""

    # Arrange
    path = paths.directory_path
    file_names = ["file1.txt", "file2.txt"]
    rglob_mock.return_value = rglob_response

    # Act
    result = sut.files_exist(path, file_names)

    # Assert
    assert result == expected

# endregion

# region files_exist_filtered()


@patch("devops_toolset.filesystem.paths.files_exist")
@pytest.mark.parametrize("filter_by, expected", [(True, ["file1.txt"]), (False, ["file2.txt"])])
def test_files_exist_filtered(files_exist, filter_by, expected, paths):
    """Given, when, then"""

    # Arrange
    path = paths.directory_path
    file_names = []
    file_list_tuple = [("file1.txt", True), ("file2.txt", False)]
    files_exist.return_value = file_list_tuple

    # Act
    result = sut.files_exist_filtered(path, filter_by, file_names)

    # Assert
    assert result == expected


# endregion

# region get_file_name_from_url()


def test_get_file_name_from_url_given_url_returns_file_name(paths):
    """Given a URL, returns the file name"""

    # Arrange
    url = paths.url

    # Act
    result = sut.get_file_name_from_url(url)

    # Assert
    assert result == paths.file_name

# endregion

# region get_file_path_from_pattern()


@patch("pathlib.Path.rglob")
@pytest.mark.parametrize("rglob_response, expected", [
    (Paths.rglob_result_0, None),
    (Paths.rglob_result_1, "/pathto/file1.json"),
    (Paths.rglob_result_many, None)
])
def test_get_file_path_from_pattern_recursive(rglob_mock, rglob_response, expected, paths):
    """Given a pattern, then returns None if result has more than one results,
    and the full path if one is found, recursively"""

    # Arrange
    path = paths.directory_path
    pattern = paths.file_pattern
    rglob_mock.return_value = rglob_response

    # Act
    result = sut.get_file_path_from_pattern(path, pattern, True)

    # Assert
    assert result == expected


@patch("pathlib.Path.glob")
@pytest.mark.parametrize("glob_response, expected", [
    (Paths.rglob_result_0, None),
    (Paths.rglob_result_1, "/pathto/file1.json"),
    (Paths.rglob_result_many, None)
])
def test_get_file_path_from_pattern_no_recursive(glob_mock, glob_response, expected, paths):
    """Given a pattern, then returns None if result has more than one results,
    and the full path if one is found, non recursively"""

    # Arrange
    path = paths.directory_path
    pattern = paths.file_pattern
    glob_mock.return_value = glob_response

    # Act
    result = sut.get_file_path_from_pattern(path, pattern)

    # Assert
    assert result == expected

# endregion

# region get_file_paths_in_tree()


def test_get_filepaths_in_tree_given_starting_path_glob_when_no_paths_then_returns_empty_list(filenames):
    """Given a starting path and a glob, when there are no matching paths, it
    returns an empty list."""

    # Arrange
    with patch.object(pathlib.Path, "rglob") as rglob:
        rglob.return_value = filenames.no_paths

    # Act
        result = sut.get_file_paths_in_tree(filenames.path, filenames.glob_no_match)

    # Assert
    assert result == []


def test_get_filepaths_in_tree_given_starting_path_glob_when_paths_then_returns_list(filenames):
    """Given a starting path and a glob, when there are matching paths, it
    returns a list with those paths."""

    # Arrange
    with patch.object(pathlib.Path, "rglob") as rglob:
        rglob.return_value = filenames.paths

    # Act
        result = sut.get_file_paths_in_tree(filenames.path, filenames.glob_no_match)

    # Assert
    assert result == filenames.paths

# endregion

# region get_filepath_in_tree() ASCENDING


def test_get_filepath_in_tree_ascending_given_file_name_when_exists_then_returns_path(filenames):
    """Given a file, when it exists in a child directory, should return its
    path"""

    # Arrange
    base_path = pathlib.Path(filenames.deep_path)
    seed = filenames.file

    with patch.object(pathlib.Path, "exists") as exits:
        exits.return_value = True
        with patch(filenames.file__path, f"{base_path}/{seed}"):

            # Act
            result = sut.get_filepath_in_tree(base_path, seed)

    # Assert
    assert result.as_posix() == filenames.deep_path_segment


def test_get_filepath_in_tree_ascending_given_file_name_when_not_exist_then_returns_none(filenames):
    """Given a file, when does not exist in a parent directory, should return
    None"""

    # Arrange
    base_path = pathlib.Path(filenames.deep_path)
    seed = filenames.file

    with patch.object(pathlib.Path, "exists") as exits:
        exits.return_value = False
        with patch(filenames.file__path, f"{filenames.path}/{filenames.test_file}"):

            # Act
            result = sut.get_filepath_in_tree(base_path, seed)

    # Assert
    assert result is None

# endregion

# region get_filepath_in_tree() DESCENDING


def test_get_filepath_descending_in_tree_given_file_name_when_exists_then_returns_path(filenames):
    """Given a file, when it exists in a child directory, should return its
    path"""

    # Arrange
    base_path = pathlib.Path(filenames.deep_path)
    seed = filenames.file

    with patch.object(pathlib.Path, "exists") as exists:
        exists.return_value = True
        with patch.object(pathlib.Path, "rglob") as rglob:
            rglob.return_value = filenames.paths
            with patch(filenames.file__path, f"{filenames.deep_path}/{filenames.test_file}"):

                # Act
                result = sut.get_filepath_in_tree(base_path, seed, Directions.DESCENDING)

    # Assert
    assert result.as_posix() == filenames.path


@pytest.mark.parametrize("rglob_return, path", [
    (FileNameFixtures.paths, FileNameFixtures.deep_path), (FileNameFixtures.no_paths, FileNameFixtures.path)])
def test_get_filepath_descending_in_tree_given_file_name_when_not_exist_but_paths_then_returns_path(
        rglob_return, path, filenames):
    """Given a file, when it does not exist in a child directory but paths are
    returned, should return None"""

    # Arrange
    base_path = pathlib.Path(filenames.deep_path)
    seed = filenames.file

    with patch.object(pathlib.Path, "exists") as exists:
        exists.return_value = False
        with patch.object(pathlib.Path, "rglob") as rglob:
            rglob.return_value = rglob_return
            with patch(filenames.file__path, f"{path}/{filenames.test_file}"):

                # Act
                result = sut.get_filepath_in_tree(base_path, seed, Directions.DESCENDING)

    # Assert
    assert result is None


# endregion

# region get_project_root()


def test_get_project_root_then_calls_get_file_path_in_tree_with_project_file(filenames):
    """Then calls get_filepath_in_tree() with project file as a parameter"""

    # Arrange
    base_path = pathlib.Path(filenames.deep_path)
    seed = FileNames.PROJECT_FILE

    with patch.object(sut, "get_filepath_in_tree") as target:

        # Act
        sut.get_project_root(base_path, seed)

        # Assert
        target.assert_called_with(base_path, seed)

# endregion

# region is_empty_dir()


def test_is_empty_dir(paths):
    """Given a directory path, when it is empty, returns True"""

    # Arrange

    # Act

    # Assert
    assert True

# endregion

# region is_valid_path()


def test_is_valid_path_given_test_path_returns_true(paths):
    """Given a test path, returns true"""

    # Arrange
    path = paths.test_path

    # Act
    result = sut.is_valid_path(path)

    # Assert
    assert result


@patch("logging.info")
def test_is_valid_path_given_non_existent_path_returns_false(logging_info_mock, paths):
    """Given a non existent path, returns false"""

    # Arrange
    path = paths.non_existent_path

    # Act
    result = sut.is_valid_path(path, True)

    # Assert
    assert not result


@patch("logging.info")
def test_is_valid_path_given_invalid_path_returns_false(logging_info_mock):
    """Given None as path, raises ValueError"""

    # Arrange

    # Act
    result = sut.is_valid_path(None)

    # Assert
    assert result is False

# endregion

# region move_files()


@patch("pathlib.Path.rglob")
def test_move_files_if_recursive_use_rglob(rglob_mock, tmp_path, paths):
    """If the glob is recursive, create a list of files to be iterated and use
    rglob()"""

    # Arrange
    origin_path: str = str(pathlib.Path.joinpath(tmp_path, "origin"))
    destination_path: str = str(pathlib.Path.joinpath(tmp_path, "destination"))
    glob: str = paths.glob
    recursive: bool = True

    # Act
    sut.move_files(origin_path, destination_path, glob, recursive)

    # Assert
    rglob_mock.assert_called_once_with(glob)


@patch("pathlib.Path.glob")
def test_move_files_if_recursive_use_glob(glob_mock, tmp_path, paths):
    """If the glob is not recursive, create a generator of files to be
    iterated and use glob()"""

    # Arrange
    origin_path: str = str(pathlib.Path.joinpath(tmp_path, "origin"))
    destination_path: str = str(pathlib.Path.joinpath(tmp_path, "destination"))
    glob: str = "*.txt"
    recursive: bool = False

    # Act
    sut.move_files(origin_path, destination_path, glob, recursive)

    # Assert
    glob_mock.assert_called_once_with(glob)


@patch("shutil.move")
@patch("logging.info")
def test_move_files_moves_n_files(info_mock, shutil_mock, tmp_path, paths):
    """Given a list of paths, shutil.move must be called exactly that number
    of times"""

    # Arrange
    origin_path: str = str(pathlib.Path.joinpath(tmp_path, "origin"))
    destination_path: str = str(pathlib.Path.joinpath(tmp_path, "destination"))
    glob: str = "*.txt"
    recursive: bool = False

    os.makedirs(origin_path)
    os.makedirs(destination_path)
    with open(os.path.join(origin_path, "test_file.txt"), "w") as test_file:
        test_file.write("test")

    # Act
    sut.move_files(origin_path, destination_path, glob, recursive)

    # Assert
    shutil_mock.assert_called_once()

# endregion
