# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import typing
from functools import partialmethod
from collections import OrderedDict

import attr
import jsonschema

from . import handlers

CONFIG_KEY = "__file_config_metadata"


@attr.s(slots=True)
class _ConfigEntry(object):
    """ Configuration entry.
    """

    name = attr.ib(type=str, default=None)
    title = attr.ib(type=str, default=None)
    description = attr.ib(type=str, default=None)
    required = attr.ib(type=bool, default=True)
    examples = attr.ib(type=list, default=None)


def _handle_dumps(self, handler):
    """ Dumps caller, used by partial method for dynamic handler assignments.

    :param handler: The dump handler
    :type handler: object
    :return: The dumped string
    :rtype: str
    """

    return handler.dumps(to_dict(self))


def _handle_dump(self, handler, file_object):
    """ Dump caller, used by partial method for dynamic handler assignments.

    :param handler: The dump handler
    :type handler: object
    :param file_object: The file object to dump to
    :type file_object: File
    :return: The dumped string
    :rtype: str
    """

    return handler.dump(to_dict(self), file_object)


@classmethod
def _handle_loads(cls, handler, content):
    """ Loads caller, used by partial method for dynamic handler assignments.

    :param handler: The loads handler
    :type handler: object
    :param content: The content to load from
    :type content: str
    :return: The loaded instance
    :rtype: object
    """

    return from_dict(cls, handler.loads(content))


@classmethod
def _handle_load(cls, handler, file_object):
    """ Loads caller, used by partial method for dynamic handler assignments.

    :param handler: The loads handler
    :type handler: object
    :param file_object: The file object to load from
    :type file_object: File
    :return: The loaded instance
    :rtype: object
    """

    return from_dict(cls, handler.load(file_object))


def config(maybe_cls=None, title=None, description=None):
    """ File config class decorator.

    :param maybe_cls: The class to inherit from, defaults to None
    :param maybe_cls: object, optional
    :return: Wrapped class
    :rtype: object
    """

    def wrap(config_cls):
        """ The wrapper function.

        :return: The class decorator
        :rtype: object
        """

        setattr(config_cls, CONFIG_KEY, dict(title=title, description=description))
        # dynamically assign available handlers to the wrapped class
        for handler_name in handlers.__all__:
            handler = getattr(handlers, handler_name)()
            setattr(
                config_cls,
                f"dumps_{handler.name}",
                partialmethod(_handle_dumps, handler),
            )
            setattr(
                config_cls, f"dump_{handler.name}", partialmethod(_handle_dump, handler)
            )
            setattr(
                config_cls,
                f"loads_{handler.name}",
                partialmethod(_handle_loads, handler),
            )
            setattr(
                config_cls, f"load_{handler.name}", partialmethod(_handle_load, handler)
            )
        return attr.s(config_cls, slots=True)

    if maybe_cls is None:
        return wrap
    else:
        return wrap(maybe_cls)


def var(
    default=None,
    type=None,
    name=None,
    title=None,
    description=None,
    required=True,
    examples=None,
    **kwargs,
):
    """ Creates a config variable.
    """

    kwargs.update(dict(default=default, type=type))
    return attr.ib(
        metadata={
            CONFIG_KEY: _ConfigEntry(
                name=name,
                title=title,
                description=description,
                required=required,
                examples=examples,
            )
        },
        **kwargs,
    )


def _is_config_type(type_):
    """ Checks if a type is a ``config`` type.

    :param type_: The type the check
    :type type_: object
    :return: True if ``type_`` is a config type, otherwise false
    :rtype: bool
    """

    return hasattr(type_, CONFIG_KEY)


def _is_typing_type(type_):
    """ Checks if a type is a ``typing`` type.

    :param type_: The type to check
    :type type_: object
    :return: True if ``type_`` is a typing type, otherwise False
    :rtype: bool
    """

    if type_ is not None:
        return getattr(type_, "__module__", None) == "typing"
    return False


def _get_schema_type(type_):
    """ Gets the jsonschema type name for a given python type.

    :param type_: The python type to translate
    :type type_: object
    :return: The corresponding jsonschema type
    :rtype: str
    """

    if type_ is not None:
        is_string = type_ in (str,)
        is_number = type_ in (int, float)
        is_array = type_ in (list, tuple, set, frozenset)
        is_object = type_ in (dict, OrderedDict)
        if _is_typing_type(type_):
            is_array = type_.__origin__ in (
                typing.List,
                typing.Tuple,
                typing.Set,
                typing.FrozenSet,
            )
            is_object = type_.__origin__ in (
                typing.Dict,
                typing.collections.OrderedDict,
            )

        assert sum((is_string, is_number, is_array, is_object)) <= 1, (
            f"encountered sittuation where type {type_!r} matches multiple jsonschema "
            "types"
        )

        if is_string:
            return "string"
        elif is_number:
            return "number"
        elif is_array:
            return "array"
        elif is_object:
            return "object"


