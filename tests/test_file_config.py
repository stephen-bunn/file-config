# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import typing

from hypothesis import given

import file_config

from . import config, config_var


@given(config_var())
def test_config_var(var):
    assert file_config.utils.is_config_var(var)


@given(config())
def test_config(config):
    assert file_config.utils.is_config_type(config)
