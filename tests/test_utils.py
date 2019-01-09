# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import re
import math
import typing
import collections

from hypothesis import given, assume, settings
from hypothesis.strategies import (
    builds,
    one_of,
    sampled_from,
    none,
    floats,
    characters,
    booleans,
    integers,
    binary,
    text,
)

import file_config
from .strategies import enums, builtins, config_var, config


@given(config_var(), builtins())
def test_is_config_var(config_var, other):
    assert file_config.utils.is_config_var(config_var)
    assert not file_config.utils.is_config_var(other)


@given(config(), builtins())
def test_is_config_type(config, other):
    assert file_config.utils.is_config_type(config)
    assert not file_config.utils.is_config_type(type(other))


@given(config())
def test_is_config(config):
    assert file_config.utils.is_config(config())


@given(characters())
def test_is_compiled_pattern(string):
    pattern = re.compile(re.escape(string))
    regex = file_config.Regex(pattern)
    assert file_config.utils.is_compiled_pattern(pattern)
    assert not file_config.utils.is_compiled_pattern(regex)


@given(builtins())
def test_is_builtin_type(type_):
    assume(type_ != None)
    assert file_config.utils.is_builtin_type(type(type_))


@settings(deadline=None)
@given(enums(), builtins())
def test_is_enum_type(enum_, other):
    assert file_config.utils.is_enum_type(enum_)
    assert not file_config.utils.is_enum_type(type(other))


def test_is_typing_type():
    for types in file_config.utils.TYPE_MAPPINGS.get("typing", {}).values():
        for type_ in types:
            assert file_config.utils.is_typing_type(type_)


def test_is_collections_type():
    for types in file_config.utils.TYPE_MAPPINGS.get("collections", {}).values():
        for type_ in types:
            assert file_config.utils.is_collections_type(type_)


@given(characters())
def test_is_regex_type(string):
    string = re.escape(string)
    pattern = re.compile(string)
    regex = file_config.Regex(string)
    assert file_config.utils.is_regex_type(regex)
    assert not file_config.utils.is_regex_type(pattern)


@given(builtins(), builtins())
def test_is_union_type(value1, value2):
    # NOTE: typing.Union does fancy conversions of similar types so we need to make
    # sure that we are dealing with a typing type
    union_type = typing.Union[type(value1), type(value2)]
    assume(file_config.utils.is_typing_type(type(union_type)))
    assert file_config.utils.is_union_type(union_type)
    assert not file_config.utils.is_union_type(type(value1))
    assert not file_config.utils.is_union_type(type(value2))


@given(none(), builtins())
def test_is_null_type(none, other):
    assume(other != None)
    assert file_config.utils.is_null_type(type(none))
    assert not file_config.utils.is_null_type(type(other))


@given(booleans(), builtins())
def test_is_bool_type(boolean, other):
    # TODO: assume from _get_types inverse
    assume(not isinstance(other, bool))
    assert file_config.utils.is_bool_type(type(boolean))
    assert not file_config.utils.is_bool_type(type(other))


@given(
    sampled_from(
        file_config.utils._get_types(file_config.utils.Types.STRING)
        + [file_config.Regex(r"^$")]
    ),
    builtins(),
)
def test_is_string_type(string, other):
    # TODO: assume from _get_types inverse
    assume(not isinstance(other, str))
    assert file_config.utils.is_string_type(string)
    assert not file_config.utils.is_string_type(type(other))


@given(integers(), builtins())
def test_is_integer_type(integer, other):
    # TODO: assume from _get_types inverse
    assume(not isinstance(other, int))
    assert file_config.utils.is_integer_type(type(integer))
    assert not file_config.utils.is_integer_type(type(other))


@given(floats(), builtins())
def test_is_number_type(number, other):
    # TODO: assume from _get_types inverse
    assume(not isinstance(other, float))
    assert file_config.utils.is_number_type(type(number))
    assert not file_config.utils.is_number_type(type(other))


@given(
    sampled_from(file_config.utils._get_types(file_config.utils.Types.ARRAY)),
    builtins(),
)
def test_is_array_type(array, other):
    # TODO: assume from _get_types inverse
    assume(not isinstance(other, (list, tuple, set, frozenset)))
    assert file_config.utils.is_array_type(array)
    assert not file_config.utils.is_array_type(other)


@given(
    sampled_from(file_config.utils._get_types(file_config.utils.Types.OBJECT)),
    builtins(),
)
def test_is_object_type(object_, other):
    assume(not isinstance(other, dict))
    assert file_config.utils.is_object_type(object_)
    assert not file_config.utils.is_object_type(type(other))


@given(builtins())
def test_typecast_builtins(value):
    assume(value)
    # FIXME: handle casting some of these types
    # NOTE: the reason we are ignoring bytes here is that it is not base64 encoded bytes
    # this causes a TypeError from binascii for incorrect padding (missing "=" suffix)
    assume(
        not isinstance(value, (list, tuple, set, frozenset, bytes, bytearray, complex))
    )
    # NOTE: can't accept nans for typecasting as nan never equals nan
    if isinstance(value, float):
        assume(not math.isnan(value))

    assert file_config.utils.typecast(type(value), str(value)) == value


@given(characters())
def test_typecast_regex(string):
    regex = file_config.Regex(re.escape(string))
    assert file_config.utils.typecast(regex, string) == string
    assert not file_config.utils.typecast(regex, string) == regex


@given(enums())
def test_typecast_enum(enum):
    item = list(enum.__members__.items())[0][-1]
    assert file_config.utils.typecast(enum, item.value) == item


def test_typecast_collections():
    for (name, types) in file_config.utils.TYPE_MAPPINGS.get("collections", {}).items():
        for type_ in types:
            value = {
                file_config.utils.Types.STRING: "",
                file_config.utils.Types.ARRAY: [],
                file_config.utils.Types.OBJECT: {},
            }[name]
            assert isinstance(file_config.utils.typecast(type_, value), type_)


@given(builtins())
def test_typecast_typings(value):
    assume(value != None)
    # FIXME: handle some of these unhashable builtin types
    # NOTE: the reason we are ignoring bytes here is that it is not base64 encoded bytes
    # this causes a TypeError from binascii for incorrect padding (missing "=" suffix)
    assume(not isinstance(value, (bytes, list, tuple, set, frozenset)))
    for (typing_type, builtin_type) in {
        typing.List: list,
        typing.Tuple: tuple,
        typing.Set: set,
        typing.FrozenSet: frozenset,
    }.items():
        assert isinstance(
            file_config.utils.typecast(typing_type[type(value)], [value]), builtin_type
        )

    for (typing_type, builtin_type) in {
        typing.Dict: dict,
        typing.ChainMap: collections.ChainMap,
    }.items():
        assert isinstance(
            file_config.utils.typecast(
                typing_type[type(value), type(value)], {value: value}
            ),
            builtin_type,
        )


@given(binary())
def test_encode_decode_bytes(value):
    encoded = file_config.utils.encode_bytes(value)
    assert isinstance(encoded, str)
    decoded = file_config.utils.decode_bytes(encoded)
    assert isinstance(decoded, bytes)
    assert decoded == value
