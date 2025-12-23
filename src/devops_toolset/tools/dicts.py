"""Tools for working with dict objects"""

import re


def filter_keys(key_list: dict, regex: str) -> list:
    """Filters keys in a dictionary

    Args:
        key_list: dict object that contains the keys to be filtered.
        regex: Regular expression used to filter the keys.

    Returns:
        list with the filtered keys.
    """

    filtered_keys = filter(lambda x: re.search(regex, x) is not None, key_list)
    return list(filtered_keys)


def replace_string_in_dict(subject: dict, search: str, replace: str) -> dict:
    """ Replaces search value for replace value inside value objects of subject
    Args:
        :param subject: Dict object which is the target of replacements
        :param search: The string to be searched in order to be replaced
        :param replace: The string to replace the search's occurrences

    Returns
        Dict object with values replaced
    """
    for key, value in subject.items():
        if isinstance(value, dict):
            subject[key] = replace_string_in_dict(value, search, replace)
        if isinstance(value, list):
            index = 0
            for item in value:
                item = replace_string_in_dict(item, search, replace)
                value[index] = item
                index = index + 1
        if isinstance(value, str) and search in value:
            subject[key] = value.replace(search, replace)
    return subject


if __name__ == "__main__":
    help(__name__)
