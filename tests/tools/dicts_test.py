"""Unit core for the dicts file"""
import json

import devops_toolset.tools.dicts as sut


# region filter_keys()


def test_filter_keys():
    """Given a dictionary and a regular expression, then return a list with
    the filtered keys."""
    # Arrange
    key_list = {"key_1": "value_1", "key_2": "value_2"}
    regex = "2"
    expected_result = ["key_2"]

    # Act
    result = sut.filter_keys(key_list, regex)

    # Assert
    assert result == expected_result


# endregion

# region replace_string_in_dict()

def test_replace_string_in_dict_returns_dict_when_no_items():
    """ Given subject, when no items, then return original subject """
    # Arrange
    subject = json.loads("{}")
    # Act
    result = sut.replace_string_in_dict(subject, "search", "replace")
    # Assert
    assert result == subject


def test_replace_string_in_dict_returns_value_replaced_when_value_is_string():
    """ Given subject, when item's value is dict, then replace string and return subject """
    # Arrange
    subject = json.loads("{\"key\":\"value_to_replace\"}")
    target_subject = json.loads("{\"key\":\"value_replaced\"}")
    # Act
    result = sut.replace_string_in_dict(subject, "value_to_replace", "value_replaced")
    # Assert
    assert result["key"] == target_subject["key"]


def test_replace_string_in_dict_calls_recursive_when_value_is_dict():
    """ Given subject, when item's value is dict, then calls recursively """
    # Arrange
    subject = json.loads("{\"key\":{\"inside_key\":\"value_to_replace\"}}")
    target_subject = json.loads("{\"key\":{\"inside_key\":\"value_replaced\"}}")
    # Act
    result = sut.replace_string_in_dict(subject, "value_to_replace", "value_replaced")
    # Assert
    assert result["key"] == target_subject["key"]


# endregion replace_string_in_dict()