def _build_type_schema(type_, property_path=[]):
    """ Builds the jsonschema entry for a type.

    :param type_: The type to build a schema for
    :type type_: object
    :param property_path: The current property path of the object, defaults to []
    :param property_path: list, optional
    :return: A jsonschema representation of the type
    :rtype: dict
    """

    schema = {}
    schema_type = _get_schema_type(type_)
    typing_used = _is_typing_type(type_)
    if schema_type is not None:
        schema["type"] = schema_type

    if "type" in schema:
        if schema["type"] == "array":
            schema["items"] = {"$id": f"#/{'/'.join(property_path)}/items"}
            if typing_used and len(type_.__args__) == 1:
                value = type_.__args__[0]
                if _is_config_type(value):
                    schema["items"].update(
                        _build_schema(value, property_path=property_path + ["items"])
                    )
                else:
                    schema["items"].update(
                        _build_type_schema(
                            value, property_path=property_path + ["items"]
                        )
                    )
        elif schema["type"] == "object":
            if typing_used and len(type_.__args__) == 2:
                key = "^(.*)$"
                schema_type = _get_schema_type(type_.__args__[0])
                if schema_type == "number":
                    key = "^([+-]?([0-9]*[.])?[0-9]+)$"

                value = type_.__args__[-1]
                if _is_config_type(value):
                    value = _build_schema(value, property_path=property_path)
                else:
                    if _get_schema_type(value) is not None:
                        value = _build_type_schema(value)
                schema["patternProperties"] = {key: value}
    return schema


def _build_attribute_schema(attribute, property_path=[]):
    """ Builds a jsonschema entry for a given attrs attribute.

    :param attribute: The attribute to build a jsonschema entry for
    :type attribute: object
    :param property_path: The current property path of the object, defaults to []
    :param property_path: list, optional
    :return: A jsonschema representation of the type
    :rtype: dict
    """

    schema = {"$id": f"#/{'/'.join(property_path)}/{attribute.name}"}
    entry = None
    try:
        entry = attribute.metadata[CONFIG_KEY]
    except KeyError:
        pass

    if attribute.default is not None:
        schema["default"] = attribute.default
    if entry is not None:
        if isinstance(entry.title, str):
            schema["title"] = entry.title
        if isinstance(entry.description, str):
            schema["description"] = entry.description
        if isinstance(entry.examples, list) and len(entry.examples) > 0:
            schema["examples"] = entry.examples

    schema.update(
        _build_type_schema(
            attribute.type, property_path=property_path + [attribute.name]
        )
    )
    return schema


def _build_schema(config_cls, property_path=[]):
    """ Builds a jsonschema for a given config class.

    :param config_cls: The config class to build the jsonschema for
    :type config_cls: type
    :param property_path: The current property path, defaults to []
    :param property_path: list, optional
    :raises ValueError: When given ``config_cls`` is not a valid config class
    :return: A jsonschema for the config class
    :rtype: dict
    """

    if not _is_config_type(config_cls):
        raise ValueError(f"class {config_cls!r} is not a 'file_config.config' class")

    config_entry = getattr(config_cls, CONFIG_KEY)
    schema = {"type": "object", "required": [], "properties": {}}
    schema_title = config_entry.get("title", config_cls.__qualname__)
    if isinstance(schema_title, str):
        schema["title"] = schema_title
    schema_description = config_entry.get("description")
    if isinstance(schema_description, str):
        schema["description"] = schema_description

    if len(property_path) <= 0:
        schema["$id"] = f"{config_cls.__qualname__}.json"
        schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    else:
        schema["$id"] = f"#/{'/'.join(property_path)}"

    property_path.append("properties")
    for attribute in attr.fields(config_cls):
        try:
            entry = attribute.metadata[CONFIG_KEY]
        except KeyError:
            continue

        if entry.required:
            schema["required"].append(attribute.name)

        if _is_config_type(attribute.type):
            schema["properties"][attribute.name] = _build_schema(
                attribute.type, property_path=property_path + [attribute.name]
            )
        else:
            schema["properties"][attribute.name] = _build_attribute_schema(
                attribute, property_path=property_path
            )

    return schema


