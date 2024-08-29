import typing
import re


class Bus:
    def __init__(self):
        self._items = {}

    @staticmethod
    def _check_if_array_and_return_groups(name: str):
        regex = r'^([a-zA-Z0-9\-_]*)\[([a-zA-Z0-9\-_]*)\]$'
        matches = re.findall(regex, name, re.MULTILINE | re.IGNORECASE | re.UNICODE)

        for match in matches:
            if len(match) == 2:
                return match

    def register(self, name: str, item: typing.Any):

        arr_data = self._check_if_array_and_return_groups(name)
        if arr_data:
            if arr_data[0] not in self._items:
                self._items[arr_data[0]] = {}
            self._items[arr_data[0]][arr_data[1]] = item
        else:
            self._items[name] = item

    def __getitem__(self, key):
        if key in self._items:
            return self._items[key]

    def __getattr__(self, key):
        if key in self._items:
            return self._items[key]




