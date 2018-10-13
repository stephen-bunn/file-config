# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import typing

from hypothesis import given

import file_config

from . import config, config_var, class_name


@given(config_var())
def test_config_var(var):
    assert file_config.utils.is_config_var(var)


@given(config())
def test_config(config):
    assert file_config.utils.is_config_type(config)
    assert file_config.utils.is_config(config())


@given(class_name())
def test_make_config(config_name):
    config = file_config.make_config(config_name, {})
    assert file_config.utils.is_config_type(config)
    assert file_config.utils.is_config(config())


@given(config(max_vars=0))
def test_from_dict(config):
    instance = file_config.from_dict(config, {})
    assert file_config.utils.is_config(instance)


@given(config())
def test_to_dict(config):
    dict_ = file_config.to_dict(config())
    assert isinstance(dict_, dict)

