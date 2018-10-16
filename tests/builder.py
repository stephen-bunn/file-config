# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import random

import attr
from hypothesis.strategies import (
    data,
    none,
    builds,
    floats,
    one_of,
    booleans,
    integers,
    composite,
    characters,
    from_regex,
    complex_numbers,
)

import file_config

MIN_ARRAY_ENTRIES = 0
MAX_ARRAY_ENTRIES = 5
MIN_OBJECT_ENTRIES = 0
MAX_OBJECT_ENTRIES = 5


@composite
def build_array(
    draw, type_, min_entries=MIN_ARRAY_ENTRIES, max_entries=MAX_ARRAY_ENTRIES
):
    if file_config.utils.is_typing_type(type_) and len(type_.__args__) > 0:
        type_ = type_.__args__[0]
        builder = build_type
        if file_config.utils.is_array_type(type_):
            builder = build_array
        elif file_config.utils.is_object_type(type_):
            builder = build_object
        elif file_config.utils.is_config_type(type_):
            builder = build_config_dict
        return [
            draw(builder(type_))
            for _ in range(random.randint(min_entries, max_entries))
        ]
    return []


@composite
def build_array_var(
    draw, var, min_entries=MIN_ARRAY_ENTRIES, max_entries=MAX_ARRAY_ENTRIES
):
    entry = var.metadata[file_config.CONFIG_KEY]
    if isinstance(entry.min, int) and entry.min != min_entries:
        min_entries = entry.min
    if isinstance(entry.max, int) and entry.max != max_entries:
        max_entries = entry.max

    return draw(
        build_array(entry.type, min_entries=min_entries, max_entries=max_entries)
    )


@composite
def build_object(
    draw, type_, min_entries=MIN_OBJECT_ENTRIES, max_entries=MAX_OBJECT_ENTRIES
):
    if file_config.utils.is_typing_type(type_) and len(type_.__args__) > 0:
        # NOTE: assumes that all objects are json serializable (only strings as keys)
        type_ = type_.__args__[-1]
        builder = build_type
        if file_config.utils.is_array_type(type_):
            builder = build_array
        elif file_config.utils.is_object_type(type_):
            builder = build_object
        elif file_config.utils.is_config_type(type_):
            builder = build_config_dict
        return {
            draw(characters()): draw(builder(type_))
            for _ in range(random.randint(min_entries, max_entries))
        }
    return {}


@composite
def build_object_var(
    draw, var, min_entries=MIN_OBJECT_ENTRIES, max_entries=MAX_OBJECT_ENTRIES
):
    entry = var.metadata[file_config.CONFIG_KEY]
    if isinstance(entry.min, int) and entry.min != min_entries:
        min_entries = entry.min
    if isinstance(entry.max, int) and entry.max != max_entries:
        max_entries = entry.max

    return draw(
        build_object(entry.type, min_entries=min_entries, max_entries=max_entries)
    )


@composite
def build_type(draw, type_):
    if file_config.utils.is_null_type(type_):
        return draw(none())
    elif file_config.utils.is_bool_type(type_):
        return draw(booleans())
    elif file_config.utils.is_string_type(type_):
        if file_config.utils.is_regex_type(type_):
            # NOTE: hypothesis treats regexes differently than jsonschema
            # and that needs to be handled here
            return draw(from_regex(f"\A{type_.__supertype__.pattern}\Z"))
        return draw(characters())
    elif file_config.utils.is_integer_type(type_):
        return draw(integers())
    elif file_config.utils.is_number_type(type_):
        if type_ == float:
            return draw(floats())
        # elif type_ == complex:
        #     return draw(complex_numbers())


@composite
def build_var_dict(draw, var):
    assert file_config.utils.is_config_var(var)
    entry = var.metadata[file_config.CONFIG_KEY]
    value = None
    if file_config.utils.is_array_type(entry.type):
        value = draw(build_array_var(var))
    elif file_config.utils.is_object_type(entry.type):
        value = draw(build_object_var(var))
    elif file_config.utils.is_config_type(entry.type):
        value = draw(build_config_dict(var))
    else:
        value = draw(build_type(entry.type))
    return {var.name: value}


@composite
def build_config_dict(draw, config_cls):
    assert file_config.utils.is_config_type(config_cls)
    result = {}
    for var in attr.fields(config_cls):
        result.update(draw(build_var_dict(var)))
    return result


@composite
def build_config(draw, config_cls):
    return file_config.from_dict(config_cls, draw(build_config_dict(config_cls)))
