# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

import typing

from hypothesis import given
from hypothesis.strategies import data

import file_config

from . import config, builder, class_name, config_var


@given(config_var())
def test_config_var(var):
    assert not callable(var)
    assert file_config.utils.is_config_var(var)


@given(config())
def test_config(config):
    assert callable(config)
    assert file_config.utils.is_config_type(config)
    assert file_config.utils.is_config(config())


@given(class_name())
def test_make_config(config_name):
    config = file_config.make_config(config_name, {})
    assert file_config.utils.is_config_type(config)
    assert file_config.utils.is_config(config())


@given(config())
def test_to_dict(config):
    dict_ = file_config.to_dict(config())
    assert isinstance(dict_, dict)


@given(config(), data())
def test_from_dict(config, data):
    instance = file_config.from_dict(
        config, data.draw(builder.build_config_dict(config))
    )
    assert file_config.utils.is_config(instance)
