# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import re
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


# @given(config())
# def test_is_config(config):
#     assert file_config.utils.is_config(config)


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


# @given()
# def test_is_typing_type(type_):
#     pass


# @given()
# def test_is_collections_type(type_):
#     pass


@given(characters())
def test_is_regex_type(string):
    pattern = re.compile(re.escape(string))
    regex = file_config.Regex(pattern)
    assert file_config.utils.is_regex_type(regex)
    assert not file_config.utils.is_regex_type(pattern)


@given(builtins(), builtins())
def test_is_union_type(value1, value2):
    # NOTE: typing.Union does fancy conversions of similar types so we need to make
    # sure that we are dealing with a typing type
    assume(typing.Union[type(value1), type(value2)].__module__ == "typing")
    assert file_config.utils.is_union_type(typing.Union[type(value1), type(value2)])


@given(none(), builtins())
def test_is_null_type(none, other):
    assume(other != None)
    assert file_config.utils.is_null_type(type(none))
    assert not file_config.utils.is_null_type(type(other))


@given(booleans(), builtins())
def test_is_bool_type(boolean, other):
    assume(not isinstance(other, bool))
    assert file_config.utils.is_bool_type(type(boolean))
    assert not file_config.utils.is_bool_type(type(other))


@given(sampled_from([str]), builtins())
def test_is_string_type(string, other):
    assume(not isinstance(other, str))
    assert file_config.utils.is_string_type(string)
    assert not file_config.utils.is_string_type(type(other))


@given(integers(), builtins())
def test_is_integer_type(integer, other):
    assume(not isinstance(other, int))
    assert file_config.utils.is_integer_type(type(integer))
    assert not file_config.utils.is_integer_type(type(other))


@given(floats(), builtins())
def test_is_number_type(number, other):
    assume(not isinstance(other, float))
    assert file_config.utils.is_number_type(type(number))
    assert not file_config.utils.is_number_type(type(other))


# TODO: sample typing types
@given(sampled_from([list, tuple, set, frozenset]), builtins())
def test_is_array_type(array, other):
    assume(not isinstance(other, (list, tuple, set, frozenset)))
    assert file_config.utils.is_array_type(array)
    assert not file_config.utils.is_array_type(other)


# TODO: sample typing types
@given(sampled_from([dict]), builtins())
def test_is_object_type(object_, other):
    assume(not isinstance(other, dict))
    assert file_config.utils.is_object_type(object_)
    assert not file_config.utils.is_object_type(type(other))


@settings(deadline=None)
@given(enums(), builtins())
def test_is_enum_type(enum_, other):
    assert file_config.utils.is_enum_type(enum_)
    assert not file_config.utils.is_enum_type(type(other))


# @given()
# def test_typecast():
#     pass
