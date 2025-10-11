# -*- coding: utf-8 -*-

"""
Core mixins package providing compatibility
utilities and interfaces.
"""

try:
    from enum import StrEnum as _StrEnum

except ImportError:
    from .compatibility import StrEnum as _StrEnum  # type: ignore[assignment]

from .compatibility import Self

# Type alias that works with both standard library
# and the custom HTTPStatus...
StrEnum = _StrEnum

__all__ = [
    "Self",
    "StrEnum",
]
