""" Unit tests for the project_types/aws/cloudfront.py module"""

import devops_toolset as sut
from unittest.mock import patch


@patch("logging.info")
def test_create_invalidation_creates_invalidation(log_info_mock):
    """Given a distribution id, creates a new invalidation"""

    # Arrange
    distribution_id: str = "A123BCDEF45G6H"

    # Act
    with patch.object(sut, "cloudfront") as cloudfront_mock:
        with patch.object(cloudfront_mock, "create_invalidation") as create_invalidation_mock:
            sut.create_invalidation(distribution_id)

        # Assert
        create_invalidation_mock.assert_called_once()
