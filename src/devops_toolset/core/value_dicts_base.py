"""Base class for ValueDicts"""

import inspect
from typing import List


class ValueDictsBase(object):
    """Base class for ValueDicts"""

    def __init__(self, value_list: List = None):
        """Plains all values from all the dictionaries passed as a parameter
        plus the ones defined in the instanced class.

        Args:
            value_list: List of class types where values should be found.
        """

        self._all_dictionaries = self.get_dicts()

        if value_list:
            for values in value_list:
                _external = values()
                self._all_dictionaries += _external.get_dicts()

        self.all = {}
        for dictionary in self._all_dictionaries:
            self.all.update(dictionary[1])

    def get(self, key: str) -> str:
        """Gets a literal from a given key.

        Args:
            key: used for getting the value
        """

        return str(self.all[key])

    def get_dicts(self):
        """Gets all dict objects of the class."""

        return inspect.getmembers(self, lambda m: type(m) is dict and len(m) > 0)
