"""Provides tools for managing the AWS S3 service"""

import boto3
import devops_toolset.filesystem.paths as paths
import logging
import os
import pathlib
import shutil

from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.aws.Literals import Literals as AwsLiterals


app: App = App()
s3 = boto3.client("s3")
literals = LiteralsCore([AwsLiterals])


def get_filtered_objects_from_bucket(bucket_name: str, object_prefix: str, destination_path: str):
    """Downloads filtered objects that match the specified keys and prefix from
    the bucket.

    Args:
        bucket_name: S3 bucket name to get the objects from.Hello world!
        object_prefix: Only the object keys that match this prefix will be
            retrieved.
        destination_path: Path where the objects will be downloaded to.
    """

    if not paths.is_valid_path(destination_path, True):
        raise ValueError()

    if object_prefix is None or object_prefix == "":
        raise ValueError()

    object_list = list_objects_in_bucket(bucket_name, object_prefix)
    key_list = list(map(lambda x: x["Key"], object_list))
    get_objects_from_bucket(bucket_name, key_list, destination_path)


def get_objects_from_bucket(bucket_name: str, keys: list[str], destination_path: str, empty_path: bool = False):
    """Downloads objects that match the specified keys from the bucket.

    Args:
        bucket_name: S3 bucket name to get the objects from.
        keys: Keys of the objects to be downloaded.
        destination_path: Path where the objects will be downloaded to.
        empty_path: If true, deletes destination path content before downloads.
    """

    if not paths.is_valid_path(destination_path, True):
        raise ValueError

    if len(keys) == 0:
        raise ValueError

    destination_path_obj = pathlib.Path(destination_path)

    logging.info(literals.get("s3_downloading_objects_from_s3_bucket").format(
        number=len(keys),
        bucket=bucket_name,
        destination=str(destination_path_obj)
    ))

    if empty_path:
        shutil.rmtree(destination_path_obj)

    for key in keys:
        object_destination_path_obj = pathlib.Path.joinpath(destination_path_obj, key)
        if not object_destination_path_obj.parent.exists():
            os.makedirs(object_destination_path_obj.parent)
        with open(object_destination_path_obj, "wb") as file:
            s3.download_fileobj(bucket_name, key, file)
            logging.info(literals.get("s3_downloaded_object_from_s3_bucket").format(
                name=key,
                bucket=bucket_name,
                destination=str(object_destination_path_obj)
            ))


def list_objects_in_bucket(bucket_name: str, object_prefix: str = "") -> list:
    """Gets all objects that match the criteria from a S3 bucket.

    Args:
        bucket_name: S3 bucket name to get the object list from.
        object_prefix: Only the object keys that match this prefix will be
            retrieved.

    Returns:
        Returns the list of all the objects in the bucket.
    """

    object_list: list = []

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=object_prefix)
    for page in pages:
        object_list.extend(page["Contents"])

    logging.info(literals.get("s3_got_x_objects_from_s3_bucket").format(
        number=len(object_list),
        bucket=bucket_name
    ))

    return object_list


def put_bulk_objects_to_bucket(bucket_name: str, local_path: str, glob: str, destination_key_prefix: str = ""):
    """Uploads multiple objects to the S3 bucket based on a glob expression.

    Args:
        bucket_name: S3 bucket name to upload objects to.
        local_path: Path to the base directories where files are located.
        glob: Glob expression used to select the files to be uploaded.
        destination_key_prefix: Prefix added to every object key.
    """

    if not paths.is_valid_path(local_path, True):
        raise ValueError()

    file_list: list = paths.get_file_paths_in_tree(local_path, glob)

    for file in file_list:
        object_key = f"{destination_key_prefix}{os.path.basename(file)}"
        put_object_to_bucket(bucket_name, str(file), object_key)


def put_object_to_bucket(bucket_name: str, local_path: str, destination_key: str):
    """Uploads an object to the S3 bucket.

    Args:
        bucket_name: S3 bucket name to get the object list from.
        local_path: Path to the file to be uploaded.
        destination_key: Path where the objects will be uploaded to.
    """

    if not paths.is_valid_path(local_path, True):
        raise ValueError()

    with open(local_path, "rb") as file:
        content = file.read()

    s3.put_object(
        Bucket=bucket_name,
        Body=content,
        Key=destination_key
    )

    logging.info(literals.get("s3_uploaded_object_to_s3_bucket").format(
        object_key=destination_key,
        bucket=bucket_name
    ))


if __name__ == "__main__":
    help(__name__)
