""" Unit tests for the project_types/aws/s3.py module"""

import devops_toolset.project_types.aws.s3 as sut
import json
import pytest

from datetime import date
from unittest.mock import patch


# region get_filtered_objects_from_bucket

def test_get_filtered_objects_from_bucket_given_invalid_path_raises_valuerror(awsdata):
    """Given an invalid path raises a ValueError."""

    # Arrange
    bucket_name = "my-bucket"
    object_prefix = ""
    destination_path = awsdata.invalid_path

    # Act
    with pytest.raises(ValueError):
        # Assert
        sut.get_filtered_objects_from_bucket(bucket_name, object_prefix, destination_path)


@patch("devops_toolset.filesystem.paths.is_valid_path")
def test_get_filtered_objects_from_bucket_given_invalid_prefix_raises_valuerror(is_valid_path_mock, awsdata):
    """Given an invalid prefix raises a ValueError."""

    # Arrange
    bucket_name = "my-bucket"
    object_prefix = ""
    destination_path = awsdata.valid_path
    is_valid_path_mock.return_value = True

    # Act
    with pytest.raises(ValueError):
        # Assert
        sut.get_filtered_objects_from_bucket(bucket_name, object_prefix, destination_path)


@patch("devops_toolset.filesystem.paths.is_valid_path")
def test_get_filtered_objects_from_bucket_given_bucket_name_gets_objects(is_valid_path_mock, awsdata):
    """Given a bucket name gets the objects from the bucket."""

    # Arrange
    bucket_name = "my-bucket"
    object_prefix = "filename"
    destination_path = awsdata.valid_path
    is_valid_path_mock.return_value = True
    paginator_pages = json.loads(awsdata.paginator_pages)

    # Act
    with patch.object(sut, "list_objects_in_bucket") as list_objects_in_bucket_mock:
        list_objects_in_bucket_mock.return_value = paginator_pages[0]["Contents"]
        with patch.object(sut, "get_objects_from_bucket") as get_objects_from_bucket_mock:
            sut.get_filtered_objects_from_bucket(bucket_name, object_prefix, destination_path)

    # Assert
    get_objects_from_bucket_mock.assert_called_once()

# endregion


# region get_objects_from_bucket

@patch("os.makedirs")
def test_get_objects_from_bucket_given_invalid_path_raises_valuerror(makedirs_mock):
    """Given an invalid path raises a ValueError."""

    # Arrange
    bucket_name = "my-bucket"
    keys = []
    destination_path = "/notvalidpath"

    # Act
    with pytest.raises(ValueError):
        # Assert
        sut.get_objects_from_bucket(bucket_name, keys, destination_path)


@patch("os.makedirs")
@patch("devops_toolset.filesystem.paths.is_valid_path")
def test_get_objects_from_bucket_given_invalid_keys_raises_valuerror(is_valid_path_mock, makedirs_mock, awsdata):
    """Given invalid keys raises a ValueError."""

    # Arrange
    bucket_name = "my-bucket"
    keys = []
    destination_path = awsdata.valid_path
    is_valid_path_mock.return_value = True

    # Act
    with pytest.raises(ValueError):
        # Assert
        sut.get_objects_from_bucket(bucket_name, keys, destination_path)


@patch("os.makedirs")
@patch("devops_toolset.filesystem.paths.is_valid_path")
@patch("logging.info")
@patch("builtins.open")
def test_get_objects_from_bucket_given_bucket_name_gets_objects(
        mock_open, logging_info_mock, makedirs_mock, is_valid_path_mock, awsdata):
    """Given a valid bucket_name downloads objects from the bucket."""

    # Arrange
    bucket_name = "my-bucket"
    keys = awsdata.key_list
    destination_path = awsdata.valid_path
    is_valid_path_mock.return_value = True

    # Act
    with patch.object(sut, "s3") as s3_mock:
        with patch.object(s3_mock, "download_fileobj") as download_fileobj_mock:
            sut.get_objects_from_bucket(bucket_name, keys, destination_path)

    # Assert
    assert download_fileobj_mock.call_count == len(keys)

# endregion


# region list_objects_in_bucket

@patch("logging.info")
def test_list_objects_in_bucket_returns_list(log_info_mock, paginator, awsdata):
    """Given a bucket name, returns a list of objects"""

    # Arrange
    bucket_name: str = "my-bucket"
    expected_result = json.loads(awsdata.paginator_pages)[0]["Contents"]

    # Act
    with patch.object(sut, "s3") as s3_mock:
        with patch.object(s3_mock, "get_paginator") as get_paginator_mock:
            get_paginator_mock.return_value = paginator
            result = sut.list_objects_in_bucket(bucket_name)

    # Assert
    assert result == expected_result

# endregion


# region put_bulk_objects_to_bucket

@patch("devops_toolset.filesystem.paths.is_valid_path")
def test_put_bulk_objects_to_bucket_given_invalid_path_raises_valuerror(is_valid_path_mock, awsdata):
    """Given an invalid path raises a ValueError."""

    # Arrange
    bucket_name = "my-bucket"
    local_path = awsdata.invalid_path
    glob = "*"
    destination_key_prefix = f"{date.today().strftime('%Y.%m.%d')}-"
    is_valid_path_mock.return_value = False

    # Act
    with pytest.raises(ValueError):
        # Assert
        sut.put_bulk_objects_to_bucket(bucket_name, local_path, glob, destination_key_prefix)


@patch("devops_toolset.filesystem.paths.get_file_paths_in_tree")
@patch("devops_toolset.filesystem.paths.is_valid_path")
def test_put_bulk_objects_to_bucket(is_valid_path_mock, get_file_paths_in_tree_mock, awsdata):
    """Given valid parameters, puts every object to the bucket."""

    # Arrange
    bucket_name = "my-bucket"
    local_path = awsdata.invalid_path
    glob = "*"
    destination_key_prefix = f"{date.today().strftime('%Y.%m.%d')}-"
    is_valid_path_mock.return_value = True
    get_file_paths_in_tree_mock.return_value = awsdata.file_list

    # Act
    with patch.object(sut, "put_object_to_bucket") as put_object_to_bucket_mock:
        sut.put_bulk_objects_to_bucket(bucket_name, local_path, glob, destination_key_prefix)

    # Assert
    assert put_object_to_bucket_mock.call_count == len(awsdata.file_list)

# endregion


# region put_object_to_bucket

@patch("builtins.open")
@patch("devops_toolset.filesystem.paths.is_valid_path")
@patch("logging.info")
def test_put_object_to_bucket_given_bucket_puts_object(logging_info_mock, is_valid_path_mock, mock_open, awsdata):
    """Given a bucket name uploads the object."""

    # Arrange
    bucket_name = "my-bucket"
    local_path = ""
    destination_key = awsdata.valid_path
    is_valid_path_mock.return_value = True

    # Act
    with patch.object(sut, "s3") as s3_mock:
        with patch.object(s3_mock, "put_object") as put_object_mock:
            sut.put_object_to_bucket(bucket_name, local_path, destination_key)

    # Assert
    put_object_mock.assert_called()


def test_put_object_to_bucket_given_invalid_path_raises_valuerror(awsdata):
    """Given an invalid local path raises a ValueError."""

    # Arrange
    bucket_name = "my-bucket"
    local_path = ""
    destination_key = awsdata.valid_path

    # Act
    with pytest.raises(ValueError):
        # Assert
        sut.put_object_to_bucket(bucket_name, local_path, destination_key)

# endregion
