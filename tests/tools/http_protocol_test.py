"""Unit tests for the tools/http_protocol module"""

from tests.tools.conftest import mocked_requests_get_ip
from unittest.mock import patch

import devops_toolset as sut


# region get_public_ip_address()


@patch("logging.info")
@patch("requests.get")
def test_get_public_ip_address_returns_ip_address(requests_get_mock, logging_info_mock):
    """Given a public service URL, calls it, parses and returns the IP
    address."""

    # Arrange
    public_service_url: str = "https://myservice.net"
    requests_get_mock.side_effect = mocked_requests_get_ip

    # Act
    result = sut.get_public_ip_address(public_service_url)

    # Assert
    assert result == "1.1.1.1"


@patch("re.search")
@patch("logging.info")
@patch("requests.get")
def test_get_public_ip_address_returns_none(requests_get_mock, logging_info_mock, re_search_mock):
    """Given an invalid public service URL, when no IP address is found,
    returns None."""

    # Arrange
    public_service_url: str = "https://myinvalidservice.net"
    requests_get_mock.side_effect = mocked_requests_get_ip
    re_search_mock.return_value = None

    # Act
    result = sut.get_public_ip_address(public_service_url)

    # Assert
    assert result is None

# endregion
