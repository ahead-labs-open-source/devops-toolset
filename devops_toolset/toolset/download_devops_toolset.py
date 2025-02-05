"""This script downloads devops-toolset from the GitHub repository (not from
    the feed).

    NOTE:
        This script should only contain pure Python code without any reference
            to the toolset, since it will be called independently."""

import argparse
import logging
import os
import pathlib
import requests
import shutil
import zipfile

logging.basicConfig(level=logging.INFO)
logging.Formatter("%(asctime)s %(levelname)-8s %(module)-15s %(message)s")
logger = logging.getLogger(__name__)


def main(destination_path: str, branch: str):
    """Downloads devops-toolset from the GitHub repository

    Args:
        destination_path: Path where devops-toolset will be downloaded and decompressed.
        branch: What branch to download from the repository.
    """

    toolset_name = "devops-toolset"
    dashed_branch = branch.replace("/", "-")
    internal_directory = f"{toolset_name}-{dashed_branch}"

    # Download the toolset
    destination_path_object, full_destination_path = download_toolset(branch, destination_path, toolset_name)

    # Decompress the toolset
    internal_directory_full_path, temporary_extraction_path = \
        decompress_toolset(destination_path_object, full_destination_path, internal_directory)

    # Delete the temporary files
    cleanup(full_destination_path, internal_directory_full_path, temporary_extraction_path)

    # Delete myself
    os.remove(__file__)


def cleanup(full_destination_path, internal_directory_full_path, temporary_extraction_path):
    """Deletes temporary files

    Args:
        full_destination_path: Path where devops-toolset will be downloaded and decompressed joined to the toolset-name
        internal_directory_full_path: Path where devops-toolset will be extracted joined to
        {toolset_name}-{dashed_branch}
        temporary_extraction_path: Path devops-toolset will be extracted

        """
    os.rmdir(internal_directory_full_path)
    logger.info(f"Deleted directory {internal_directory_full_path}")
    os.rmdir(temporary_extraction_path)
    logger.info(f"Deleted directory {temporary_extraction_path}")
    os.remove(full_destination_path)
    logger.info(f"Deleted file {full_destination_path}")


def decompress_toolset(destination_path_object, full_destination_path, internal_directory):
    """Decompresses devops-toolset

    Args:
        destination_path_object: Path where devops-toolset will be downloaded and decompressed.
        full_destination_path: Path where devops-toolset will be downloaded and decompressed joined to the toolset-name
        internal_directory: {toolset_name}-{dashed_branch}

        """
    temporary_extraction_path = pathlib.Path.joinpath(destination_path_object, "__temp")
    with zipfile.ZipFile(full_destination_path, "r") as zip_file:
        zip_file.extractall(temporary_extraction_path)
    internal_directory_full_path = pathlib.Path.joinpath(temporary_extraction_path, internal_directory)
    items = os.listdir(internal_directory_full_path)
    for item in items:
        from_path = pathlib.Path.joinpath(internal_directory_full_path, item)
        to_path = pathlib.Path.joinpath(destination_path_object, item)
        shutil.move(from_path, to_path)
    logger.info(f"devops-toolset decompressed to {destination_path_object}")
    return internal_directory_full_path, temporary_extraction_path


def download_toolset(branch, destination_path, toolset_name):
    """Downloads devops-toolset from the GitHub repository

        Args:
            toolset_name: The name of the zip downloaded.
            destination_path: Path where devops-toolset will be downloaded and
                decompressed.
            branch: What branch to download from the repository.
        """
    destination_path_object = pathlib.Path(destination_path)
    full_destination_path = pathlib.Path.joinpath(destination_path_object, f"{toolset_name}.zip")
    response = requests.get(f"https://github.com/aheadlabs/devops-toolset/archive/{branch}.zip")
    if not os.path.exists(destination_path):
        os.mkdir(destination_path)
    with open(full_destination_path, "wb") as zip_file:
        zip_file.write(response.content)
    logger.info(f"devops-toolset downloaded to {full_destination_path}")
    return destination_path_object, full_destination_path


def is_valid_path(path: str) -> bool:
    """Checks if a path is valid"""

    if path is None or path.strip() == "":
        return False

    return True


class PathValidator(argparse.Action):
    """Validates a path"""
    def __init__(self, option_strings, dest, **kwargs):
        super(PathValidator, self).__init__(option_strings, dest.replace("-", "_"), **kwargs)

    def __call__(self, parent_parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

        if not is_valid_path(values):
            raise ValueError("The argument {argument} is not valid.".format(argument=self.dest))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination-path", action=PathValidator)
    parser.add_argument("--branch", default="master")
    args, args_unknown = parser.parse_known_args()

    main(args.destination_path, args.branch)
