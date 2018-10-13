# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import random
import keyword

import attr
from hypothesis.strategies import (
    none,
    text,
    dates,
    times,
    uuids,
    binary,
    builds,
    floats,
    one_of,
    tuples,
    nothing,
    booleans,
    decimals,
    integers,
    composite,
    datetimes,
    fractions,
    iterables,
    characters,
    from_regex,
    timedeltas,
    complex_numbers,
)

import file_config

CONFIG_VAR_MIN_COUNT = 0
CONFIG_VAR_MAX_COUNT = 10


@composite
def random_builtin(draw, ignore: list = []):
    ignore = tuple(ignore)
    return draw(
        one_of(
            none(),
            builds(set),
            text(),
            # dates(),
            builds(list),
            # times(),
            # uuids(),
            # binary(),
            floats(),
            tuples(),
            booleans(),
            # decimals(),
            integers(),
            # datetimes(),
            # fractions(),
            iterables(nothing()),
            characters(),
            builds(frozenset),
            # timedeltas(),
            complex_numbers(),
        ).filter(lambda x: not isinstance(x, ignore))
    )


@composite
def class_name(draw):
    return draw(
        from_regex(r"\A[a-zA-Z_]+[a-zA-Z0-9_]?\Z").filter(
            lambda name: name not in keyword.kwlist
        )
    )


@composite
def attribute_name(draw):
    return draw(
        from_regex(r"\A[a-z]+[a-zA-Z0-9_]?\Z").filter(
            lambda name: name not in keyword.kwlist
        )
    )


@composite
def config_var(draw, var_type=None, var_default=None, **kwargs):
    if not var_type:
        if not var_default:
            var_default = draw(random_builtin())
        var_type = type(var_default)
    return file_config.var(type=var_type, default=var_default, **kwargs)


@composite
def config(
    draw,
    config_name=None,
    config_vars=None,
    min_vars=CONFIG_VAR_MIN_COUNT,
    max_vars=CONFIG_VAR_MAX_COUNT,
):
    if not isinstance(config_vars, dict):
        config_vars = {}
        for _ in range(random.randint(min_vars, max_vars)):
            var_name = draw(attribute_name())
            config_vars[var_name] = draw(config_var())

    if not config_name:
        config_name = draw(class_name())

    return file_config.make_config(config_name, config_vars, repr=False)
