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
def config_var(draw):
    var_default = draw(random_builtin())
    return file_config.var(type=type(var_default), default=var_default)


@composite
def config(draw):
    config_vars = {}
    for _ in range(random.randint(1, 5)):
        var_name = draw(
            from_regex(r"\A[a-z]+[a-zA-Z0-9_]?\Z").filter(
                lambda name: name not in keyword.kwlist
            )
        )
        config_vars[var_name] = draw(config_var())
    config_name = draw(
        from_regex(r"\A[a-zA-Z_]+[a-zA-Z0-9_]?\Z").filter(
            lambda name: name not in keyword.kwlist
        )
    )
    return file_config.make_config(config_name, config_vars, repr=False)
