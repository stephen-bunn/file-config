# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

from typing import Any, Dict, List, Type, Union, TypeVar, Callable, Optional, overload
from dataclasses import field, dataclass, make_dataclass

from .types import CONFIG_FIELD_MISSING, Config_T, ConfigField_T
from .constants import CONFIG_KEY

_T = TypeVar("_T")


@dataclass
class _ConfigMetadata:
    """Defines metadata for a config class."""

    title: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    schema_id: Optional[str] = field(default=None)
    schema_draft: Optional[str] = field(default=None)


@dataclass
class _ConfigFieldMetadata:
    """Defines metadata for a config field entry."""

    type: Optional[Type] = field(default=None)
    default: Any = field(default=None)
    name: Optional[str] = field(default=None)
    title: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    required: bool = field(default=True)
    examples: List[str] = field(default_factory=list)
    # NOTE: unfortunately until mypy supports recurisve types, it is pretty hard to have
    # a JsonSerializable type that these two callables would really benefit from.
    # https://github.com/python/typing/issues/182#issuecomment-629711850
    encoder: Optional[Callable[[Any], Any]] = field(default=None)
    decoder: Optional[Callable[[Any], Any]] = field(default=None)
    min: Optional[Union[int, float]] = field(default=None)
    max: Optional[Union[int, float]] = field(default=None)
    unique: bool = field(default=False)
    contains: List[Any] = field(default_factory=list)


@overload
def config(cls: None, **kwargs) -> Callable[[Type[_T]], Config_T[_T]]:
    ...


@overload
def config(cls: Type[_T], **kwargs) -> Config_T[_T]:
    ...


def config(
    cls: Optional[Type[_T]] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    schema_id: Optional[str] = None,
    schema_draft: Optional[str] = None,
    **kwargs,
) -> Union[Config_T[_T], Callable[[Type[_T]], Config_T[_T]]]:
    """File config class decorator.

    Use this function as a decorator on a classes that have config vars
    (using :func:`~var`) as class variables.

    Examples:
        >>> import file_config
        >>> @file_config.config(
                title="My Config Title",
                description="A description about my config"
            )
            class MyConfig:
                name: str = file_config.var()

    Args:
        cls (Optional[Type[_T]]):
            The class that should be decorated as a config.
            Defaults to None when this decorator is called with arguments.
        title (Optional[str]):
            A title for the config.
            Defaults to None.
        description (Optional[str]):
            A description of the config's purpose.
            Defaults to None.
        schema_id (Optional[str]):
            The JSONSchema ``$id`` to use when building the config's schema.
            Defaults to None.
        schema_draft (Optional[str]):
            The JSONSchema ``$schema`` to use when building the config's schema.
            Defaults to None.

    Returns:
        Union[Type[_T], Callable[[Type[_T]], Type[_T]]]:
            A config class that can be used for serialization.
    """

    def wrap(cls: Type[_T]) -> Type[_T]:
        """Wrap a given class as a config class.

        Applies various adjustments to the class definition that is required for
        understanding how to handle the class during serialization or schema buliding.

        Args:
            cls (Type[_T]):
                The class to wrap.

        Returns:
            Type[_T]:
                The newly wrapped class.
        """

        setattr(
            cls,
            CONFIG_KEY,
            _ConfigMetadata(
                title=title,
                description=description,
                schema_id=schema_id,
                schema_draft=schema_draft,
            ),
        )

        return dataclass(cls, **kwargs)

    # `cls` is set to None when the decorator is explicitly called during usage
    # (when users provide kwargs to the decorator). In this instance, we should return
    # the wrapping callable so the decorator can still be applied to the class
    return wrap if cls is None else wrap(cls)


def var(
    default: Any = CONFIG_FIELD_MISSING,
    name: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    # TODO: potentially we should deprecated required for CONIG_FIELD_MISSING usage
    # in the default. It is more in-line with dataclass syntax
    required: bool = True,
    examples: Optional[List[str]] = None,
    encoder: Optional[Callable[[Any], Any]] = None,
    decoder: Optional[Callable[[Any], Any]] = None,
    # If we wanted to be _less_ implicit with `min` and `max` we could introduce
    # `min_items` / `max_items` similar to what Pydantic does.
    min: Optional[Union[int, float]] = None,
    max: Optional[Union[int, float]] = None,
    unique: bool = False,
    contains: Optional[List[Any]] = None,
    **kwargs,
) -> ConfigField_T:
    """Config field definition function.

    Args:
        default (Any):
            The default value for the field if desired.
            Defaults to ``CONFIG_FIELD_MISSING`` which will prompt to raise an error
            when a value is not provided for the field during class instantitation.
        name (Optional[str]):
            A different name to use for this field during serialization.
            Defaults to None.
        title (Optional[str]):
            The schema title to use for this field.
            Defaults to None.
        description (Optional[str]):
            A schema description to use for this field.
            Defaults to None.
        required (bool):
            Whether to require this field during schema validation.
            May be deprecated in the future.
            Defaults to True.
        examples (Optional[List[str]]):
            A list of schema examples for this field.
            Defaults to None.
        encoder (Optional[Callable[[Any], Any]]):
            The encoder callable to use when serializing this field.
            Defaults to None.
        decoder (Optional[Callable[[Any], Any]]):
            The decoder callabe to use when deserializing this field.
            Defaults to None.
        min (Optional[Union[int, float]]):
            The minimum value to allow for the field during validation.
            What this value will validate against is still pretty implicit based on the
            type used for the field.
            Defaults to None.
        max (Optional[Union[int, float]]):
            The maximum value to allow for the field during validation.
            What this field will validate against is still pretty impicit based on the
            type used for the field.
            Defaults to None.
        unique (bool):
            Whether to ensure a unique values for this field.
            This only applies to iterable types.
            Defaults to False.
        contains (Optional[List[Any]]):
            What values to ensure that the field value contains.
            This only applies to iterable types.
            Defaults to None.

    Returns:
        ConfigField_T:
            A config field definition.
    """

    kwargs.update(default=default)
    return field(
        metadata={
            CONFIG_KEY: _ConfigFieldMetadata(
                default=default,
                name=name,
                title=title,
                description=description,
                required=required,
                examples=(examples if examples else []),
                encoder=encoder,
                decoder=decoder,
                min=min,
                max=max,
                unique=unique,
                contains=(contains if contains else []),
            )
        },
        **kwargs,
    )


def make_config(
    name: str,
    vars: Dict[str, ConfigField_T],
    title: Optional[str] = None,
    description: Optional[str] = None,
    schema_id: Optional[str] = None,
    schema_draft: Optional[str] = None,
    **kwargs,
) -> Config_T:

    return config(
        make_dataclass(name, fields=vars, **kwargs),
        title=title,
        description=description,
        schema_id=schema_id,
        schema_draft=schema_draft,
    )
