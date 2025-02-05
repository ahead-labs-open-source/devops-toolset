"""Contains paths-related operations."""

import logging
import os
import pathlib
import requests
import shutil
from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.filesystem.Literals import Literals as FileSystemLiterals
from devops_toolset.filesystem.constants import Directions, FileNames, FileType
from typing import List, Tuple, Union
from urllib.parse import urlparse

app: App = App()
platform_specific = app.load_platform_specific("environment")
literals = LiteralsCore([FileSystemLiterals])


# noinspection PyTypeChecker
def download_file(url: str, destination: str, save_as: str = None, headers: dict = None,
                  file_type: FileType = FileType.BINARY) -> tuple:
    """Downloads a file from a URL.

    Args:
        url: Where to download the file from.
        destination: Path to the directory where the file will be downloaded.
        save_as: File name to save the downloaded file as.
        headers: Authentication headers.
        file_type: The type of the file. Defaults to BINARY.

    Returns:
        Tuple with (file name, file path)
    """

    if not os.path.isdir(destination):
        raise ValueError(literals.get("fs_not_dir"))

    destination_path = pathlib.Path(destination)
    file_name = save_as if save_as else get_file_name_from_url(url)
    full_destination_path = pathlib.Path.joinpath(destination_path, file_name)

    response = requests.get(url, headers=headers) if headers else requests.get(url)

    file_mode: str = f"w{file_type.value}"
    with open(full_destination_path, file_mode) as file:
        file.write(response.content)

    return file_name, full_destination_path


def files_exist(path: str, file_names: List[str]) -> List[Tuple[str, bool]]:
    """Determines if every file path in the list exists in the specified path.

    Args:
        path: Path where files will be checked.
        file_names: List of file names to be checked.

    Returns:
         List of tuples where each element contains the path evaluated (glob if
         not found) and a boolean value: True if path exists; False if it
         doesn't.
    """

    result = []

    for file_name in file_names:
        files = sorted(pathlib.Path(path).rglob(file_name))
        if len(files) == 0:
            result.append((file_name, False))
        elif len(files) > 1:
            for file in files:
                result.append((file, True))
        else:
            result.append((files[0], True))

    return result


def files_exist_filtered(path: str, filter_by: bool, file_names: List[str]) -> List[str]:
    """Returns a filtered list, only with values that meet the condition.

    Args:
        path: Path where files will be checked.
        filter_by: Returns the value[0] that meets the criteria on value[1].
        file_names: List of file names to be checked.

    Returns:
        List of strings that meet the filter.
    """

    unfiltered_list = files_exist(path, file_names)

    filtered_list = []
    for value in unfiltered_list:
        if filter_by == value[1]:
            filtered_list.append(value[0])

    return filtered_list


def get_file_name_from_url(url: str) -> str:
    """Returns the file name from a URL.

    Args:
        url: URL to be parsed.

    Returns:
        File name.
    """

    parsed = urlparse(url)
    return os.path.basename(parsed.path)


def get_file_path_from_pattern(path: str, pattern: str, recursive: bool = False) -> Union[str, None]:
    """Gets the file path from a file name pattern.

    Args:
        path: Where to look for.
        pattern: glob pattern of the file name to be found.
        recursive: If True the search will be recursive.

    Returns:
        None if no file or more than one is found, path to file if one found.
    """

    if recursive:
        files = sorted(pathlib.Path(path).rglob(pattern))
    else:
        files = sorted(pathlib.Path(path).glob(pattern))

    if len(files) == 0 or len(files) > 1:
        return None
    else:
        return str(files[0])


def get_file_path_from_pattern_multiple_paths(paths: list, pattern: str, recursive: bool = False) \
        -> Union[List[str], str, None]:
    """Gets the file path from a file name pattern using a list of base paths.

    Args:
        paths: Where to look for.
        pattern: glob pattern of the file name to be found.
        recursive: If True the search will be recursive.

    Returns:
        None if no file or more than one is found, path to file if one found.
    """
    for path in paths:
        file_path = get_file_path_from_pattern(path, pattern, recursive)
        if file_path is not None:
            return file_path

    return None