def build_schema(config_cls):
    """ Builds a jsonschema for a given config class.

    :param config_cls: The config class to build a jsonschema for
    :type config_cls: type
    :return: A jsonschema dictionary
    :rtype: dict
    """

    return _build_schema(config_cls, property_path=[])


def _build(config_cls, dictionary):
    """ Builds an instance of ``config_cls`` using ``dictionary``.

    :param config_cls: The class to use for building
    :type config_cls: type
    :param dictionary: The dictionary to use for building ``config_cls``
    :type dictionary: dict
    :return: An instance of ``config_cls``
    :rtype: object
    """

    values = {}
    for attribute in attr.fields(config_cls):
        try:
            entry = attribute.metadata[CONFIG_KEY]
        except KeyError:
            continue

        attribute_name = entry.name if entry.name else attribute.name
        attribute_default = attribute.default if attribute.default else None

        if attribute.type is None:
            values[attribute.name] = dictionary.get(attribute_name, attribute_default)
        else:
            schema_type = _get_schema_type(attribute.type)
            if schema_type == "array":
                values[attribute.name] = dictionary.get(attribute_name, [])
                if (
                    len(values[attribute.name]) > 0
                    and _is_typing_type(attribute.type)
                    and len(attribute.type.__args__) > 0
                ):
                    nested_type = attribute.type.__args__[0]
                    if _is_config_type(nested_type):
                        values[attribute.name] = [
                            _build(nested_type, item)
                            for item in dictionary.get(attribute_name, [])
                        ]
            else:
                item = dictionary.get(attribute_name, {})
                values[attribute.name] = (
                    _build(attribute.type, item)
                    if _is_config_type(attribute.type)
                    else item
                )

    return config_cls(**values)


def _dump(instance, dict_type=OrderedDict):
    """ Dumps an instance from ``instance`` to a dictionary type mapping.

    :param instance: The instance to serialized to a dictionary
    :type instance: object
    :param dict_type: Some dictionary type, defaults to ``OrderedDict``
    :type dict_type: object
    :return: Dumped dictionary
    :rtype: dict
    """

    values = dict_type()
    for attribute in attr.fields(instance.__class__):
        try:
            entry = attribute.metadata[CONFIG_KEY]
        except KeyError:
            continue

        attribute_name = entry.name if entry.name else attribute.name
        attribute_default = attribute.default if attribute.default else None

        schema_type = _get_schema_type(attribute.type)
        if schema_type == "array":
            items = getattr(instance, attribute.name, [])
            if isinstance(items, list):
                values[attribute_name] = [
                    (
                        _dump(item, dict_type=dict_type)
                        if _is_config_type(item)
                        else item
                    )
                    for item in items
                ]
        else:
            if _is_config_type(attribute.type):
                values[attribute_name] = _dump(
                    getattr(instance, attribute.name, {}), dict_type=dict_type
                )
            else:
                entry_value = getattr(instance, attribute.name, attribute_default)
                if isinstance(entry_value, (dict, OrderedDict)):
                    entry_mapping = {}
                    for (key, value) in entry_value.items():
                        entry_mapping[key] = (
                            _dump(value, dict_type=dict_type)
                            if _is_config_type(value)
                            else value
                        )
                    entry_value = entry_mapping
                if entry_value is not None:
                    values[attribute_name] = entry_value

    return values


def validate(instance):
    """ Validates a given ``instance``.

    :param instance: The instance to validate
    :type instance: object
    """

    jsonschema.validate(
        to_dict(instance, dict_type=dict), build_schema(instance.__class__)
    )


def from_dict(config_cls, dictionary):
    """ Loads an instance of ``config_cls`` from a dictionary.

    :param config_cls: The class to build an instance of
    :type config_cls: type
    :param dictionary: The dictionary to load from
    :type dictionary: dict
    :return: An instance of ``config_cls``
    :rtype: object
    """

    return _build(config_cls, dictionary)


def to_dict(instance, dict_type=OrderedDict):
    """ Dumps an instance to an dictionary mapping.

    :param instance: The instance to dump
    :type instance: object
    :param dict_type: The dictionary type to use, defaults to ``OrderedDict``
    :type dict_type: object
    :return: Dictionary serialization of instance
    :rtype: OrderedDict
    """

    return _dump(instance, dict_type=dict_type)
