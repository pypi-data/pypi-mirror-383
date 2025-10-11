# -*- coding: utf-8 -*-

"""
Compatibility utilities for Python
version differences.
"""

from enum import Enum

try:
    from typing import Self

except ImportError:
    from typing_extensions import Self  # type: ignore[assignment]


class StrEnum(str, Enum):
    """
    For backward compatibility because StrEnum class
    was added in Python 3.11...
    """

    def __new__(cls, value, *args, **kwargs):
        if not isinstance(value, str):
            raise TypeError(f"{value} is not a string")

        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj
