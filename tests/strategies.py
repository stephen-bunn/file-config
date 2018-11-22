# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import math
import enum
import random
import keyword

import attr
from hypothesis import assume
from hypothesis.strategies import (
    one_of,
    from_regex,
    composite,
    builds,
    none,
    integers,
    booleans,
    floats,
    tuples,
    lists,
    sets,
    frozensets,
    characters,
    text,
    binary,
    fractions,
    decimals,
    datetimes,
    dates,
    times,
    timedeltas,
    complex_numbers,
    uuids,
)

import file_config


MIN_ENUM_VALUES = 1
MAX_ENUM_VALUES = 5
MIN_CONFIG_VARS = 1
MAX_CONFIG_VARS = 5


@composite
def builtins(draw, ignore=None):
    return draw(
        one_of(
            none(),
            integers(),
            booleans(),
            floats(),
            builds(tuple),
            builds(list),
            builds(set),
            builds(frozenset),
            characters(),
            text(),
            binary(),
            complex_numbers(),
        )
    )


@composite
def class_name(draw):
    name = draw(from_regex(r"^[a-zA-Z]+[a-zA-Z0-9_]*$")).replace("\n", "")
    assume(name not in keyword.kwlist)
    return name


@composite
def variable_name(draw):
    name = draw(from_regex(r"^[a-z]+[a-zA-Z0-9_]*$")).replace("\n", "")
    assume(name not in keyword.kwlist)
    return name


@composite
def config_var(draw):
    value = draw(builtins())
    return file_config.var(type=type(value), default=value)


@composite
def config_var_dict(draw):
    return {
        draw(variable_name()): draw(config_var())
        for _ in range(
            MIN_CONFIG_VARS, random.randint(MIN_CONFIG_VARS, MAX_CONFIG_VARS) + 1
        )
    }


@composite
def config(draw):
    return file_config.make_config(draw(class_name()), draw(config_var_dict()))


@composite
def enums(draw):
    return enum.Enum(
        draw(class_name()),
        {
            draw(variable_name()): draw(one_of(characters(), integers()))
            for _ in range(
                MIN_ENUM_VALUES, random.randint(MIN_ENUM_VALUES, MAX_ENUM_VALUES) + 1
            )
        },
    )
