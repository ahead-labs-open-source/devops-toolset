""" Unit tests core for the script_common_test file """

import pytest
import devops_toolset as sut
from tests.project_types.wordpress.conftest import mocked_requests_get
from unittest.mock import patch, mock_open


# region check_required_files()

@patch("devops_toolset.core.log_tools.log_indented_list")
def test_check_required_files_returns_when_required_files_are_present(log_indented_list_mock, wordpressdata):
    """ Given list of required files, when list does not contain elements, then return without action """
    # Arrange
    required_files_list = []
    root_path = wordpressdata.root_path
    # Act
    sut.check_required_files(required_files_list, root_path, {})
    # Assert
    log_indented_list_mock.assert_not_called()


@patch("devops_toolset.core.log_tools.log_indented_list")
@patch("clint.textui.prompt.yn")
@patch("logging.critical")
def test_check_required_files_raises_value_error_when_not_required_files_and_not_use_defaults(logging_critical_mock,
                                                                                              prompt_yn_mock,
                                                                                              log_indented_list_mock,
                                                                                              wordpressdata):
    """ Given list of required files, when list does not contain elements and user does not want to use defaults, then
    raises a ValueError """
    # Arrange
    required_files_list = wordpressdata.required_files_list_two_files
    prompt_yn_mock.return_value = False
    root_path = wordpressdata.root_path
    # Act
    with pytest.raises(ValueError):
        sut.check_required_files(required_files_list, root_path, {})
        # Assert
        logging_critical_mock.assert_called()


@patch("devops_toolset.core.log_tools.log_indented_list")
@patch("clint.textui.prompt.yn")
@patch("devops_toolset.filesystem.paths.get_file_name_from_url")
@patch("logging.info")
@patch("devops_toolset.filesystem.paths.files_exist_filtered")
def test_check_required_files_downloads_files_when_use_defaults(files_exist_filtered, logging_info_mock,
                                                                get_filename_mock, prompt_yn_mock,
                                                                log_indented_list_mock, wordpressdata, mocks):
    """ Given list of required files, when list does not contain elements and user does not want to use defaults, then
    raises a ValueError """
    # Arrange
    required_files_list = wordpressdata.required_files_list_one_file
    files_exist_filtered.return_value = required_files_list
    required_files_urls = {"*plugin-config.json": "some_url"}
    mocks.requests_get_mock.side_effect = mocked_requests_get
    get_filename_mock.return_value = "some_url"
    prompt_yn_mock.return_value = True
    root_path = wordpressdata.root_path
    # Act
    m = mock_open()
    expected_content = b"sample response in bytes"
    # Act
    with patch(wordpressdata.builtins_open, m, create=True):
        sut.check_required_files(required_files_list, root_path, required_files_urls)
        # Assert
        handler = m()
        handler.write.assert_called_with(expected_content)

# endregion check_required_files()
