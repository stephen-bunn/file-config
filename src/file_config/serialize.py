# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains helpers for config serialization."""

from typing import Any, Dict, Type, TypeVar
from collections import OrderedDict

from .types import CONFIG_FIELD_MISSING, Config_T
from .utils import (
    is_config,
    encode_bytes,
    is_enum_type,
    is_array_type,
    is_bytes_type,
    is_config_var,
    is_config_type,
    is_object_type,
)
from .constants import CONFIG_KEY

_T = TypeVar("_T")


def load(config_cls: Type[_T], content: Dict[str, Any], validate: bool = False) -> _T:

    if not is_config_type(config_cls):
        raise ValueError(
            f"Canont build instance of {config_cls!r} from {content!r}, "
            "class is not a config"
        )

    # TODO: handle validation

    for _, config_field in getattr(config_cls, "__dataclass_fields__", {}).items():
        if not is_config_var(config_field):
            continue

    # TODO: finish this up

def dump(config_instance: Config_T, dict_type: Type[_T] = OrderedDict) -> _T:

    if not is_config(config_instance):
        raise ValueError(
            f"Cannot dump instance {config_instance!r} to {dict_type!r}, "
            "instance is not a config class"
        )

    result: _T = dict_type()
    for _, config_field in getattr(
        config_instance.__class__,
        "__dataclass_fields__",
        {},
    ).items():
        if not is_config_var(config_field):
            continue

        metadata = config_field.metadata[CONFIG_KEY]
        # Attempt to pull key, type, and default from metadata if it exists,
        # otherwise default to the dataclasses' field properties.
        dump_key = metadata.name if metadata.name else config_field.name
        dump_type = metadata.type if metadata.type else config_field.type
        dump_default = (
            metadata.default
            if metadata.default and metadata.default != CONFIG_FIELD_MISSING
            else None
        )

        # When customer encoder is defined, rely on the callable for serialization
        if metadata.encoder and callable(metadata.encoder):
            result[dump_key] = metadata.encoder(
                getattr(config_instance, config_field.name, dump_default)
            )
            continue

        if is_bytes_type(dump_type):
            # Encode bytes with base64 before dumping
            result[dump_key] = encode_bytes(
                getattr(config_instance, config_field.name, dump_default)
            )
        elif is_enum_type(dump_type):
            # Only enum values are serializable
            dump_value = getattr(config_instance, config_field.name, dump_default)
            result[dump_key] = (
                dump_value.value if dump_value in dump_type else dump_value
            )
        elif is_array_type(dump_type):
            # Recursively serialize values if type is an iterable
            result[dump_key] = [
                (_dump(item, dict_type=dict_type) if is_config(item) else item)
                for item in getattr(config_instance, config_field.name, [])
            ]
        elif is_config_type(dump_type):
            # Recursively serialize values if type is an object
            result[dump_key] = _dump(
                getattr(config_instance, config_field.name, {}), dict_type=dict_type
            )
        else:
            dump_value = getattr(config_instance, config_field.name, dump_default)
            if is_object_type(type(dump_value)):
                # If the dump value we encounter is still an object that wasn't
                # previously handled, we still need to recursively dump the values of
                # the object
                dump_value = {
                    key: (
                        _dump(value, dict_type=dict_type) if is_config(value) else value
                    )
                    for key, value in dump_value.items()
                }

            if dump_value is not None:
                result[dump_key] = dump_value

    return result
