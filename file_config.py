# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import typing
from collections import OrderedDict

import attr
import yaml
import tomlkit
import jsonschema
import ujson as json

CONFIG_KEY = "__file_config_metadata"


def yaml_represent_ordereddict(dumper, data):
    """ A custom data representer for ``OrderedDict`` instances.

    .. note:: Credit to https://stackoverflow.com/a/16782282/7828560.

    :param dumper: The dumper object
    :type dumper: object
    :param data: The ``OrderedDict`` instance
    :type data: OrderedDict
    :return: The yaml mapping node
    :rtype: yaml.nodes.MappingNode
    """

    values = []
    for (key, value) in data.items():
        values.append((dumper.represent_data(key), dumper.represent_data(value)))
    return yaml.nodes.MappingNode("tag:yaml.org,2002:map", values)


# add a custom representer for OrderedDict for correctly ordered yaml
yaml.add_representer(OrderedDict, yaml_represent_ordereddict)


@attr.s(slots=True)
class _ConfigEntry(object):
    """ Configuration entry.
    """

    name = attr.ib(type=str, default=None)
    default = attr.ib(default=None)
    required = attr.ib(type=bool, default=True)
    subclass = attr.ib(type=object, default=None)
    multiple = attr.ib(type=bool, default=False)


def config(maybe_cls=None):
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

        setattr(config_cls, CONFIG_KEY, True)
        return attr.s(config_cls, slots=True)

    if maybe_cls is None:
        return wrap
    else:
        return wrap(maybe_cls)


