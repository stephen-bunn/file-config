# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

from __future__ import annotations

import re
from typing import Type, NewType, Pattern, TypeVar, Protocol
from dataclasses import MISSING, Field

from .constants import REGEX_TYPE_NAME

_T = TypeVar("_T")
CONFIG_FIELD_MISSING = MISSING
ConfigField_T = Field


class Config_T(Protocol[_T]):
    ...


def build_regex_type(pattern: str) -> Type[Pattern]:
    """Build a new detectable type for compiled regex patterns.

    Examples:
        >>> build_regex_type(r"foobar")
        <function NewType.<locals>.new_type at 0x100cf90d0>
        >>> @config
            MyConfig:
                name: Regex(r"foobar") = var()

    Args:
        pattern (str):
            The regex pattern to compile.

    Returns:
        Type[Pattern]:
            The new type that can be used to describe the pattern.
    """

    return NewType(REGEX_TYPE_NAME, re.compile(pattern))


# Alias the name `Regex` to constructe a regex type
# Sugary syntax for config var definitions
Regex = build_regex_type
