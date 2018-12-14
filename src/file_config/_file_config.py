# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

from functools import partialmethod
from collections import OrderedDict

import attr
import jsonschema

from . import handlers
from .utils import (
    typecast,
    is_config,
    encode_bytes,
    is_enum_type,
    is_array_type,
    is_bytes_type,
    is_config_var,
    is_config_type,
    is_object_type,
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
    encoder = attr.ib(default=None)
    decoder = attr.ib(default=None)
    min = attr.ib(type=int, default=None)
    max = attr.ib(type=int, default=None)
    unique = attr.ib(type=bool, default=None)
    contains = attr.ib(type=list, default=None)


def _handle_dumps(self, handler, **kwargs):
    """ Dumps caller, used by partial method for dynamic handler assignments.

    :param object handler: The dump handler
    :return: The dumped string
    :rtype: str
    """

    return handler.dumps(self.__class__, to_dict(self), **kwargs)


def _handle_dump(self, handler, file_object, **kwargs):
    """ Dump caller, used by partial method for dynamic handler assignments.

    :param object handler: The dump handler
    :param file file_object: The file object to dump to
    :return: The dumped string
    :rtype: str
    """

    return handler.dump(self.__class__, to_dict(self), file_object, **kwargs)


@classmethod
def _handle_loads(cls, handler, content, validate=False, **kwargs):
    """ Loads caller, used by partial method for dynamic handler assignments.

    :param object handler: The loads handler
    :param str content: The content to load from
    :param bool validate: Performs content validation before loading,
        defaults to False, optional
    :return: The loaded instance
    :rtype: object
    """

    return from_dict(cls, handler.loads(cls, content, **kwargs), validate=validate)


@classmethod
def _handle_load(cls, handler, file_object, validate=False, **kwargs):
    """ Loads caller, used by partial method for dynamic handler assignments.

    :param object handler: The loads handler
    :param file file_object: The file object to load from
    :param bool validate: Performs content validation before loading,
        defaults to False, optional
    :return: The loaded instance
    :rtype: object
    """

    return from_dict(cls, handler.load(cls, file_object, **kwargs), validate=validate)


def config(maybe_cls=None, these=None, title=None, description=None):
    """ File config class decorator.

    Usage is to simply decorate a **class** to make it a
    :func:`config <file_config._file_config.config>` class.

    >>> import file_config
    >>> @file_config.config(
            title="My Config Title",
            description="A description about my config"
        )
        class MyConfig(object):
            pass

    :param class maybe_cls: The class to inherit from, defaults to None, optional
    :param dict these: A dictionary of str to ``file_config.var`` to use as attribs
    :param str title: The title of the config, defaults to None, optional
    :param str description: A description of the config, defaults to None, optional
    :return: Config wrapped class
    :rtype: class
    """

    def wrap(config_cls):
        """ The wrapper function.

        :param class config_cls: The class to wrap
        :return: The config_cls wrapper
        :rtype: class
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
        config_vars = these if isinstance(these, dict) else None
        return attr.s(config_cls, these=config_vars, slots=True)

    if maybe_cls is None:
        return wrap
    else:
        return wrap(maybe_cls)


def var(
    type=None,  # noqa
    default=None,
    name=None,
    title=None,
    description=None,
    required=True,
    examples=None,
    encoder=None,
    decoder=None,
    min=None,  # noqa
    max=None,  # noqa
    unique=None,
    contains=None,
    **kwargs,
):
    """ Creates a config variable.

    Use this method to create the class variables of your
    :func:`config <file_config._file_config.config>` decorated class.

    >>> import file_config
    >>> @file_config.config
        class MyConfig(object):
            name = file_config.var(str)

    :param type type: The expected type of the variable, defaults to None, optional
    :param default: The default value of the var, defaults to None, optional
    :param str name: The serialized name of the variable, defaults to None, optional
    :param str title: The validation title of the variable, defaults to None, optional
    :param str description: The validation description of the variable,
        defaults to None, optional
    :param bool required: Flag to indicate if variable is required during validation,
        defaults to True, optional
    :param list examples: A list of validation examples, if necessary,
        defaults to None, optional
    :param encoder: The encoder to use for the var, defaults to None, optional
    :param decoder: The decoder to use for the var, defaults to None, optional
    :param int min: The minimum constraint of the variable, defaults to None, optional
    :param int max: The maximum constraint of the variable, defaults to None, optional
    :param bool unique: Flag to indicate if variable should be unique,
        may not apply to all variable types, defaults to None, optional
    :param contains: Value that list varaible should contain in validation,
        may not apply to all variable types, defaults to None, optional
    :return: A new config variable
    :rtype: attr.Attribute
    """

    # NOTE: this method overrides some of the builtin Python method names on purpose in
    # order to supply a readable and easy to understand api
    # In this case it is not dangerous as they are only overriden in the scope and are
    # never used within the scope
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
                encoder=encoder,
                decoder=decoder,
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

    Usage is virtually the same as :func:`attr.make_class`.

    >>> import file_config
    >>> MyConfig = file_config.make_config(
            "MyConfig",
            {"name": file_config.var(str)}
        )

    :param str name: The name of the config
    :param dict var_dict: The dictionary of config variable definitions
    :param str title: The title of the config, defaults to None, optional
    :param str description: The description of the config, defaults to None, optional
    :return: A new config class
    :rtype: class
    """

    return config(
        attr.make_class(name, attrs={}, **kwargs),
        these=var_dict,
        title=title,
        description=description,
    )


def _build(config_cls, dictionary, validate=False):
    """ Builds an instance of ``config_cls`` using ``dictionary``.

    :param type config_cls: The class to use for building
    :param dict dictionary: The dictionary to use for building ``config_cls``
    :param bool validate: Performs validation before building ``config_cls``,
        defaults to False, optional
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
    if validate:
        jsonschema.validate(dictionary, build_schema(config_cls))

    kwargs = {}
    for var in attr.fields(config_cls):
        if not is_config_var(var):
            continue

        entry = var.metadata[CONFIG_KEY]
        arg_key = entry.name if entry.name else var.name
        arg_default = var.default if var.default else None

        if callable(entry.decoder):
            kwargs[var.name] = entry.decoder(dictionary.get(arg_key, arg_default))
            continue

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
                (_, value_type) = entry.type.__args__
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
            if arg_key not in dictionary:
                kwargs[var.name] = None
            else:
                kwargs[var.name] = typecast(
                    entry.type, dictionary.get(arg_key, arg_default)
                )

    return config_cls(**kwargs)


def _dump(config_instance, dict_type=OrderedDict):
    """ Dumps an instance from ``instance`` to a dictionary type mapping.

    :param object instance: The instance to serialized to a dictionary
    :param object dict_type: Some dictionary type, defaults to ``OrderedDict``
    :return: Dumped dictionary
    :rtype: collections.OrderedDict (or instance of ``dict_type``)
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

        if callable(entry.encoder):
            result[dump_key] = entry.encoder(
                getattr(config_instance, var.name, dump_default)
            )
            continue

        if is_array_type(entry.type):
            items = getattr(config_instance, var.name, [])
            if items is not None:
                result[dump_key] = [
                    (_dump(item, dict_type=dict_type) if is_config(item) else item)
                    for item in items
                ]
        elif is_enum_type(entry.type):
            dump_value = getattr(config_instance, var.name, dump_default)
            result[dump_key] = (
                dump_value.value if dump_value in entry.type else dump_value
            )
        elif is_bytes_type(entry.type):
            result[dump_key] = encode_bytes(
                getattr(config_instance, var.name, dump_default)
            )
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

    :param object instance: The instance to validate
    :raises jsonschema.exceptions.ValidationError: On failed validation
    """

    jsonschema.validate(
        to_dict(instance, dict_type=dict), build_schema(instance.__class__)
    )


def from_dict(config_cls, dictionary, validate=False):
    """ Loads an instance of ``config_cls`` from a dictionary.

    :param type config_cls: The class to build an instance of
    :param dict dictionary: The dictionary to load from
    :param bool validate: Preforms validation before building ``config_cls``,
        defaults to False, optional
    :return: An instance of ``config_cls``
    :rtype: object
    """

    return _build(config_cls, dictionary, validate=validate)


def to_dict(instance, dict_type=OrderedDict):
    """ Dumps an instance to an dictionary mapping.

    :param object instance: The instance to dump
    :param object dict_type: The dictionary type to use, defaults to ``OrderedDict``
    :return: Dictionary serialization of instance
    :rtype: OrderedDict
    """

    return _dump(instance, dict_type=dict_type)