def var(default=None, name=None, required=True, **kwargs):
    """ Creates a config variable.
    """

    type_ = kwargs.get("type")
    is_multiple = _get_schema_type(type_) == "array"
    subclass = None
    if _is_config_type(type_):
        subclass = type_
    elif _is_typing_type(type_):
        if is_multiple and _is_config_type(type_.__args__[0]):
            subclass = type_.__args__[0]

    return attr.ib(
        metadata={
            CONFIG_KEY: _ConfigEntry(name, default, required, subclass, is_multiple)
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
        return "__module__" in type_.__dict__ and type_.__module__ == "typing"
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
    if attribute.default is not None:
        schema["default"] = attribute.default

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

    schema = {
        "type": "object",
        "title": config_cls.__qualname__,
        "required": [],
        "properties": {},
    }
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
        if entry.subclass is None:
            schema["properties"][attribute.name] = _build_attribute_schema(
                attribute, property_path=property_path
            )
        else:
            schema["properties"][attribute.name] = _build_schema(
                entry.subclass, property_path=property_path + [attribute.name]
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
        entry_default = entry.default if entry.default else None
        if attribute.type is None:
            values[attribute.name] = dictionary.get(attribute_name, entry_default)
        else:
            if entry.multiple:
                values[attribute.name] = [
                    _build(entry.subclass, _)
                    for _ in dictionary.get(attribute_name, [])
                ]
            else:
                values[attribute.name] = _build(
                    entry.subclass, dictionary.get(attribute_name, {})
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
        # TODO: convert to attribute.default rather than entry.default
        entry_default = entry.default if entry.default else None

        if entry.subclass is None:
            entry_value = getattr(instance, attribute.name, entry_default)
            if isinstance(entry_value, (OrderedDict, dict)):
                entry_mapping = {}
                for (key, value) in entry_value.items():
                    entry_mapping[key] = _dump(value, dict_type=dict_type)
                entry_value = entry_mapping
            values[attribute_name] = entry_value
        else:
            if entry.multiple:
                values[attribute_name] = [
                    _dump(_, dict_type=dict_type)
                    for _ in getattr(instance, attribute.name, [])
                ]
            else:
                values[attribute_name] = _dump(
                    getattr(instance, attribute.name, {}), dict_type=dict_type
                )
    return values


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


def loads_json(config_cls, json_content):
    """ Loads an instance of ``config_cls`` from a json string.

    :param config_cls: The class to build an instance of
    :type config_cls: type
    :param json_content: The json content to load from
    :type json_content: dict
    :return: An instance of ``config_cls``
    :rtype: object
    """

    return from_dict(config_cls, json.loads(json_content))


def loads_yaml(config_cls, yaml_content):
    """ Loads an instance of ``config_cls`` from a yaml string.

    :param config_cls: The class to build an instance of
    :type config_cls: type
    :param yaml_content: The yaml content to load from
    :type yaml_content: dict
    :return: An instance of ``config_cls``
    :rtype: object
    """

    return from_dict(config_cls, yaml.load(yaml_content))


def loads_toml(config_cls, toml_content):
    """ Loads an instance of ``config_cls`` from a toml string.

    :param config_cls: The class to build an instance of
    :type config_cls: type
    :param toml_content: The toml content to load from
    :type toml_content: dict
    :return: An instance of ``config_cls``
    :rtype: object
    """

    return from_dict(config_cls, tomlkit.parse(toml_content))


def loads(config_cls, content):
    """ Loads an instance of ``config_cls`` from some content.

    .. note:: It is almost always more efficient to just use the explicit ``load`` such
        as ``loads_json`` or ``loads_toml`` as this iterates over the handlers and tries
        to find which one succeeds.

    :param content: The content to load from
    :type content: str
    :raises ValueError: If no parser can handle the loading
    :return: An instance of ``config_cls``
    :rtype: object
    """

    for handler in (loads_json, loads_toml, loads_yaml):
        try:
            return handler(config_cls, content)
        except Exception:
            pass
    raise ValueError(f"no parser can handle given content")


def load_json(config_cls, file_object):
    """ Loads an instance of ``config_cls`` from a given json file object.

    :param file_object: The JSON file object.
    :type file_object: File
    :return: An instance of ``config_cls``
    :rtype: object
    """

    return loads_json(config_cls, file_object.read())


def load_toml(config_cls, file_object):
    """ Loads an instance of ``config_cls`` from a given toml file object.

    :param file_object: The TOML file object.
    :type file_object: File
    :return: An instance of ``config_cls``
    :rtype: object
    """

    return loads_toml(config_cls, file_object.read())


def load_yaml(config_cls, file_object):
    """ Loads an instance of ``config_cls`` from a given yaml file object.

    :param file_object: The YAML file object.
    :type file_object: File
    :return: An instance of ``config_cls``
    :rtype: object
    """

    return loads_yaml(config_cls, file_object.read())


def load(config_cls, file_object):
    """ Loads an instance of ``config_cls`` from a file object.

    :param config_cls: The class to build an instance of
    :type config_cls: type
    :param file_object: The file object to load from
    :type file_object: File
    :return: An instance of ``config_cls``
    :rtype: object
    """

    return loads(config_cls, file_object.read())


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


def dumps_json(instance):
    """ Dumps an instance to a json string.

    :param instance: The instance to dump
    :type instance: object
    :return: JSON serialization of instance
    :rtype: str
    """

    return json.dumps(to_dict(instance))


def dumps_yaml(instance):
    """ Dumps an instance to a yaml string.

    :param instance: The instance to dump
    :type instance: object
    :return: YAML serialization of instance
    :rtype: str
    """

    return yaml.dump(to_dict(instance))


def dumps_toml(instance):
    """ Dumps an instance to a toml string.

    :param instance: The instance to dump
    :type instance: object
    :return: TOML serialization of instance
    :rtype: str
    """

    return tomlkit.dumps(to_dict(instance))


def dump_json(instance, file_object):
    """ Dumps an instance to a json file object.

    :param instance: The instance to dump
    :type instance: object
    :param file_object: JSON file object to dump to
    :type file_object: File
    """

    file_object.write(dumps_json(instance))


def dump_toml(instance, file_object):
    """ Dumps an instance to a toml file object.

    :param instance: The instance to dump
    :type instance: object
    :param file_object: TOML file object to dump to
    :type file_object: File
    """

    file_object.write(dumps_toml(instance))


def dump_yaml(instance, file_object):
    """ Dumps an instance to a yaml file object.

    :param instance: The instance to dump
    :type instance: object
    :param file_object: YAML file object to dump to
    :type file_object: File
    """

    file_object.write(dumps_yaml(instance))


def validate(instance):
    """ Validates a given ``instance``.

    :param instance: The instance to validate
    :type instance: object
    """

    jsonschema.validate(
        to_dict(instance, dict_type=dict), build_schema(instance.__class__)
    )
