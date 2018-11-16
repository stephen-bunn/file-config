# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

import re
import enum
import typing
import collections

import attr
from hypothesis import given
from hypothesis.strategies import one_of, from_type, characters

import file_config

from . import config, config_var


@given(config_var())
def test_is_config_var(var):
    assert file_config.utils.is_config_var(var)
    assert not file_config.utils.is_config_var(attr.ib())


@given(config())
def test_is_config(config):
    assert file_config.utils.is_config(config())
    assert not file_config.utils.is_config(attr.s())


@given(config())
def test_is_config_type(config):
    assert file_config.utils.is_config_type(config)
    assert not file_config.utils.is_config_type(attr.s)


@given(characters())
def test_is_compiled_pattern(string):
    assert not file_config.utils.is_compiled_pattern(string)
    assert file_config.utils.is_compiled_pattern(re.compile(re.escape(string)))


@given(characters())
def test_is_regex_type(string):
    assert file_config.utils.is_regex_type(file_config.Regex(re.escape(string)))


def test_is_enum_type():
    class TestEnum(enum.Enum):
        A = 0
        B = 1

    assert file_config.utils.is_enum_type(TestEnum)
    assert not file_config.utils.is_enum_type(TestEnum.A)
