# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import re
import typing
import collections

import six
import attr

from .constants import CONFIG_KEY


COMPILED_PATTERN_TYPE = type(re.compile(""))


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


def is_compiled_pattern(compiled_pattern):
    return isinstance(compiled_pattern, COMPILED_PATTERN_TYPE)


def is_builtin_type(type_):
    return isinstance(type_, type) and type_ in (
        bool,
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


def is_regex_type(type_):
    return (
        callable(type_)
        and hasattr(type_, "__supertype__")
        and is_compiled_pattern(type_.__supertype__)
    )


def is_null_type(type_):
    if type_ in (type(None),):
        return True
    return False


def is_bool_type(type_):
    if is_builtin_type(type_):
        return type_ in (bool,)
    return False


def is_string_type(type_):
    if is_builtin_type(type_):
        return type_ in (str,)
    elif is_typing_type(type_):
        return type_.__origin__ in (typing.Text, typing.AnyStr)
    elif is_collections_type(type_):
        return type_ in (collections.UserString,)
    elif is_regex_type(type_):
        return True
    return False


def is_integer_type(type_):
    if is_builtin_type(type_):
        return type_ in (int,)
    return False


def is_number_type(type_):
    if is_builtin_type(type_):
        return type_ in (float, complex)
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