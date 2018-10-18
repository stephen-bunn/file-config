# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import re
import typing
import collections

import attr
from hypothesis import given
from hypothesis.strategies import characters, one_of, from_type

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
