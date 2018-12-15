# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

import re
import base64
import typing
import itertools
import collections
from enum import Enum
from functools import lru_cache

import attr

from .constants import CONFIG_KEY, REGEX_TYPE_NAME


class Types(Enum):
    """ An enum which keeps a record of top-level type grouping names.

    .. note:: Specifically implemented for ease of use with the ``TYPE_MAPPINGS`` and
        helps reduce the use of **magic** strings used throughout the ``is_x_type``
        methods.
    """

    NULL = "null"
    BOOL = "bool"
    BYTES = "bytes"
    INTEGER = "integer"
    NUMBER = "number"
    STRING = "string"
    ARRAY = "array"
    OBJECT = "object"
    ENUM = "enum"
    UNION = "union"


COMPILED_PATTERN_TYPE = type(re.compile(""))
TYPE_MAPPINGS = {
    "builtins": {
        Types.NULL: (type(None),),
        Types.BOOL: (bool,),
        Types.BYTES: (bytes, bytearray),
        Types.INTEGER: (int,),
        Types.NUMBER: (float,),
        Types.STRING: (str,),
        Types.ARRAY: (list, tuple, set, frozenset),
        Types.OBJECT: (dict,),
        Types.ENUM: (Enum,),
    },
    "typing": {
        Types.STRING: (typing.AnyStr,),
        Types.ARRAY: (typing.List, typing.Tuple, typing.Set, typing.FrozenSet),
        Types.OBJECT: (typing.Dict, typing.ChainMap, typing.NamedTuple),
        Types.UNION: (typing.Union,),
    },
    "collections": {
        Types.STRING: (collections.UserString,),
        Types.ARRAY: (collections.UserList,),
        Types.OBJECT: (
            collections.ChainMap,
            collections.Counter,
            collections.OrderedDict,
            collections.UserDict,
        ),
    },
}


def _get_types(type_):
    """ Gathers all types within the ``TYPE_MAPPINGS`` for a specific ``Types`` value.

    :param Types type_: The type to retrieve
    :return: All types within the ``TYPE_MAPPINGS``
    :rtype: list
    """

    return list(
        itertools.chain.from_iterable(
            map(lambda x: TYPE_MAPPINGS[x].get(type_, []), TYPE_MAPPINGS)
        )
    )


def encode_bytes(bytes_):
    return base64.encodebytes(bytes_).decode("utf-8")


def decode_bytes(string):
    if is_string_type(type(string)):
        string = bytes(string, "utf-8")
    return base64.decodebytes(string)


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


@lru_cache()
def is_compiled_pattern(compiled_pattern):
    return isinstance(compiled_pattern, COMPILED_PATTERN_TYPE)


@lru_cache()
def is_builtin_type(type_):
    # NOTE: supported builtin types
    return isinstance(type_, type) and getattr(type_, "__module__", None) == "builtins"


@lru_cache()
def is_enum_type(type_):
    return isinstance(type_, type) and issubclass(type_, tuple(_get_types(Types.ENUM)))


@lru_cache()
def is_typing_type(type_):
    return getattr(type_, "__module__", None) == "typing"


@lru_cache()
def is_collections_type(type_):
    return (
        isinstance(type_, type) and getattr(type_, "__module__", None) == "collections"
    )


@lru_cache()
def is_regex_type(type_):
    return (
        callable(type_)
        and type_.__name__ == REGEX_TYPE_NAME
        and hasattr(type_, "__supertype__")
        and is_compiled_pattern(type_.__supertype__)
    )


@lru_cache()
def is_union_type(type_):
    if is_typing_type(type_) and hasattr(type_, "__origin__"):
        # NOTE: union types can only be from typing module
        return type_.__origin__ in _get_types(Types.UNION)
    return False


@lru_cache()
def is_null_type(type_):
    return type_ in _get_types(Types.NULL)


@lru_cache()
def is_bool_type(type_):
    return type_ in _get_types(Types.BOOL)


@lru_cache()
def is_bytes_type(type_):
    return type_ in _get_types(Types.BYTES)


@lru_cache()
def is_string_type(type_):
    string_types = _get_types(Types.STRING)
    if is_typing_type(type_):
        return type_ in string_types or is_regex_type(type_)
    return type_ in string_types


@lru_cache()
def is_integer_type(type_):
    return type_ in _get_types(Types.INTEGER)


@lru_cache()
def is_number_type(type_):
    return type_ in _get_types(Types.NUMBER)


@lru_cache()
def is_array_type(type_):
    array_types = _get_types(Types.ARRAY)
    if is_typing_type(type_):
        return type_ in array_types or (
            hasattr(type_, "__origin__") and type_.__origin__ in array_types
        )
    return type_ in array_types


def is_object_type(type_):
    object_types = _get_types(Types.OBJECT)
    if is_typing_type(type_):
        return type_ in object_types or (
            hasattr(type_, "__origin__") and type_.__origin__ in object_types
        )
    return type_ in object_types


def typecast(type_, value):
    # NOTE: does not do any special validation of types before casting
    # will just raise errors on type casting failures
    if is_builtin_type(type_) or is_collections_type(type_) or is_enum_type(type_):
        # FIXME: move to Types enum and TYPE_MAPPING entry
        if is_bytes_type(type_):
            return decode_bytes(value)
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
