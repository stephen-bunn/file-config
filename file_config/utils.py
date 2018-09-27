# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import attr

from .constants import CONFIG_KEY


def is_config_var(var):
    return (
        isinstance(var, attr._make.Attribute)
        and hasattr(var, "metadata")
        and CONFIG_KEY in var.metadata
    )


def is_config_type(type_):
    return (
        isinstance(type_, type)
        and hasattr(type_, "__attrs_attrs__")
        and hasattr(type_, CONFIG_KEY)
    )


def is_typing_type(type_):
    return isinstance(type_, type) and getattr(type_, "__module__", None) == "typing"
