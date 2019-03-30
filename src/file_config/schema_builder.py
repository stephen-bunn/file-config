# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

import re
import typing
import warnings
import collections

import attr

from .utils import (
    is_bool_type,
    is_enum_type,
    is_null_type,
    is_array_type,
    is_config_var,
    is_regex_type,
    is_union_type,
    is_config_type,
    is_number_type,
    is_object_type,
    is_string_type,
    is_typing_type,
    is_builtin_type,
    is_integer_type,
)
from .constants import CONFIG_KEY, REGEX_TYPE_NAME


def Regex(pattern):
    """ A custom typing type to store regular expressions for schema building.

    :param str pattern: The regular expression
    :return: A new Regex type instance
    :rtype: typing.Type
    """

    return typing.NewType(REGEX_TYPE_NAME, re.compile(pattern))


def _build_attribute_modifiers(var, attribute_mapping, ignore=None):
    """ Handles adding schema modifiers for a given config var and some mapping.

    :param attr._make.Attribute var: The config var to build modifiers for
    :param Dict[str, str] attribute_mapping: A mapping of attribute to jsonschema
        modifiers
    :param List[str] ignore: A list of mapping keys to ignore, defaults to None
    :raises ValueError: When the given ``var`` is not an config var
    :raises ValueError: When jsonschema modifiers are given the wrong type
    :return: A dictionary of the built modifiers
    :rtype: Dict[str, Any]
    """

    if not isinstance(ignore, list):
        ignore = ["type", "name", "required", "default"]
    if not is_config_var(var):
        raise ValueError(
            f"cannot build field modifiers for {var!r}, is not a config var"
        )

    entry = var.metadata[CONFIG_KEY]
    modifiers = {}

    for (entry_attribute, entry_value) in zip(
        attr.fields(type(entry)), attr.astuple(entry)
    ):
        if entry_value is not None:
            if entry_attribute.name in ignore:
                continue
            elif entry_attribute.name in attribute_mapping:
                # NOTE: stupid type comparisons required for off case where
                # bool is a subclass of int `isinstance(True, (int, float)) == True`
                if entry_attribute.type is not None and (
                    type(entry_value) in entry_attribute.type
                    if isinstance(entry_attribute.type, (list, tuple, set))
                    else type(entry_value) == entry_attribute.type
                ):  # noqa
                    modifiers[attribute_mapping[entry_attribute.name]] = entry_value
                else:
                    raise ValueError(
                        f"invalid modifier type for modifier {entry_attribute.name!r} "
                        f"on var {var.name!r}, expected type {entry_attribute.type!r}, "
                        f"received {entry_value!r} of type {type(entry_value)!r}"
                    )
            else:
                warnings.warn(
                    f"field modifier {entry_attribute.name!r} has no effect on var "
                    f"{var.name!r} of type {entry.type!r}"
                )

    return modifiers


def _build_null_type(var, property_path=None):
    """ Builds schema definitions for null type values.

    :param var: The null type value
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    return {"type": "null"}


def _build_enum_type(var, property_path=None):
    """ Builds schema definitions for enum type values.

    :param var: The enum type value
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    entry = var.metadata[CONFIG_KEY]
    enum_values = [member.value for member in entry.type.__members__.values()]
    schema = {"enum": enum_values}

    for (type_name, check) in dict(
        bool=is_bool_type,
        string=is_string_type,
        number=is_number_type,
        integer=is_integer_type,
    ).items():
        if all(check(type(_)) for _ in enum_values):
            schema["type"] = type_name
            break

    return schema


def _build_bool_type(var, property_path=None):
    """ Builds schema definitions for boolean type values.

    :param var: The boolean type value
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :param property_path: [type], optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    return {"type": "boolean"}


def _build_string_type(var, property_path=None):
    """ Builds schema definitions for string type values.

    :param var: The string type value
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :param property_path: [type], optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    schema = {"type": "string"}
    if is_builtin_type(var):
        return schema

    if is_regex_type(var):
        schema["pattern"] = var.__supertype__.pattern
        return schema

    if is_config_var(var):
        schema.update(
            _build_attribute_modifiers(var, {"min": "minLength", "max": "maxLength"})
        )
        if is_regex_type(var.type):
            schema["pattern"] = var.type.__supertype__.pattern

    return schema


