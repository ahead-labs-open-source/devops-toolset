"""Unit core for the apache file"""

import devops_toolset as sut
import pytest
from unittest.mock import patch, mock_open


# region main()


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@patch("json.loads")
@patch("json.dump")
@pytest.mark.parametrize("hosted_zone", ["/hostedzone/ABCDEFGHIJKL123456789", None])
def test_main_given_json_path_should_dump_resources(json_dump_mock, json_loads_mock,
                                                    call_subprocess_with_result_mock, hosted_zone):
    """Given json_dump, should generate a dict by calling subprocess and dumping into path"""

    # Arrange
    resource: dict = {"SomeResource": "SomeValue"}
    json_path = "path/to/json"
    json_loads_mock.return_value = resource
    m = mock_open()

    # Act
    with patch("builtins.open", m, create=True):
        sut.main(json_path, hosted_zone)
        # Assert
        json_dump_mock.assert_called_once()


# endregion
