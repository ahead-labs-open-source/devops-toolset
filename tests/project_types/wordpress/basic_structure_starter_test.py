""" Unit core for the start_basic_structure_test file """
import os
from unittest.mock import patch, call, mock_open
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.wordpress.Literals import Literals as WordpressLiterals
from tests.project_types.wordpress.conftest import mocked_requests_get
from devops_toolset.project_types.wordpress.basic_structure_starter import BasicStructureStarter

import devops_toolset.filesystem.paths as path_tools
import pathlib
import pytest


literals = LiteralsCore([WordpressLiterals])

# region condition_met()


@pytest.mark.parametrize('item, expected', [
    ({"condition": "foo_value"}, True),
    ({"foo_condition": "when-parent-not-empty"}, True)])
def test_condition_met_should_return_true_when_cond_not_in_item_or_condition_not_when_parent_not_empty(item,
                                                                                                       expected,
                                                                                                       wordpressdata):
    """ Given item and base_path parameters, should return True if "condition" is not
    part of item keys """
    # Arrange
    base_path = wordpressdata.wordpress_path
    # Act
    result = BasicStructureStarter.condition_met(item, base_path)
    # Assert
    assert result == expected


@patch.object(path_tools, "is_empty_dir")
def test_condition_met_given_parameters_should_call_is_empty_dir_result(is_empty_dir_mock, wordpressdata):
    """ Given item and base_path parameters, should call is empty dir method """
    # Arrange
    item = {"condition": "when-parent-not-empty"}
    base_path = wordpressdata.wordpress_path
    base_path_parent = str(pathlib.Path(base_path))
    # Act
    BasicStructureStarter.condition_met(item, base_path)
    # Assert
    is_empty_dir_mock.assert_called_once_with(base_path_parent)

# endregion condition_met()

# region add_item()


@patch.object(BasicStructureStarter, "condition_met", return_value=False)
def test_add_item_given_parameters_should_call_condition_met_when_item_has_children_object(
        condition_met_mock, wordpressdata):
    """ Given an item and base_path should call condition_met when has children inside item """
    # Arrange
    item = {"type": "directory", "name": "foo_directory"}
    base_path = wordpressdata.wordpress_path
    token_replacements = wordpressdata.token_replacements
    with patch.object(path_tools, "is_valid_path", return_value=True):
        # Act
        BasicStructureStarter(token_replacements).add_item(item, base_path)
        # Assert
        condition_met_mock.assert_not_called()


@patch.object(BasicStructureStarter, "condition_met", return_value=False)
def test_add_item_given_parameters_when_child_condition_is_false_and_have_children_then_calls_recursive_add_item(
        condition_met_mock, wordpressdata):
    """ Given an item and base_path should call add-item recursively
     when the item has children inside"""
    # Arrange
    item = {"type": "directory", "name": "foo_directory", "children": [{"name": "foo_file"}]}
    base_path = wordpressdata.wordpress_path
    expected_path_1 = str(pathlib.Path.joinpath(pathlib.Path(base_path), "foo_directory"))
    expected_path_2 = str(pathlib.Path.joinpath(pathlib.Path(expected_path_1), "foo_file"))
    token_replacements = wordpressdata.token_replacements
    with patch.object(path_tools, "is_valid_path", return_value=True) as is_valid_path_mock:
        # Act
        BasicStructureStarter(token_replacements).add_item(item, base_path)
        # Assert
        calls = [call(expected_path_1, True),
                 call(expected_path_2, True)]
        is_valid_path_mock.assert_has_calls(calls, any_order=True)


@patch.object(BasicStructureStarter, "condition_met", return_value=True)
@patch.object(os, "mkdir")
def test_add_item_given_parameters_when_child_condition_and_type_is_directory_should_call_os_mkdir(
        os_mkdir_mock, condition_met_mock, wordpressdata):
    """ Given an item and base_path should call os.mkdir with the destination path
     when the item has type directory """
    # Arrange
    expected_directory = "foo_directory"
    item = {"type": "directory", "name": expected_directory, "children": [{"name": "foo_file"}]}
    base_path = wordpressdata.wordpress_path
    token_replacements = wordpressdata.token_replacements
    expected_final_path = pathlib.Path.joinpath(pathlib.Path(base_path), "foo_directory")
    with patch.object(path_tools, "is_valid_path", return_value=False):
        # Act
        BasicStructureStarter(token_replacements).add_item(item, base_path)
        # Assert
        os_mkdir_mock.assert_called_once_with(expected_final_path)


@patch.object(BasicStructureStarter, "condition_met", return_value=True)
@patch("builtins.open", new_callable=mock_open)
@patch.object(BasicStructureStarter, "get_default_content")
def test_add_item_given_parameters_when_child_condition_and_type_is_file_should_create_empty_file(
        get_default_content_mock, file_mock, condition_met_mock, wordpressdata):
    """ Given an item and base_path should create a file with the destination path
     when the item has type file and no default content is present """
    # Arrange
    expected_file = "foo_file"
    item = {"type": "file", "name": expected_file, "children": [{"name": expected_file}]}
    base_path = wordpressdata.wordpress_path
    token_replacements = wordpressdata.token_replacements
    with patch.object(path_tools, "is_valid_path", return_value=False):
        # Act
        BasicStructureStarter(token_replacements).add_item(item, base_path)
        # Assert
        get_default_content_mock.assert_not_called()


@patch.object(BasicStructureStarter, "condition_met", return_value=True)
@patch.object(BasicStructureStarter, "get_default_content", return_value="")
def test_add_item_given_parameters_when_child_condition_and_type_is_file_should_create_content_file(
        get_default_content_mock, condition_met_mock, wordpressdata):
    """ Given an item and base_path should write default content
     when the item has type file and default content is present """

    # Arrange
    expected_file = "foo_file"
    item = {"type": "file", "name": expected_file,
            "default_content": "foo_content",
            "children": [{"name": expected_file}]}
    base_path = wordpressdata.wordpress_path
    m = mock_open()
    token_replacements = wordpressdata.token_replacements
    with patch(wordpressdata.builtins_open, m, create=True):
        with patch.object(path_tools, "is_valid_path", return_value=False):
            # Act
            BasicStructureStarter(token_replacements).add_item(item, base_path)
            # Assert
            handler = m()
            handler.write.assert_called_once_with("")


# endregion add_item()

# region get_default_content()


@pytest.mark.parametrize("item, expected_value", [
    ({"source": "raw", "name": "raw_name", "value": "some_raw_value"}, "some_raw_value"),
    ({"source": "from_file", "name": "file_name", "value": "file"}, "some_from_file_value"),
    ({"source": "from_url", "name": "url_name", "value": "url_resource"}, "sample text response")])
@patch('builtins.open', new_callable=mock_open, read_data="some_from_file_value")
def test_get_default_content_given_item_when_source_then_return_corresponding_value(
        file_mock, item, expected_value, wordpressdata, mocks):
    """Given item when source has value raw, then return value content"""
    # Arrange
    mocks.requests_get_mock.side_effect = mocked_requests_get
    token_replacements = wordpressdata.token_replacements
    # Act
    result = BasicStructureStarter(token_replacements).get_default_content(item, False)
    # Assert
    assert result == expected_value

# endregion get_default_content()