def _build_integer_type(var, property_path=None):
    """ Builds schema definitions for integer type values.

    :param var: The integer type value
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :param property_path: [type], optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    schema = {"type": "integer"}
    if is_builtin_type(var):
        return schema

    if is_config_var(var):
        schema.update(
            _build_attribute_modifiers(var, {"min": "minimum", "max": "maximum"})
        )

    return schema


def _build_number_type(var, property_path=None):
    """ Builds schema definitions for number type values.

    :param var: The number type value
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :param property_path: [type], optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    schema = {"type": "number"}
    if is_builtin_type(var):
        return schema

    if is_config_var(var):
        schema.update(
            _build_attribute_modifiers(var, {"min": "minimum", "max": "maximum"})
        )

    return schema


def _build_array_type(var, property_path=None):
    """ Builds schema definitions for array type values.

    :param var: The array type value
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :param property_path: [type], optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    schema = {"type": "array", "items": {"$id": f"#/{'/'.join(property_path)}/items"}}
    if is_builtin_type(var):
        return schema

    if is_config_var(var):
        schema.update(
            _build_attribute_modifiers(
                var,
                {
                    "min": "minItems",
                    "max": "maxItems",
                    "unique": "uniqueItems",
                    "contains": "contains",
                },
            )
        )

        if is_typing_type(var.type) and len(var.type.__args__) > 0:
            # NOTE: typing.List only allows one typing argument
            nested_type = var.type.__args__[0]
            schema["items"].update(
                _build(nested_type, property_path=property_path + ["items"])
            )
    elif is_typing_type(var):
        nested_type = var.__args__[0]
        schema["items"].update(
            _build(nested_type, property_path=property_path + ["items"])
        )

    return schema


def _build_object_type(var, property_path=None):
    """ Builds schema definitions for object type values.

    :param var: The object type value
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :param property_path: [type], optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    schema = {"type": "object"}
    if is_builtin_type(var):
        return schema

    entry = var.metadata[CONFIG_KEY]

    if isinstance(entry.min, int):
        schema["minProperties"] = entry.min
    if isinstance(entry.max, int):
        schema["maxProperties"] = entry.max

    # NOTE: typing.Dict only accepts two typing arguments
    if is_typing_type(var.type) and len(var.type.__args__) == 2:
        (key_type, value_type) = var.type.__args__

        key_pattern = "^(.*)$"
        if is_regex_type(key_type):
            key_pattern = key_type.__supertype__.pattern
        elif not is_string_type(key_type):
            raise ValueError(
                f"cannot serialize object with key of type {key_type!r}, "
                f"located in var {var.name!r}"
            )

        schema["patternProperties"] = {
            key_pattern: _build(value_type, property_path=property_path)
        }

    return schema


