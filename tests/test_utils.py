# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import re
from typing import Union

from hypothesis import given, assume
from hypothesis.strategies import builds, one_of, none, characters, booleans, text

import file_config
from .strategies import builtins


@given(characters())
def test_is_compiled_pattern(string):
    pattern = re.compile(re.escape(string))
    regex = file_config.Regex(pattern)
    assert file_config.utils.is_compiled_pattern(pattern)
    assert not file_config.utils.is_compiled_pattern(regex)


@given(characters())
def test_is_regex_type(string):
    pattern = re.compile(re.escape(string))
    regex = file_config.Regex(pattern)
    assert file_config.utils.is_regex_type(regex)
    assert not file_config.utils.is_regex_type(pattern)


# @given(builds())
# def test_is_union_type(builds):
#     assert file_config.utils.is_union_type(type(builds(Union)))


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


@given(one_of(characters(), text()), builtins())
def test_is_string_type(string, other):
    assume(not isinstance(other, str))
    assert file_config.utils.is_string_type(type(string))
    assert not file_config.utils.is_string_type(type(other))
