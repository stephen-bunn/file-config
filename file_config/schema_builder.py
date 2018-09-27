# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import re
import collections
from typing import List

import six
import attr

from .constants import CONFIG_KEY
from .utils import is_config_type, is_config_var, is_typing_type

RE_PATTERN_TYPE = type(re.compile(""))


def _build_type(type_, property_path=[]):
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

    schema.update(_build_type(var.type, property_path=property_path + [var.name]))
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


def build_schema(config_cls):
    return _build_config(config_cls, property_path=[])