def _build_type(type_, value, property_path=None):
    """ Builds the schema definition based on the given type for the given value.

    :param type_: The type of the value
    :param value: The value to build the schema definition for
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    for (type_check, builder) in (
        (is_enum_type, _build_enum_type),
        (is_null_type, _build_null_type),
        (is_bool_type, _build_bool_type),
        (is_string_type, _build_string_type),
        (is_integer_type, _build_integer_type),
        (is_number_type, _build_number_type),
        (is_array_type, _build_array_type),
        (is_object_type, _build_object_type),
    ):
        if type_check(type_):
            return builder(value, property_path=property_path)

    # NOTE: warning ignores type None (as that is the config var default)
    if type_:
        warnings.warn(f"unhandled translation for type {type_!r} with value {value!r}")
    return {}


def _build_var(var, property_path=None):
    """ Builds a schema definition for a given config var.

    :param attr._make.Attribute var: The var to generate a schema definition for
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :raises ValueError: When the given ``var`` is not a file_config var
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    if not is_config_var(var):
        raise ValueError(f"var {var!r} is not a config var")

    entry = var.metadata[CONFIG_KEY]
    var_name = entry.name if entry.name else var.name
    schema = {"$id": f"#/{'/'.join(property_path)}/{var_name}"}

    if var.default is not None:
        schema["default"] = var.default

    if entry is not None:
        if isinstance(entry.title, str):
            schema["title"] = entry.title
        if isinstance(entry.description, str):
            schema["description"] = entry.description
        if isinstance(entry.examples, collections.Iterable) and len(entry.examples) > 0:
            schema["examples"] = entry.examples

    # handle typing.Union types by simply using the "anyOf" key
    if is_union_type(var.type):
        type_union = {"anyOf": []}
        for allowed_type in var.type.__args__:
            # NOTE: requires jsonschema draft-07
            type_union["anyOf"].append(
                _build_type(
                    allowed_type, allowed_type, property_path=property_path + [var_name]
                )
            )
        schema.update(type_union)
    else:
        schema.update(
            _build_type(var.type, var, property_path=property_path + [var_name])
        )
    return schema


def _build_config(config_cls, property_path=None):
    """ Builds the schema definition for a given config class.

    :param class config_cls: The config class to build a schema definition for
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :raises ValueError: When the given ``config_cls`` is not a config decorated class
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    if not is_config_type(config_cls):
        raise ValueError(f"class {config_cls!r} is not a config class")

    schema = {"type": "object", "required": [], "properties": {}}
    cls_entry = getattr(config_cls, CONFIG_KEY)

    # add schema title, defaults to config classes `__qualname__`
    schema_title = cls_entry.get("title", config_cls.__qualname__)
    if isinstance(schema_title, str):
        schema["title"] = schema_title

    schema_description = cls_entry.get("description")
    if isinstance(schema_description, str):
        schema["description"] = schema_description

    # if the length of the property path is 0, assume that current object is root
    if len(property_path) <= 0:
        schema["$id"] = f"{config_cls.__qualname__}.json"
        # NOTE: requires draft-07 for typing.Union type schema generation
        schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    else:
        schema["$id"] = f"#/{'/'.join(property_path)}"

    property_path.append("properties")
    for var in attr.fields(config_cls):
        if not is_config_var(var):
            # encountered attribute is not a serialized field (i.e. missing CONFIG_KEY)
            continue
        entry = var.metadata[CONFIG_KEY]
        var_name = entry.name if entry.name else var.name
        if entry.required:
            schema["required"].append(var_name)

        if is_config_type(var.type):
            schema["properties"][var_name] = _build_config(
                var.type, property_path=property_path + [var_name]
            )
        else:
            schema["properties"][var_name] = _build_var(
                var, property_path=property_path
            )

    return schema


def _build(value, property_path=None):
    """ The generic schema definition build method.

    :param value: The value to build a schema definition for
    :param List[str] property_path: The property path of the current type,
        defaults to None, optional
    :return: The built schema definition
    :rtype: Dict[str, Any]
    """

    if not property_path:
        property_path = []

    if is_config_type(value):
        return _build_config(value, property_path=property_path)
    elif is_config_var(value):
        return _build_var(value, property_path=property_path)
    elif is_builtin_type(value):
        return _build_type(value, value, property_path=property_path)
    elif is_regex_type(value):
        # NOTE: building regular expression types assumes type is string
        return _build_type(str, value, property_path=property_path)
    elif is_typing_type(value):
        return _build_type(value, value, property_path=property_path)
    return _build_type(type(value), value, property_path=property_path)


def build_schema(config_cls):
    """ Builds the JSONSchema for a given config class.

    :param class config_cls: The config class to build the JSONSchema for
    :return: The resulting JSONSchema
    :rtype: dict
    """

    return _build_config(config_cls, property_path=[])
