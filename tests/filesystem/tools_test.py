"""Unit core for the tools file"""

from unittest.mock import patch, mock_open, call

import json
import pathlib
import devops_toolset as sut
import pytest


# region is_file_empty()


@patch("os.path.getsize")
@pytest.mark.parametrize("getsize_result, expected_result", [(0, True), (5, False)])
def test_is_file_empty_given_path_when_empty_then_return_true(getsize_mock, getsize_result, expected_result, paths):
    """Given an empty file return True."""

    # Arrange
    path = paths.test_path
    getsize_mock.return_value = getsize_result
    # Act
    result = sut.is_file_empty(path)

    # Assert
    assert result == expected_result

# endregion is_file_empty()

# region strip_utf8_bom_character_from_file()


@patch("logging.info")
@patch("builtins.open", new_callable=mock_open)
def test_strip_utf8_bom_character_from_file_reads_file(open_file_mock, logging_info_mock):
    """Given a path reads its content"""

    # Arrange
    path: str = "pathto/file"
    calls: list = [
        call(path, "r", encoding="utf-8-sig"),
        call(path, "w", encoding="utf-8")
    ]

    # Act
    sut.strip_utf8_bom_character_from_file(path)

    # Assert
    open_file_mock.assert_has_calls(calls, any_order=True)

# endregion strip_utf8_bom_character_from_file()

# region update_json_file_key_text()


def test_update_json_file_key_text_when_key_path_empty_raises_value_error():
    """Given an empty key_path list, raises a ValueError."""

    # Arrange
    key_path: list = []
    key_value: str = "myValue"
    json_file_path = "pathto/file.json"

    # Act
    with pytest.raises(ValueError) as value_error:
        sut.update_json_file_key_text(key_path, key_value, json_file_path)

        # Assert
        assert str(value_error.value) == sut.literals.get("list_length_zero")


def test_update_json_file_key_text_when_key_path_greater_than_three_raises_value_error():
    """Given a key_path list with more than 3 elements, raises a
    ValueError."""

    # Arrange
    key_path: list = ["key1", "key2", "key3", "key4",]
    key_value: str = "myValue"
    json_file_path = "pathto/file.json"

    # Act
    with pytest.raises(ValueError) as value_error:
        sut.update_json_file_key_text(key_path, key_value, json_file_path)

        # Assert
        assert str(value_error.value) == sut.literals.get("list_length_higher_than").format(length=3)


def test_update_json_file_key_text_when_depth_1_returns_value(filecontents, tmp_path):
    """Given a key_path list with depth 1 returns the key value."""

    # Arrange
    key1: str = "key1"
    key_value: str = filecontents.key_value
    json_file_content: str = filecontents.json_file_depth_1
    json_file_content_dict: dict = json.loads(filecontents.json_file_depth_1)
    json_file_content_dict[key1] = key_value
    json_file_path = pathlib.Path.joinpath(tmp_path, filecontents.json_file_name)
    with open(str(json_file_path), "w") as json_file:
        json_file.write(json_file_content)
    key_path: list = [key1]

    # Act
    sut.update_json_file_key_text(key_path, key_value, str(json_file_path))

    # Assert
    with open(json_file_path, "r") as json_file:
        result: dict = json.loads(json_file.read())
        assert result == json_file_content_dict


def test_update_json_file_key_text_when_depth_2_returns_value(filecontents, tmp_path):
    """Given a key_path list with depth 2 returns the key value."""

    # Arrange
    key1: str = "key1"
    key2: str = "key2"
    key_value: str = filecontents.key_value
    json_file_content: str = filecontents.json_file_depth_2
    json_file_content_dict: dict = json.loads(filecontents.json_file_depth_2)
    json_file_content_dict[key1][key2] = key_value
    json_file_path = pathlib.Path.joinpath(tmp_path, filecontents.json_file_name)
    with open(str(json_file_path), "w") as json_file:
        json_file.write(json_file_content)
    key_path: list = [key1, key2]

    # Act
    sut.update_json_file_key_text(key_path, key_value, str(json_file_path))

    # Assert
    with open(json_file_path, "r") as json_file:
        result: dict = json.loads(json_file.read())
        assert result == json_file_content_dict


def test_update_json_file_key_text_when_depth_3_returns_value(filecontents, tmp_path):
    """Given a key_path list with depth 3 returns the key value."""

    # Arrange
    key1: str = "key1"
    key2: str = "key2"
    key3: str = "key3"
    key_value: str = filecontents.key_value
    json_file_content: str = filecontents.json_file_depth_3
    json_file_content_dict: dict = json.loads(filecontents.json_file_depth_3)
    json_file_content_dict[key1][key2][key3] = key_value
    json_file_path = pathlib.Path.joinpath(tmp_path, filecontents.json_file_name)
    with open(str(json_file_path), "w") as json_file:
        json_file.write(json_file_content)
    key_path: list = [key1, key2, key3]

    # Act
    sut.update_json_file_key_text(key_path, key_value, str(json_file_path))

    # Assert
    with open(json_file_path, "r") as json_file:
        result: dict = json.loads(json_file.read())
        assert result == json_file_content_dict

# endregion update_json_file_key_text()

# region update_xml_file_entity_text()


@patch("xml.etree.ElementTree.parse")
def test_update_xml_file_entity_text_parse_file(parse_mock):
    """Given an XML file path parse its content."""

    # Act
    sut.update_xml_file_entity_text("", "", "file.xml")

    # Assert
    parse_mock.assert_called_once_with("file.xml")


# endregion update_xml_file_entity_text()