def get_file_paths_in_tree(starting_path: str, glob: str) -> List[pathlib.Path]:
    """Gets a list with the paths to the descendant files that match the glob pattern.

    Args:
        starting_path: Path to start the seek from.
        glob: glob pattern to match the files that should be found.

    Returns:
        List with the paths to the files that match.
    """

    paths = []

    for guess_path in pathlib.Path(starting_path).rglob(glob):
        paths.append(guess_path)

    return paths


def get_filepath_in_tree(
        base_path: pathlib.Path, seed: str, direction: Directions = Directions.ASCENDING) -> pathlib.PurePath:
    """Gets path to the directory containing the file.

    Args:
        base_path: Path where the search starts from.
        seed: File or directory name (not path to file) that should be found.
        direction: The direction of the seek (ascending by default).

    Returns:
        Path to the directory or None if path not found.
    """

    current_path = base_path
    path_to_file = None

    if direction == Directions.ASCENDING:
        for i in range(len(current_path.parents)):
            guess_path = pathlib.Path.joinpath(current_path.parents[i], seed)
            if pathlib.Path(guess_path).exists():
                path_to_file = pathlib.Path(guess_path).parent
                break
    else:
        for guess_path in current_path.parent.rglob(seed):
            if pathlib.Path(guess_path).exists():
                path_to_file = pathlib.Path(guess_path).parent
                break
            else:
                path_to_file = None

    return path_to_file


def get_project_root(base_path: pathlib.Path, seed: str = FileNames.PROJECT_FILE) -> str:
    """Gets the project root directory path.

    Args:
        base_path: Path where the search starts from.
        seed: What file or directory to look for.

    Returns:
        Path to the project root directory or None if path not found."""

    return str(get_filepath_in_tree(base_path, seed))


def is_empty_dir(path: str = None) -> bool:
    """Checks if the current path is an empty directory

       Args:
           path: Path string to be analyzed

       Returns:
           True if path is an empty directory
       """

    path_object = pathlib.Path(path)
    files_inside_path = filter(lambda x: pathlib.Path.is_dir(pathlib.Path(x)) is False, os.listdir(path_object))
    try:
        min(files_inside_path)
    except ValueError:
        return True
    return False


def is_valid_path(path: Union[str, None] = None, check_existence: bool = False) -> bool:
    """Checks if it is a valid path.

    Args:
        path: Path string to be analyzed.
        check_existence: If True, it checks that the path exists.

    Returns:
        True if path is valid an exists.
    """

    if path is None or path.strip() == "":
        logging.info(literals.get("fs_file_path_not_valid"))
        return False

    if check_existence and not os.path.exists(path):
        logging.info(literals.get("fs_file_path_does_not_exist").format(path=path))
        return False

    return True


def move_files(origin: str, destination: str, glob: str, recursive: bool = False):
    """Moves one or more files from one path to another.

    Args:
        origin: Path where files and directories should be found.
        destination: Path where files and directories will be moved.
        glob: Files to be matched to be moved.
        recursive: If True files are searched recursively
    """

    destination_directory_path = pathlib.Path(destination)

    if recursive:
        # Convert file list to a list
        files = [*pathlib.Path(origin).rglob(glob)]
    else:
        # Keep file list in a generator
        files = pathlib.Path(origin).glob(glob)

    # Iterate through files to move them
    for origin_file_path in files:
        # Get paths related to the file
        origin_directory_path: str = pathlib.Path(os.path.commonprefix([origin, origin_file_path])).as_posix()
        relative_path: str = origin_file_path.as_posix().removeprefix(origin_directory_path).lstrip("/")
        destination_file_path: str = pathlib.Path.joinpath(destination_directory_path, relative_path).as_posix()

        # Move file
        logging.info(literals.get("fs_file_moving").format(
            origin_file_path=origin_file_path,
            destination_file_path=destination_file_path
        ))
        shutil.move(origin_file_path, destination_file_path)


if __name__ == "__main__":
    help(__name__)
