# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import os
import pathlib

import attr
import toml
import yaml
import ujson as json

CONFIG_KEY = "file_config.config_metadata_key"


@attr.s(slots=True)
class _ConfigEntry(object):
    """ Configuration entry.
    """

    name = attr.ib(default=None)
    default = attr.ib(default=None)
    subclass = attr.ib(default=None)
    multiple = attr.ib(type=bool, default=False)


def config(maybe_cls=None):
    """ File config class decorator.

    :param maybe_cls: The class to inherit from, defaults to None
    :param maybe_cls: object, optional
    :return: Wrapped class
    :rtype: object
    """

    def wrap(cls):
        """ The wrapper function.

        :return: The class decorator
        :rtype: object
        """

        return attr.s(cls, slots=True)

    if maybe_cls is None:
        return wrap
    else:
        return wrap(maybe_cls)


def var(default=None, type=None, name=None, validator=None):
    """ Creates a config variable.
    """

    return attr.ib(
        default=default,
        type=type,
        validator=validator,
        metadata={CONFIG_KEY: _ConfigEntry(name, default, None, False)},
    )


def many(cls, default=None, name=None, validator=None):
    """ Creates a list of nested config instances.
    """

    return attr.ib(
        default=default,
        type=cls,
        validator=validator,
        metadata={CONFIG_KEY: _ConfigEntry(name, default, cls, True)},
    )


def one(cls, default=None, name=None, validator=None):
    """ Creates a single nested config instance.
    """

    return attr.ib(
        default=default,
        type=cls,
        validator=validator,
        metadata={CONFIG_KEY: _ConfigEntry(name, default, cls, False)},
    )


def _build(cls, dictionary):
    """ Builds an instance of ``cls`` using ``dictionary``.

    :param cls: The class to use for building
    :type cls: object
    :param dictionary: The dictionary to use for building ``cls``
    :type dictionary: dict
    :return: An instance of ``cls``
    :rtype: cls
    """

    values = {}
    for attribute in attr.fields(cls):
        try:
            entry = attribute.metadata[CONFIG_KEY]
        except KeyError:
            continue

        attribute_name = entry.name if entry.name else attribute.name
        entry_default = entry.default if entry.default else None
        if entry.subclass is None:
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
    return cls(**values)


def _dump(instance):
    """ Dumps an instance from ``instance`` to a dictionary.

    :param instance: The instance to serialized to a dictionary
    :type instance: object
    :return: Dumped dictionary
    :rtype: dict
    """

    values = {}
    for attribute in attr.fields(instance.__class__):
        try:
            entry = attribute.metadata[CONFIG_KEY]
        except KeyError:
            continue

        attribute_name = entry.name if entry.name else attribute.name
        entry_default = entry.default if entry.default else None
        if entry.subclass is None:
            values[attribute_name] = getattr(instance, attribute.name, entry_default)
        else:
            if entry.multiple:
                values[attribute_name] = [
                    _dump(_) for _ in getattr(instance, attribute.name, [])
                ]
            else:
                values[attribute_name] = _dump(getattr(instance, attribute.name, {}))
    return values


def from_dict(cls, dictionary):
    """ Loads an instance of ``cls`` from a dictionary.

    :param cls: The class to build an instance of
    :type cls: object
    :param dictionary: The dictionary to load from
    :type dictionary: dict
    :return: An instance of ``cls``
    :rtype: object
    """

    return _build(cls, dictionary)


def loads_json(cls, json_content):
    """ Loads an instance of ``cls`` from a json string.

    :param cls: The class to build an instance of
    :type cls: object
    :param json_content: The json content to load from
    :type json_content: dict
    :return: An instance of ``cls``
    :rtype: object
    """

    return from_dict(cls, json.loads(json_content))


def loads_yaml(cls, yaml_content):
    """ Loads an instance of ``cls`` from a yaml string.

    :param cls: The class to build an instance of
    :type cls: object
    :param yaml_content: The yaml content to load from
    :type yaml_content: dict
    :return: An instance of ``cls``
    :rtype: object
    """

    return from_dict(cls, yaml.load(yaml_content))


def loads_toml(cls, toml_content):
    """ Loads an instance of ``cls`` from a toml string.

    :param cls: The class to build an instance of
    :type cls: object
    :param toml_content: The toml content to load from
    :type toml_content: dict
    :return: An instance of ``cls``
    :rtype: object
    """

    return from_dict(cls, toml.loads(toml_content))


def loads(cls, content):
    """ Loads an instance of ``cls`` from some content.

    .. note:: It is almost always more efficient to just use the explicit ``load`` such
        as ``loads_json`` or ``loads_toml`` as this iterates over the handlers and tries
        to find which one succeeds.

    :param content: The content to load from
    :type content: str
    :raises ValueError: If no parser can handle the loading
    :return: An instance of ``cls``
    :rtype: object
    """

    for handler in (loads_json, loads_toml, loads_yaml,):
        try:
            return handler(cls, content)
        except Exception:
            pass
    raise ValueError(f"no parser can handle given content")


def load_json(cls, file_object):
    """ Loads an instance of ``cls`` from a given json file object.

    :param file_object: The JSON file object.
    :type file_object: File
    :return: An instance of ``cls``
    :rtype: object
    """

    return loads_json(cls, file_object.read())


def load_toml(cls, file_object):
    """ Loads an instance of ``cls`` from a given toml file object.

    :param file_object: The TOML file object.
    :type file_object: File
    :return: An instance of ``cls``
    :rtype: object
    """

    return loads_toml(cls, file_object.read())


def load_yaml(cls, file_object):
    """ Loads an instance of ``cls`` from a given yaml file object.

    :param file_object: The YAML file object.
    :type file_object: File
    :return: An instance of ``cls``
    :rtype: object
    """

    return loads_yaml(cls, file_object.read())


def load(cls, file_object):
    """ Loads an instance of ``cls`` from a file object.

    :param cls: The class to build an instance of
    :type cls: object
    :param file_object: The file object to load from
    :type file_object: File
    :return: An instance of ``cls``
    :rtype: object
    """

    return loads(cls, file_object.read())


def to_dict(instance):
    """ Dumps an instance to a dict.

    :param instance: The instance to dump
    :type instance: object
    :return: Dictionary serialization of instance
    :rtype: dict
    """

    return _dump(instance)


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

    return toml.dumps(to_dict(instance))


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
