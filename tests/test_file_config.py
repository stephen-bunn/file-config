# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import typing

from file_config import _file_config as file_config


def test_is_typing_type():
    for type_name in typing.__all__:
        type_ = getattr(typing, type_name)
        if hasattr(type_, "__module__") and type_.__module__ == "typing":
            assert file_config._is_typing_type(type_)
