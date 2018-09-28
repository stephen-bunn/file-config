# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import typing
import warnings
import collections

import six
import attr

from .constants import CONFIG_KEY
from .utils import (
    is_config_type,
    is_config_var,
    is_typing_type,
    is_builtin_type,
    is_string_type,
    is_number_type,
    is_array_type,
    is_object_type,
)

# TODO: handle jsonschema/typing union types and regex pattern matching


def _build_string_type(var, property_path=[]):
    schema = {"type": "string"}
    # TODO: handle jsonschema arguments
    return schema


def _build_number_type(var, property_path=[]):
    schema = {"type": "number"}
    # TODO: handle jsonschema arguments
    return schema


def _build_array_type(var, property_path=[]):
    schema = {"type": "array", "items": {"$id": f"#/{'/'.join(property_path)}/items"}}
    if is_typing_type(var.type) and len(var.type.__args__) > 0:
        # NOTE: typing.List only allows one typing argument
        nested_type = var.type.__args__[0]
        schema["items"].update(
            _build(nested_type, property_path=property_path + ["items"])
        )
    return schema


def _build_object_type(var, property_path=[]):
    schema = {"type": "object"}
    if is_typing_type(var.type) and len(var.type.__args__) == 2:
        (key_type, value_type) = var.type.__args__

        key_pattern = "^(.*)$"
        # FIXME: find a way to override the regex used in patternProperties
        # (and everywhere else)
        if not is_string_type(key_type):
            raise ValueError(
                f"cannot serialize object with key of type {key_type!r}, "
                f"located in var {var.name!r}"
            )

        schema["patternProperties"] = {
            key_pattern: _build(value_type, property_path=property_path)
        }

    return schema


def _build_type(type_, value, property_path=[]):
    for (type_check, builder) in (
        (is_string_type, _build_string_type),
        (is_number_type, _build_number_type),
        (is_array_type, _build_array_type),
        (is_object_type, _build_object_type),
    ):
        if type_check(type_):
            return builder(value, property_path=property_path)

    warnings.warn(f"unhandled translation for type {type_!r}")
    return {}


def _build_var(var, property_path=[]):
    if not is_config_var(var):
        raise ValueError(f"var {var!r} is not a config var")

    schema = {"$id": f"#/{'/'.join(property_path)}/{var.name}"}
    entry = var.metadata[CONFIG_KEY]

    if var.default is not None:
        schema["default"] = var.default

    if entry is not None:
        if isinstance(entry.title, six.string_types):
            schema["title"] = entry.title
        if isinstance(entry.description, six.string_types):
            schema["description"] = entry.description
        if isinstance(entry.examples, collections.Iterable) and len(entry.examples) > 0:
            schema["examples"] = entry.examples

    schema.update(_build_type(var.type, var, property_path=property_path + [var.name]))
    return schema


def _build_config(config_cls, property_path=[]):
    if not is_config_type(config_cls):
        raise ValueError(f"class {config_cls!r} is not a config class")

    schema = {"type": "object", "required": [], "properties": {}}
    cls_entry = getattr(config_cls, CONFIG_KEY)

    # add schema title, defaults to config classes `__qualname__`
    schema_title = cls_entry.get("title", config_cls.__qualname__)
    if isinstance(schema_title, six.string_types):
        schema["title"] = schema_title

    schema_description = cls_entry.get("description")
    if isinstance(schema_description, str):
        schema["description"] = schema_description

    # if the length of the property path is 0, assume that current object is root
    if len(property_path) <= 0:
        schema["$id"] = f"{config_cls.__qualname__}.json"
        schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    else:
        schema["$id"] = f"#/{'/'.join(property_path)}"

    property_path.append("properties")
    for var in attr.fields(config_cls):
        if not is_config_var(var):
            # encountered attribute is not a serialized field (i.e. missing CONFIG_KEY)
            continue
        entry = var.metadata[CONFIG_KEY]
        if entry.required:
            schema["required"].append(var.name)

        if is_config_type(var.type):
            schema["properties"][var.name] = _build_config(
                var.type, property_path=property_path + [var.name]
            )
        else:
            schema["properties"][var.name] = _build_var(
                var, property_path=property_path
            )

    return schema


def _build(value, property_path=[]):
    if is_config_type(value):
        return _build_config(value, property_path=property_path)
    elif is_config_var(value):
        return _build_var(value, property_path=property_path)
    return _build_type(type(value), value, property_path=property_path)


def build_schema(config_cls):
    return _build_config(config_cls, property_path=[])
