# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains utility functions for checking and coercing types."""

import base64
import typing
import itertools
import collections
from enum import Enum
from typing import Any, Dict, Type, Tuple, Pattern, TypeVar

from .types import ConfigField_T
from .constants import CONFIG_KEY, REGEX_TYPE_NAME

_T = TypeVar("_T")


class SchemaType(Enum):
    """Defines the available support schema types."""

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


SCHEMA_TYPE_MAPPINGS: Dict[str, Dict[SchemaType, Tuple[Any]]] = {
    "builtins": {
        SchemaType.NULL: (type(None),),
        SchemaType.BOOL: (bool,),
        SchemaType.BYTES: (bytes, bytearray),
        SchemaType.INTEGER: (int,),
        SchemaType.NUMBER: (float,),
        SchemaType.ARRAY: (list, tuple, set, frozenset),
        SchemaType.OBJECT: (dict,),
        SchemaType.ENUM: (Enum,),
    },
    "typing": {
        SchemaType.STRING: (typing.AnyStr,),
        SchemaType.ARRAY: (typing.List, typing.Tuple, typing.Set, typing.FrozenSet),
        SchemaType.OBJECT: (typing.Dict, typing.ChainMap, typing.NamedTuple),
        SchemaType.UNION: (typing.Union,),
    },
    "collections": {
        SchemaType.STRING: (collections.UserString,),
        SchemaType.ARRAY: (collections.UserList,),
        SchemaType.OBJECT: (
            collections.ChainMap,
            collections.Counter,
            collections.OrderedDict,
            collections.UserDict,
        ),
    },
}


def _get_schema_types(schema_type: SchemaType) -> Tuple[Any]:
    """Gathers all supported Python types for a specific :class:`SchemaType`.

    Args:
        schema_type (SchemaType): The schema type to gather matching Python types for.

    Returns:
        Tuple[Any]: A tuple of supported Python types.
    """

    return tuple(
        itertools.chain.from_iterable(
            map(
                lambda type_: SCHEMA_TYPE_MAPPINGS[type_].get(schema_type, tuple()),
                SCHEMA_TYPE_MAPPINGS,
            )
        )
    )


def encode_bytes(value: bytes) -> str:
    """Encode some given bytes into a base64 encoded string.

    Examples:
        >>> encode_bytes(b"foobar")
        "Zm9vYmFy"

    Args:
        value (bytes): The bytes to encode.

    Returns:
        str: The base64 encoded string
    """

    return base64.encodebytes(value).decode("utf-8")


def decode_bytes(value: str) -> bytes:
    """Decode some base64 encoded string back into bytes.

    Examples:
        >>> decode_bytes("Zm9vYmFy")
        b"foobar"

    Args:
        value (str): The base64 encoded string to decode.

    Returns:
        bytes: The resulting decoded bytes.
    """

    return base64.decodebytes(bytes(value, "utf-8"))


def is_config_var(config_var: Any) -> bool:
    """Determine if a given value is a config var definition.

    Examples:
        >>> is_config_var(MyConfig.__dataclass_fields__["name"])
        True

    Args:
        config_var (Any): The potential config var definition.

    Returns:
        bool: True if the given value is a config var definition, otherwise False.
    """

    return (
        isinstance(config_var, ConfigField_T)
        and hasattr(config_var, "metadata")
        and config_var.metadata.get(CONFIG_KEY, None) is not None
    )


def is_config_type(config_type: Type) -> bool:
    """Determine if a given value is a config class.

    Examples:
        >>> @config
            MyConfig:
                name: str = var()
        >>> is_config_type(MyConfig)
        True

    Args:
        config_type (Type): The potential config decorated class.

    Returns:
        bool: True if the given value is a config decorated class, otherwise False.
    """

    return (
        isinstance(config_type, type)
        and hasattr(config_type, "__dataclass_params__")
        and hasattr(config_type, CONFIG_KEY)
    )


def is_config(config: object) -> bool:
    """Determine if a given value is a config class instance.

    Examples:
        >>> @config
            MyConfig:
                name: str = var()
        >>> is_config(MyConfig(name="Hello, World"))
        True

    Args:
        config (object): The potential config class instance.

    Returns:
        bool: True if the given value is a config class instance, otherwise False.
    """

    return isinstance(config, object) and is_config_type(type(config))


def is_builtin_type(type_: Type) -> bool:
    """Determine if a given value is a builtin type.

    Examples:
        >>> is_bulitin_type(int)
        True
        >>> is_builtin_type(1)
        False

    Args:
        type_ (Type): The potential builtin type.

    Returns:
        bool: True if the given value is a builtin type, otherwise False.
    """

    return isinstance(type_, type) and getattr(type_, "__module__", None) == "builtins"


