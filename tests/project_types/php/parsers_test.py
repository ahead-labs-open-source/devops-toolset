""" Unit core for the parsers script """
import json
import pathlib
from unittest.mock import patch, mock_open
from tests.project_types.php.conftest import ParsersData

import devops_toolset as sut


# region parse_composer_json_data


@patch("pathlib.Path.joinpath")
@patch("logging.info")
@patch("builtins.open", new_callable=mock_open, read_data=ParsersData.composer_file_data)
def test_parse_composer_json_data_given_path_when_none_then_get_default_composer_json_path(mocked_open,
    logging_mock, joinpath_mock, parsersdata):
    """ Given composer_json_path argument, when None, then should get a default composer json path """
    # Arrange
    joinpath_mock.return_value = pathlib.Path(parsersdata.composer_json_file_path)
    add_environment_variables = False
    # Act
    sut.parse_composer_json_data(add_environment_variables)
    # Assert
    joinpath_mock.assert_called_once()


@patch("logging.info")
@patch("builtins.open", new_callable=mock_open, read_data=ParsersData.composer_file_data)
def test_parse_composer_json_data_given_parameters_when_add_environment_variables_then_call_create_env_variables(
    mocked_open, logging_mock, parsersdata):
    """ Given parameters, when add_environment_variables is true, then call create_environment_variables """
    # Arrange
    add_environment_variables = True
    data = json.loads(ParsersData.composer_file_data)
    expected_env_variables = {
        "PROJECT_NAME": data["name"],
        "PROJECT_VERSION": data["version"]
    }
    # Act
    with patch.object(sut, "platform_specific") as platform_specific_mock:
        with patch.object(platform_specific_mock, "create_environment_variables") as create_env_variables_mock:
            sut.parse_composer_json_data(add_environment_variables, parsersdata.composer_json_file_path)
            # Assert
            create_env_variables_mock.assert_called_once_with(expected_env_variables)

# endregion parse_composer_json_data
