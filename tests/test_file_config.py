# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import attr
import pytest
import jsonschema
from hypothesis import given
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
