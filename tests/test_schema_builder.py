# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from hypothesis import given
from hypothesis.strategies import characters

import file_config
from . import config, class_name


@given(config(min_vars=0, max_vars=0))
def test_empty_config(config):
    schema = file_config.build_schema(config)
    assert schema["type"] == "object"
    assert len(schema["properties"]) == 0
    assert len(schema["required"]) == 0


@given(class_name(), characters(), characters())
def test_config_metadata(config_name, title, description):
    config = file_config.make_config(
        config_name, {}, title=title, description=description
    )
    schema = file_config.build_schema(config)
    assert schema["title"] == title
    assert schema["description"] == description


@given(class_name())
def test_empty_var(config_name):
    config = file_config.make_config(config_name, {"test": file_config.var()})
    schema = file_config.build_schema(config)
    assert len(schema["properties"]) == 1
    assert len(schema["required"]) == 1
    assert "test" in schema["properties"]
    assert "type" not in schema["properties"]["test"]


@given(config(config_vars={"test": file_config.var(required=False)}))
def test_optional_var(config):
    schema = file_config.build_schema(config)
    assert len(schema["properties"]) == 1
    assert len(schema["required"]) == 0
    assert "test" in schema["properties"]
    assert "type" not in schema["properties"]["test"]


@given(class_name(), characters())
def test_var_title(config_name, title):
    config = file_config.make_config(
        config_name, {"test": file_config.var(title=title)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["title"] == title


@given(class_name(), characters())
def test_var_description(config_name, description):
    config = file_config.make_config(
        config_name, {"test": file_config.var(description=description)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["description"] == description


@given(class_name())
def test_string_var(config_name):
    for type_ in (str,):
        config = file_config.make_config(config_name, {"test": file_config.var(type_)})
        schema = file_config.build_schema(config)
        assert schema["properties"]["test"]["type"] == "string"


@given(class_name())
def test_integer_var(config_name):
    for type_ in (int,):
        config = file_config.make_config(config_name, {"test": file_config.var(type_)})
        schema = file_config.build_schema(config)
        assert schema["properties"]["test"]["type"] == "integer"


@given(class_name())
def test_number_var(config_name):
    for type_ in (float, complex):
        config = file_config.make_config(config_name, {"test": file_config.var(type_)})
        schema = file_config.build_schema(config)
        assert schema["properties"]["test"]["type"] == "number"
