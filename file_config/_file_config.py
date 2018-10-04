# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import typing
from functools import partialmethod
from collections import OrderedDict

import attr
import jsonschema

from . import handlers
from .utils import (
    typecast,
    is_config,
    is_array_type,
    is_config_var,
    is_config_type,
    is_object_type,
    is_string_type,
    is_typing_type,
)
from .constants import CONFIG_KEY
from .schema_builder import build_schema


@attr.s(slots=True)
class _ConfigEntry(object):
    """ Configuration entry.
    """

    type = attr.ib(default=None)
    default = attr.ib(type=str, default=None)
    name = attr.ib(type=str, default=None)
    title = attr.ib(type=str, default=None)
    description = attr.ib(type=str, default=None)
    required = attr.ib(type=bool, default=True)
    examples = attr.ib(type=list, default=None)
    min = attr.ib(type=int, default=None)
    max = attr.ib(type=int, default=None)
    unique = attr.ib(type=bool, default=None)
    contains = attr.ib(type=list, default=None)


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
            handler = getattr(handlers, handler_name)
            if handler.available:
                handler = handler()
                setattr(
                    config_cls,
                    f"dumps_{handler.name}",
                    partialmethod(_handle_dumps, handler),
                )
                setattr(
                    config_cls,
                    f"dump_{handler.name}",
                    partialmethod(_handle_dump, handler),
                )
                setattr(
                    config_cls,
                    f"loads_{handler.name}",
                    partialmethod(_handle_loads, handler),
                )
                setattr(
                    config_cls,
                    f"load_{handler.name}",
                    partialmethod(_handle_load, handler),
                )
        return attr.s(config_cls, slots=True)

    if maybe_cls is None:
        return wrap
    else:
        return wrap(maybe_cls)


def var(
    type=None,
    default=None,
    name=None,
    title=None,
    description=None,
    required=True,
    examples=None,
    min=None,
    max=None,
    unique=None,
    contains=None,
    **kwargs,
):
    """ Creates a config variable.

    :param type: The expected type of the variable, defaults to None
    :param type: type, optional
    :param default: The default value of the var, defaults to None
    :param default: any, optional
    :param name: The serialized name of the variable, defaults to None
    :param name: str, optional
    :param title: The validation title of the variable, defaults to None
    :param title: str, optional
    :param description: The validation description of the variable, defaults to None
    :param description: str, optional
    :param required: Flag to indicate if variable is required during validation,
        defaults to True
    :param required: bool, optional
    :param examples: A list of validation examples, if necessary, defaults to None
    :param examples: list, optional
    :param min: The minimum constraint of the variable, defaults to None
    :param min: int, optional
    :param max: The maximum constraint of the variable, defaults to None
    :param max: int, optional
    :param unique: Flag to indicate if variable should be unique,
        may not apply to all variable types, defaults to None
    :param unique: bool, optional
    :param contains: Value that list varaible should contain in validation,
        may not apply to all variable types, defaults to None
    :param contains: any, optional
    :return: A new config variable
    :rtype: attr._make.Attribute
    """

    kwargs.update(dict(default=default, type=type))
    return attr.ib(
        metadata={
            CONFIG_KEY: _ConfigEntry(
                type=type,
                default=default,
                name=name,
                title=title,
                description=description,
                required=required,
                examples=examples,
                min=min,
                max=max,
                unique=unique,
                contains=contains,
            )
        },
        **kwargs,
    )


def make_config(name, var_dict, title=None, description=None, **kwargs):
    """ Creates a config instance from scratch.

    :param name: The name of the config
    :type name: str
    :param var_dict: The dictionary of config variable definitions
    :type var_dict: dict
    :param title: The title of the config, defaults to None
    :param title: str, optional
    :param description: The description of the config, defaults to None
    :param description: str, optional
    :return: A new config class
    :rtype: class
    """

    return config(
        attr.make_class(name, var_dict, **kwargs), title=title, description=description
    )


def _build(config_cls, dictionary):
    """ Builds an instance of ``config_cls`` using ``dictionary``.

    :param config_cls: The class to use for building
    :type config_cls: type
    :param dictionary: The dictionary to use for building ``config_cls``
    :type dictionary: dict
    :return: An instance of ``config_cls``
    :rtype: object
    """

    if not is_config_type(config_cls):
        raise ValueError(
            f"cannot build {config_cls!r} from {dictionary!r}, "
            f"{config_cls!r} is not a config"
        )

    # perform jsonschema validation on the given dictionary
    # (simplifys dynamic typecasting)
    jsonschema.validate(dictionary, build_schema(config_cls))

    kwargs = {}
    for var in attr.fields(config_cls):
        if not is_config_var(var):
            continue

        entry = var.metadata[CONFIG_KEY]
        arg_key = entry.name if entry.name else var.name
        arg_default = var.default if var.default else None

        if is_array_type(entry.type):
            if is_typing_type(entry.type) and len(entry.type.__args__) > 0:
                nested_type = entry.type.__args__[0]
                if is_config_type(nested_type):
                    kwargs[var.name] = [
                        _build(nested_type, item)
                        for item in dictionary.get(arg_key, [])
                    ]
                else:
                    kwargs[var.name] = typecast(entry.type, dictionary.get(arg_key, []))
        elif is_object_type(entry.type):
            item = dictionary.get(arg_key, {})
            if is_typing_type(entry.type) and len(entry.type.__args__) == 2:
                (key_type, value_type) = entry.type.__args__
                kwargs[var.name] = {
                    key: _build(value_type, value)
                    if is_config_type(value_type)
                    else typecast(value_type, value)
                    for (key, value) in item.items()
                }
            else:
                kwargs[var.name] = typecast(entry.type, item)
        elif is_config_type(entry.type):
            kwargs[var.name] = _build(entry.type, dictionary.get(arg_key, arg_default))
        else:
            # TODO: handle correct type casting logic based on builtin or typing types
            kwargs[var.name] = typecast(
                entry.type, dictionary.get(arg_key, arg_default)
            )

    return config_cls(**kwargs)


def _dump(config_instance, dict_type=OrderedDict):
    """ Dumps an instance from ``instance`` to a dictionary type mapping.

    :param instance: The instance to serialized to a dictionary
    :type instance: object
    :param dict_type: Some dictionary type, defaults to ``OrderedDict``
    :type dict_type: object
    :return: Dumped dictionary
    :rtype: dict
    """

    if not is_config(config_instance):
        raise ValueError(
            f"cannot dump instance {config_instance!r} to dict, "
            "instance is not a config class"
        )

    result = dict_type()
    for var in attr.fields(config_instance.__class__):
        if not is_config_var(var):
            continue

        entry = var.metadata[CONFIG_KEY]
        dump_key = entry.name if entry.name else var.name
        dump_default = var.default if var.default else None

        if is_array_type(entry.type):
            items = getattr(config_instance, var.name, [])
            if items is not None:
                result[dump_key] = [
                    (_dump(item, dict_type=dict_type) if is_config(item) else item)
                    for item in items
                ]
        else:
            if is_config_type(entry.type):
                result[dump_key] = _dump(
                    getattr(config_instance, var.name, {}), dict_type=dict_type
                )
            else:
                dump_value = getattr(config_instance, var.name, dump_default)
                if is_object_type(type(dump_value)):
                    dump_value = {
                        key: (
                            _dump(value, dict_type=dict_type)
                            if is_config(value)
                            else value
                        )
                        for (key, value) in dump_value.items()
                    }

                if dump_value is not None:
                    result[dump_key] = dump_value

    return result


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
