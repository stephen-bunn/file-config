# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

from hypothesis import assume
from hypothesis.strategies import (
    one_of,
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