def is_typing_type(type_: Any) -> bool:
    """Determine if a given value is a typing type.

    Examples:
        >>> is_typing_type(List[str])
        True
        >>> is_typing_type(list)
        False

    Args:
        type_ (Any): The potential typing type.

    Returns:
        bool: True if the given value is a typing type, otherwise False.
    """

    # Types from the typing module do not have a consistent base class type they use.
    # From my experience it's easier to just rely on checking the module.
    return getattr(type_, "__module__", None) == "typing"


def is_collections_type(type_: Type) -> bool:
    """Determine if a given value is a collections type.

    Examples:
        >>> is_collections_type(collections.ChainMap)
        True

    Args:
        type_ (Type): The potential collections type.

    Returns:
        bool: True if the given value is a collections type, otherwise False.
    """

    return (
        isinstance(type_, type) and getattr(type_, "__module__", None) == "collections"
    )


def is_enum_type(type_: Type) -> bool:
    """Determine if a given value is an enum type.

    Examples:
        >>> class MyEnum(Enum):
                VALUE = "value"
        >>> is_enum_type(MyEnum)
        True
        >>> is_enum_type(MyEnum.VALUE)
        False

    Args:
        type_ (Type): The potential enum type.

    Returns:
        bool: True if the given value is an enum class, otherwise False.
    """

    return isinstance(type_, type) and issubclass(
        type_, _get_schema_types(SchemaType.ENUM)
    )


def is_compiled_pattern(type_: Type) -> bool:
    """Determine if a given value is a compiled pattern from :mod:`re`.

    Examples:
        >>> is_compiled_pattern(re.compile(r""))
        True
        >>> is_compiled_pattern(r"")
        False

    Args:
        type_ (Type): The potentially compiled pattern.

    Returns:
        bool: True if the given value is a compiled pattern, otherwise False.
    """

    return isinstance(type_, Pattern)


def is_regex_type(type_: Type) -> bool:
    """Determine if a given value is a :func:`~utils.Regex` type.

    Examples:
        >>> is_regex_type(Regex(r"foobar"))
        True

    Args:
        type_ (Type): The potential regex type.

    Returns:
        bool: True if the given value is a type generated by :func:`~utils.Regex`,
            otherwise False.
    """

    return (
        callable(type_)
        and getattr(type_, "__name__", None) == REGEX_TYPE_NAME
        and hasattr(type_, "__supertype__")
        and is_compiled_pattern(type_.__supertype__)
    )


def is_null_type(type_: Type) -> bool:
    """Determine if a given value is a null type.

    Examples:
        >>> is_null_type(type(None))
        True

    Args:
        type_ (Type): The potential null type.

    Returns:
        bool: True if the given value is a null type, otherwise False.
    """

    return type_ in _get_schema_types(SchemaType.NULL)


def is_bool_type(type_: Type) -> bool:
    """Determine if a given value is a bool type.

    Examples:
        >>> is_bool_type(bool)
        True

    Args:
        type_ (Type): The potential bool type.

    Returns:
        bool: True if the given value should be represented by a bool type,
            otherwise False.
    """

    return type_ in _get_schema_types(SchemaType.BOOL)


def is_bytes_type(type_: Type) -> bool:
    """Determine if a given value is a bytes type.

    Examples:
        >>> is_bytes_type(bytes)
        True
        >>> is_bytes_type(bytearray)
        True

    Args:
        type_ (Type): The potential bytes type.

    Returns:
        bool: True if the given value should be represented by a bytes type,
            otherwise False.
    """

    return type_ in _get_schema_types(SchemaType.BYTES)


def is_string_type(type_: Type) -> bool:
    """Determine if a given value is a string type.

    Examples:
        >>> is_string_type(type("foobar"))
        True
        >>> is_string_type(Regex("foobar"))
        True
        >>> is_string_type(typing.AnyStr)
        True
        >>> is_string_type(collections.UserString)
        True

    Args:
        type_ (Type): The potential string type.

    Returns:
        bool: True if the given value should be represented by a string type,
            otherwise False.
    """

    string_types = _get_schema_types(SchemaType.STRING)
    # Regex types are considered string types when building schemas
    if is_typing_type(type_) and is_regex_type(type_):
        return True

    return type_ in string_types


def is_integer_type(type_: Type) -> bool:
    """Determine if a given value is a integer type.

    Examples:
        >>> is_integer_type(int)
        True

    Args:
        type_ (Type): The potential integer type.

    Returns:
        bool: True if the given value should be represented by a integer type,
            otherwise False.
    """

    return type_ in _get_schema_types(SchemaType.INTEGER)


