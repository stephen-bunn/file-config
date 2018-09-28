# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import typing
import collections

import six
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


def is_config(config_instance):
    return isinstance(config_instance, object) and is_config_type(type(config_instance))


def is_builtin_type(type_):
    return isinstance(type_, type) and type_ in (
        str,
        int,
        float,
        complex,
        list,
        tuple,
        bytes,
        bytearray,
        set,
        frozenset,
        dict,
    )


def is_typing_type(type_):
    return isinstance(type_, type) and getattr(type_, "__module__", None) == "typing"


def is_collections_type(type_):
    return (
        isinstance(type_, type) and getattr(type_, "__module__", None) == "collections"
    )


def is_string_type(type_):
    if is_builtin_type(type_):
        return type_ in (str,)
    elif is_typing_type(type_):
        return type_.__origin__ in (typing.Text, typing.AnyStr)
    elif is_collections_type(type_):
        return type_ in (collections.UserString,)
    return False


def is_number_type(type_):
    if is_builtin_type(type_):
        return type_ in (int, float, complex)
    return False


def is_array_type(type_):
    if is_builtin_type(type_):
        return type_ in (list, tuple, set, frozenset)
    elif is_typing_type(type_):
        return type_.__origin__ in (
            typing.List,
            typing.Tuple,
            typing.Set,
            typing.FrozenSet,
        )
    elif is_collections_type(type_):
        return type_ in (collections.deque, collections.UserList)
    return False


def is_object_type(type_):
    if is_builtin_type(type_):
        return type_ in (dict,)
    elif is_typing_type(type_):
        return type_.__origin__ in (typing.Dict,)
    elif is_collections_type(type_):
        return type_ in (
            collections.ChainMap,
            collections.Counter,
            collections.OrderedDict,
            collections.defaultdict,
            collections.UserDict,
        )
    return False
