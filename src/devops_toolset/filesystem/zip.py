"""Supports al compression / decompression operations in the file system."""

from devops_toolset.core.app import App
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.filesystem.literals import Literals as FileSystemLiterals
import devops_toolset.filesystem.constants as constants
import devops_toolset.filesystem.paths
import logging
import os
import pathlib
import shutil
import zipfile

app: App = App()
literals = LiteralsCore([FileSystemLiterals])


def download_and_unzip_file(url: str, destination: str, delete_after_unzip: bool = True, unzip_root: str = None):
    """Downloads and unzips a file from a URL.

    Args:
        url: Where to download the file from.
        destination: Where to download and unzip the file.
        delete_after_unzip: If True it deletes the file after unzipping it.
        unzip_root: Determines which directory inside the zip file is the root
            directory.
    """

    file_name, file_path = devops_toolset.filesystem.paths.download_file(url, destination, constants.FileType.BINARY)
    destination_path = pathlib.Path(destination)
    temp_extraction_path = pathlib.Path.joinpath(destination_path, constants.FileNames.TEMP_DIRECTORY)

    with zipfile.ZipFile(file_path, "r") as zip_file:
        zip_file.extractall(temp_extraction_path)

    if unzip_root is not None:
        temp_rooted_extraction_path = pathlib.Path.joinpath(temp_extraction_path, unzip_root)
        for path, directories, files in os.walk(temp_rooted_extraction_path):
            path_object = pathlib.Path(path)
            for file in files:
                shutil.move(str(pathlib.Path.joinpath(path_object, file)), destination)
            for directory in directories:
                shutil.move(str(pathlib.Path.joinpath(path_object, directory)), destination)
        os.rmdir(temp_rooted_extraction_path)
        os.rmdir(temp_extraction_path)

    if delete_after_unzip:
        os.remove(file_path)


def zip_directory(directory_path: str, file_path, internal_path_prefix: str = ""):
    """Creates a ZIP file of the contents of the specified directory path.

    Args:
        directory_path: Path to the directory to be zipped (directory will not
            be included in the ZIP file).
        file_path: Path to the file to be created.
        internal_path_prefix: Prefix to be added to all the internal paths.
            Must end with /

    Returns:
        Path to the created ZIP file.
    """
    with zipfile.ZipFile(file_path, "w") as output_file:
        for directory, subfolders, files in os.walk(directory_path):
            for file in files:
                current_path = pathlib.Path.joinpath(pathlib.Path(directory), file)
                zip_internal_basepath = pathlib.Path(directory.replace(directory_path, "")).as_posix()
                zip_internal_path = f"{internal_path_prefix}{zip_internal_basepath}/{file}"
                output_file.write(current_path, zip_internal_path)
                logging.debug(literals.get("fs_zip_added_file").format(
                    zip_file_name=os.path.basename(file_path),
                    added_file=zip_internal_path
                ))


def read_text_file_in_zip(zip_file_path: str, text_file_path: str) -> bytes:
    """Reads a text file that is enclosed inside a ZIP file.

    Args:
        zip_file_path: Path to the ZIP file.
        text_file_path: Path to the text file inside the ZIP file.

    Returns:
        Content of the text file
    """
    with zipfile.ZipFile(zip_file_path, "r") as zip_file:
        return zip_file.read(text_file_path)


if __name__ == "__main__":
    help(__name__)
