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
def config_var(draw, allowed_strategies=None):
    if isinstance(allowed_strategies, list):
        value = draw(one_of(allowed_strategies))
    else:
        value = draw(builtins())
    return file_config.var(type=type(value), default=value)


@composite
def config_var_dict(draw, min_vars=None, max_vars=None, allowed_strategies=None):
    if not isinstance(min_vars, int):
        min_vars = MIN_CONFIG_VARS
    if not isinstance(max_vars, int):
        max_vars = MAX_CONFIG_VARS
    return {
        draw(variable_name()): draw(config_var(allowed_strategies=allowed_strategies))
        for _ in range(MIN_CONFIG_VARS, random.randint(min_vars, max_vars) + 1)
    }


@composite
def config(
    draw, config_vars=None, min_vars=None, max_vars=None, allowed_strategies=None
):
    if isinstance(config_vars, dict):
        return file_config.make_config(draw(class_name()), config_vars)
    else:
        return file_config.make_config(
            draw(class_name()),
            draw(
                config_var_dict(
                    min_vars=min_vars,
                    max_vars=max_vars,
                    allowed_strategies=allowed_strategies,
                )
            ),
        )


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
