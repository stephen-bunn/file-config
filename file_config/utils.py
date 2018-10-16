# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import re
import typing
import collections

import attr

from .constants import CONFIG_KEY, REGEX_TYPE_NAME

COMPILED_PATTERN_TYPE = type(re.compile(""))


def is_config_var(var):
    return (
        isinstance(var, (attr._make.Attribute, attr._make._CountingAttr))
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
        and type_.__name__ == REGEX_TYPE_NAME
        and hasattr(type_, "__supertype__")
        and is_compiled_pattern(type_.__supertype__)
    )


def is_union_type(type_):
    return isinstance(type_, typing._Union)


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
        return type_ in (float,)
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


def typecast(type_, value):
    # NOTE: does not do any special validation of types before casting
    # will just raise errors on type casting failures
    if is_builtin_type(type_) or is_collections_type(type_):
        return type_(value)
    elif is_regex_type(type_):
        return typecast(str, value)
    elif is_typing_type(type_):
        base_type = type_.__extra__
        arg_types = type_.__args__

        if is_array_type(type_):
            if len(arg_types) == 1:
                item_type = arg_types[0]
                return base_type([typecast(item_type, item) for item in value])
            else:
                return base_type(value)
        elif is_object_type(type_):
            if len(arg_types) == 2:
                (key_type, item_type) = arg_types
                return base_type(
                    {
                        typecast(key_type, key): typecast(item_type, item)
                        for (key, item) in value.items()
                    }
                )
            else:
                return base_type(value)
        else:
            return base_type(value)
    else:
        return value
