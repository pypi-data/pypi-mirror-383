# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from secrets import choice
from string import ascii_letters
from string import digits
from string import punctuation
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional


def random_string(
    vocabulary: Optional[str] = None,
    length: int = 20,
    exclude: Optional[str] = None,
) -> str:
    """Create random string"""

    if not vocabulary:
        vocabulary = ascii_letters + digits + punctuation

    choices_: List[str] = []
    while len(choices_) < length:
        char = choice(vocabulary)
        if not exclude or (exclude and char not in exclude):
            choices_.append(char)

    return "".join(choices_)


def get_batches(list_: List, n: int) -> Iterator:
    """
    Divide a list into chunks...

    :param list_: List to divide.
    :param n: Number of elements by chunk.
    :return:
    """

    for i in range(0, len(list_), n):
        yield list_[i : i + n]


def remove_attributes(record: Dict, attrs: List[str]) -> None:
    """Remove attributes from a Dict"""

    for key in attrs:
        if key in record:
            del record[key]


def rename_attributes(record: Dict, mapper: Dict[str, str]) -> None:
    """Rename the object attributes using the column_mapper"""

    _items = list(record.items())
    for key, value in _items:
        if key in mapper:
            record[mapper[key]] = value
            del record[key]


def add_attributes(record: Dict, expected_attrs: List[str]):
    """
    The function add to the dictionary the list of
    attributes (if not exists) expected
    using None...

    :param record: Dictionary to update.
    :param expected_attrs: Attributes to add.
    :return:
    """

    for key in expected_attrs:
        if key not in record:
            record[key] = None


def convert_data_type(
    data: Dict[str, str],
    columns_type_mapper: Dict[str, Any],
) -> None:
    """
    Update (cast) the value depending on the specified type...

    :param data: Dictionary to update.
    :param columns_type_mapper: Dictionary that specify the data types.
    """

    if not columns_type_mapper:
        return

    # Safe type mapping
    type_converters = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
    }

    for key, type_name in columns_type_mapper.items():
        if key in data and data[key] is not None:
            if type_name not in type_converters:
                raise ValueError(f"Unsupported type: {type_name}")

            value = data[key].strip() if type_name == "float" else data[key]
            try:
                converter = type_converters[type_name]
                data[key] = converter(value)

            except Exception as e:
                raise e.__class__(f"Cannot convert {value} to {type_name}: {e}") from e


def to_snake_case(string: str) -> str:
    """It converts a string from camel-case to snake-case"""

    return "".join(["_" + i.lower() if i.isupper() else i for i in string]).lstrip("_")


def flatten_json(data: Dict, flatten_sublist: bool = False):
    """
    Utility function for flattening dictionary objects...

    :param data: Object to flatten.
    :param flatten_sublist: Set as True if you want to flatten sublist objects.

    :return: Flatten data (dictionary).
    """

    res = {}

    def flatten(x, name: str = ""):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + "_")

        elif flatten_sublist and isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1

        else:
            res[name[:-1]] = x

    flatten(data)
    return res


def to_one_line(multiline_string: str) -> str:
    """It converts a multiline string to a single line one"""

    return re.sub(
        pattern=r"\s+", repl=" ", string=multiline_string.replace("\n", " ")
    ).strip()


def bytes_to_str(data: List | Dict | bytes, encoding: str = "utf-8"):
    """
    Convert bytes to str in keys and values...

    Example:
        {b"key": b"value"})         -> {"key": "value"}
        {b"key": [1, 2, b"3"]}      -> {"key": [1, 2, "3"]}
        [1, 2, b"3", {b"a": b"a"}]  -> [1, 2, "3", {"a": "a"}]
        b"test")                    -> "test"
    """

    def convert(obj_, encoding_, result=None):
        if not result:
            result = {}

        if isinstance(obj_, dict):
            dic_ = {}
            for key in obj_:
                previous_key = key
                if isinstance(key, bytes):
                    key = key.decode()

                dic_[key] = convert(obj_[previous_key], encoding_, dic_)

            return dic_

        if isinstance(obj_, list):
            return [convert(x, encoding_, result or {}) for x in obj_]

        return obj_.decode() if isinstance(obj_, bytes) else obj_

    return convert(data, encoding)