def is_number_type(type_: Type) -> bool:
    """Determine if a given value is a number type.

    Examples:
        >>> is_number_type(float)
        True

    Args:
        type_ (Type): The potential number type.

    Returns:
        bool: True if the given value should be represented by a number type,
            otherwise False.
    """

    return type_ in _get_schema_types(SchemaType.NUMBER)


def is_array_type(type_: Type) -> bool:
    """Determine if a given value is a array type.

    Examples:
        >>> is_array_type(list)
        True
        >>> is_array_type(tuple)
        True
        >>> is_array_type(typing.List)
        True
        >>> is_array_type(typing.List[str])
        True

    Args:
        type_ (Type): The potential array type.

    Returns:
        bool: True if the given value should be represented by a array type,
            otherwise False.
    """

    array_types = _get_schema_types(SchemaType.ARRAY)
    # When given a type using subtypes (eg. typing.List[str]) we need to pull the
    # "origin" typing from the type to get typing.List
    if is_typing_type(type_) and getattr(type_, "__origin__", None) in array_types:
        return True

    return type_ in array_types


def is_object_type(type_: Type) -> bool:
    """Determine if a given value is an object type.

    Examples:
        >>> is_object_type(dict)
        True
        >>> is_object_type(typing.Dict)
        True
        >>> is_object_type(typing.Dict[str, Any])
        True
        >>> is_object_type(collections.OrderedDict)
        True

    Args:
        type_ (Type): The potential object type.

    Returns:
        bool: True if the given value should be represented by an object type,
            otherwise False.
    """

    object_types = _get_schema_types(SchemaType.OBJECT)
    # When given a type using subtypes (eg. typing.Dict[str, Any]) we need to pull the
    # "origin" typing from the type to get typing.Dict
    if is_typing_type(type_) and getattr(type_, "__origin__", None) in object_types:
        return True

    return type_ in object_types


def is_union_type(type_: Type) -> bool:
    """Determine if a given value is a :class:`typing.Union` type.

    .. note::
        Note that :class:`typing.Optional` is actually surfaced as a union of a given
        subtype and ``None``.

    Examples:
        >>> is_union_type(Union[str, bool])
        True
        >>> is_union_type(Optional[str])
        True

    Args:
        type_ (Type): The potential union type.

    Returns:
        bool: True if the given value is a union type, otherwise False.
    """

    return getattr(type_, "__origin__", None) in _get_schema_types(SchemaType.UNION)


def typecast(type_: Type[_T], value: Any) -> _T:
    """Attempt to cast a given value to a given type.

    Examples:
        >>> typecast(typing.List[int], ('1', '2', '3',))
        [1, 2, 3]
        >>> typecast(typing.Dict[str, int], {1, '2'})
        {'1': 2}

    Args:
        type_ (Type[_T]): The type to try and cast the value to.
        value (Any): The value to cast.

    Raises:
        ValueError:
            When the given value cannot be casted with the given type.

    Returns:
        _T: The typecasted value.
    """

    # Handle types that can simply be called to cast values
    if is_builtin_type(type_) or is_collections_type(type_) or is_enum_type(type_):
        # If the given type is bytes, return the decoded value
        # FIXME: Move to SchemaTypes enum?
        if is_bytes_type(type_):
            return decode_bytes(value)

        return type_(value)

    # Handle custom Regex type that should be treated as just strings
    elif is_regex_type(type_):
        return typecast(str, value)

    # Handle typing types
    elif is_typing_type(type_):
        # typing.GenericAlias uses __origin__ instead of __extra__
        # FIXME: Is this fetch of the base_type correct? What actually needs __extra__
        base_type = getattr(type_, "__extra__", getattr(type_, "__origin__"))
        arg_types = getattr(type_, "__args__", [])

        if is_array_type(type_):
            if len(arg_types) == 1:
                # When only a single subtype is declared for the array, we should
                # automatically typecast all items to that type
                return base_type([typecast(arg_types[0], item) for item in value])
            else:
                return base_type(value)
        elif is_object_type(type_):
            if len(arg_types) == 2:
                # When both a key and value subtype are declared for the object, we
                # should automatically typecast keys and values to those types
                return base_type(
                    {
                        typecast(arg_types[0], key): typecast(arg_types[-1], item)
                        for key, item in value.items()
                    }
                )

        # Fallback to just attempting to cast the value using the typing base type
        return base_type(value)

    # Default to the original value
    return value
