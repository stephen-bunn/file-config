# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import enum
import typing

import attr
import pytest
import jsonschema
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import characters

import file_config

from .strategies import config, config_var, config_var_dict, class_name


FIRST_LEVEL_IMPORTS = (
    "__version__",
    "config",
    "var",
    "validate",
    "to_dict",
    "from_dict",
    "build_schema",
    "make_config",
    "Regex",
    "CONFIG_KEY",
    "handlers",
    "contrib",
)


def test_signature():
    for importable in FIRST_LEVEL_IMPORTS:
        assert hasattr(file_config, importable)


@given(config())
def test_config(config):
    assert callable(config)
    assert callable(file_config.config(maybe_cls=None))
    assert file_config.utils.is_config_type(config)
    assert file_config.utils.is_config(config())
    assert hasattr(config, file_config.CONFIG_KEY)


@given(config_var())
def test_config_var(var):
    assert not callable(var)
    assert file_config.utils.is_config_var(var)
    assert file_config.CONFIG_KEY in var.metadata


@given(class_name(), config_var_dict(), characters(), characters())
def test_make_config(class_name, config_var_dict, title, description):
    config = file_config.make_config(
        class_name, config_var_dict, title=title, description=description
    )
    assert file_config.utils.is_config_type(config)
    assert file_config.utils.is_config(config())
    assert getattr(config, file_config.CONFIG_KEY).get("title") == title
    assert getattr(config, file_config.CONFIG_KEY).get("description") == description


def test_validate():
    @file_config.config
    class ConfigInstance:
        a = file_config.var(type=str, default="a")

    config_instance = ConfigInstance()
    # NOTE: validate returns nothing if nothing is wrong
    assert not file_config.validate(config_instance)

    config_instance.a = 1
    with pytest.raises(jsonschema.exceptions.ValidationError):
        file_config.validate(config_instance)


@given(config())
def test_from_dict(config):
    config_dict = file_config.to_dict(config())
    assert isinstance(file_config.from_dict(config, config_dict), config)


@given(config())
def test_to_dict(config):
    assert isinstance(file_config.to_dict(config()), dict)


@given(config())
def test_reflective(config):
    config_instance = config()
    config_dict = file_config.to_dict(config_instance)
    assert isinstance(config_dict, dict)
    new_instance = file_config.from_dict(config, config_dict)
    assert isinstance(new_instance, config)
    assert config_instance == new_instance


@given(class_name())
def test_custom_encoder_decoder(config_name):
    encoder = lambda x: f"x={x}"
    decoder = lambda x: x[2:]

    config = file_config.make_config(
        config_name, {"test": file_config.var(str, encoder=encoder, decoder=decoder)}
    )
    instance = config(test="test")
    encoded = file_config.to_dict(instance)
    assert encoded["test"] == "x=test"

    decoded = file_config.from_dict(config, encoded)
    assert decoded.test == "test"


@given(class_name())
def test_build_exceptions(config_name):
    with pytest.raises(ValueError):
        file_config._file_config._build(None, {})

    # test build validation
    config = file_config.make_config(config_name, {"test": file_config.var(str)})
    with pytest.raises(jsonschema.exceptions.ValidationError):
        file_config._file_config._build(config, {"test": 1}, validate=True)


def test_build_nested_array():
    @file_config.config
    class A:
        @file_config.config
        class B:
            bar = file_config.var(str)

        foo = file_config.var(typing.List[B])
        bar = file_config.var(typing.List[str])

    # test list of nested configs
    instance = file_config._file_config._build(
        A, {"foo": [{"bar": "test"}], "bar": ["test"]}
    )
    assert isinstance(instance, A)
    assert isinstance(instance.bar[0], str)
    assert instance.bar[0] == "test"
    assert isinstance(instance.foo[0], A.B)
    assert instance.foo[0].bar == "test"


def test_build_nested_object():
    @file_config.config
    class A:
        @file_config.config
        class B:
            bar = file_config.var(str)

        foo = file_config.var(typing.Dict[str, B])
        bar = file_config.var(typing.Dict[str, str])

    instance = file_config._file_config._build(
        A, {"foo": {"test": {"bar": "test"}}, "bar": {"test": "test"}}
    )
    assert isinstance(instance, A)
    assert isinstance(instance.bar, dict)
    assert instance.bar["test"] == "test"
    assert isinstance(instance.foo, dict)
    assert isinstance(instance.foo["test"], A.B)
    assert instance.foo["test"].bar == "test"


@given(class_name())
def test_dump_exceptions(config_name):
    with pytest.raises(ValueError):
        file_config._file_config._dump(None)


def test_dump_enum():
    class TestEnum(enum.Enum):
        A = 0
        B = 1

    @file_config.config
    class A:
        foo = file_config.var(TestEnum)

    instance = A(foo=TestEnum.A)
    dumped = file_config._file_config._dump(instance)
    assert dumped["foo"] == 0


def test_dump_nested_config():
    @file_config.config
    class A:
        @file_config.config
        class B:
            bar = file_config.var(str)

        foo = file_config.var(B)

    instance = A(foo=A.B(bar="test"))
    dumped = file_config._file_config._dump(instance)
    assert dumped["foo"]["bar"] == "test"
