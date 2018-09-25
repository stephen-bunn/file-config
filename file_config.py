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
        if not entry.subclass:
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
        if not entry.subclass:
            values[attribute_name] = getattr(instance, attribute.name, entry_default)
        else:
            if entry.multiple:
                values[attribute_name] = [
                    _dump(entry.subclass, _)
                    for _ in getattr(instance, attribute.name, [])
                ]
            else:
                values[attribute_name] = _dump(
                    entry.subclass, getattr(instance, attribute.name, {})
                )
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


def from_json(cls, json_content):
    """ Loads an instance of ``cls`` from a json string.

    :param cls: The class to build an instance of
    :type cls: object
    :param json_content: The json content to load from
    :type json_content: dict
    :return: An instance of ``cls``
    :rtype: object
    """

    return from_dict(cls, json.loads(json_content))


def from_yaml(cls, yaml_content):
    """ Loads an instance of ``cls`` from a yaml string.

    :param cls: The class to build an instance of
    :type cls: object
    :param yaml_content: The yaml content to load from
    :type yaml_content: dict
    :return: An instance of ``cls``
    :rtype: object
    """

    return from_json(cls, yaml.load(yaml_content))


def from_toml(cls, toml_content):
    """ Loads an instance of ``cls`` from a toml string.

    :param cls: The class to build an instance of
    :type cls: object
    :param toml_content: The toml content to load from
    :type toml_content: dict
    :return: An instance of ``cls``
    :rtype: object
    """

    return from_json(cls, toml.loads(toml_content))


def from_content(cls, content, content_extension=".json"):
    """ Loads an instance of ``cls`` from a content string.

    :param cls: The class to build an instance of
    :type cls: object
    :param content: The content to load from
    :type content: str
    :param content_extension: The extension of the content, defaults to ".json"
    :param content_extension: str, optional
    :raises ValueError: If a content handler cannot be found for an extension
    :return: An instance of ``cls``
    :rtype: object
    """

    content_handlers = {
        ".json": from_json,
        ".toml": from_toml,
        ".yaml": from_yaml,
        ".yml": from_yaml,
    }
    if content_extension not in content_handlers:
        raise ValueError(f"don't know how to handle content from {content_extension!r}")
    return content_handlers[content_extension](cls, content)


def from_file(cls, filepath):
    """ Loads an instance of ``cls`` from a filepath.

    :param cls: The class to build an instance of
    :type cls: object
    :param filepath: The filepath to load from
    :type filepath: str
    :raises FileNotFoundError: If the filepath doesn't exist
    :return: An instance of ``cls``
    :rtype: object
    """

    filepath = pathlib.Path(filepath)
    if not filepath.is_file():
        raise FileNotFoundError(f"no such file {filepath!r} exists")
    with filepath.open("r") as stream:
        return from_content(cls, stream.read(), filepath.suffix.lower())


def to_dict(instance):
    """ Dumps an instance to a dict.

    :param instance: The instance to dump
    :type instance: object
    :return: Dictionary serialization of instance
    :rtype: dict
    """

    return _dump(instance)


def to_json(instance):
    """ Dumps an instance to a json string.

    :param instance: The instance to dump
    :type instance: object
    :return: JSON serialization of instance
    :rtype: str
    """

    return json.dumps(to_dict(instance))


def to_yaml(instance):
    """ Dumps an instance to a yaml string.

    :param instance: The instance to dump
    :type instance: object
    :return: YAML serialization of instance
    :rtype: str
    """

    return yaml.dump(to_dict(instance))


def to_toml(instance):
    """ Dumps an instance to a toml string.

    :param instance: The instance to dump
    :type instance: object
    :return: TOML serialization of instance
    :rtype: str
    """

    return toml.dumps(to_dict(instance))


def to_content(instance, content_extension=".json"):
    """ Dumps an instance to a content string.

    :param instance: The instance to dump
    :type instance: object
    :param content_extension: The extension of the format to dump, defaults to ".json"
    :param content_extension: str, optional
    :raises ValueError: If the content handler cannot be found for an extension
    :return: Serialization of an instance
    :rtype: str
    """

    content_handlers = {
        ".json": to_json,
        ".toml": to_toml,
        ".yaml": to_yaml,
        ".yml": to_yaml,
    }
    if content_extension not in content_handlers:
        raise ValueError(f"don't know how to handle content from {content_extension!r}")
    return content_handlers[content_extension](instance)


def to_file(instance, filepath):
    """ Writes an instance to a filepath.

    :param instance: The instance to write
    :type instance: object
    :param filepath: The filepath to write to
    :type filepath: str
    """

    filepath = pathlib.Path(filepath)
    with filepath.open("r") as stream:
        stream.write(to_content(instance, filepath.suffix.lower()))
