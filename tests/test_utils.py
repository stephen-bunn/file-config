# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import attr
from hypothesis import given

import file_config

from . import config_var


@given(config_var())
def test_is_config_var(var):
    assert file_config.utils.is_config_var(var)
    assert not file_config.utils.is_config_var(attr.ib())
