"""Test configuration file for AWS package.

This code is executed once per unit test session.
Add here whatever you want to pass as a fixture in your core.

    ie: (see FileNames example)
        - Add a class that contains what you want to pass as a fixture in your core.
        - Create a fixture with that same lowered name that returns an instance to that class."""


import json
import pytest


class AwsData(object):
    """Class used to create the awsdata fixture"""

    invalid_path = "/notvalidpath"
    file_list = ["file1", "file2", "file3"]
    key_list = ["key1", "key2", "key3"]
    paginator_pages = "[{\"Contents\": [{\"Key\": \"messages.en.xlf\", \"LastModified\": \"\", \"ETag\": \"123456789a\", \"Size\": 1024, \"StorageClass\": \"STANDARD\"}, {\"Key\": \"messages.es.xlf\", \"LastModified\": \"\", \"ETag\": \"123456789b\", \"Size\": 1025, \"StorageClass\": \"STANDARD\"}], \"Name\": \"my-bucket\", \"Prefix\": \"\", \"MaxKeys\": 1000, \"EncodingType\": \"url\", \"KeyCount\": 2}]"
    valid_path = "pathto/foo"


class Paginator(object):
    """Class to mock the AWS S3 paginator object"""

    @staticmethod
    def paginate(**kwargs):
        return json.loads(AwsData.paginator_pages)

@pytest.fixture
def awsdata():
    """Sample data for testing AWS related functionality"""
    return AwsData()


@pytest.fixture
def paginator():
    """Paginator mock"""
    return Paginator()
