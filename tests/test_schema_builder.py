# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import enum

import typing
import pytest
from hypothesis import given, settings
from hypothesis.strategies import characters

import file_config
from .strategies import config, builtins, class_name, variable_name


@given(config(min_vars=0, max_vars=0))
def test_empty_config(config):
    schema = file_config.build_schema(config)
    assert schema["type"] == "object"
    assert len(schema["properties"]) == 0
    assert len(schema["required"]) == 0


@given(builtins())
def test_not_config(config):
    with pytest.raises(ValueError):
        file_config.build_schema(config)


def test_not_var():
    with pytest.raises(ValueError):
        file_config.schema_builder._build_var(None)


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


@given(class_name(), characters(), characters(), characters())
def test_var_metadata(config_name, title, description, example):
    config = file_config.make_config(
        config_name,
        {
            "test": file_config.var(
                title=title, description=description, examples=[example]
            )
        },
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["title"] == title
    assert schema["properties"]["test"]["description"] == description
    assert "examples" in schema["properties"]["test"]

    examples = schema["properties"]["test"]["examples"]
    assert isinstance(examples, list)
    assert len(examples) == 1
    assert examples[0] == example


@given(class_name(), variable_name(), config(config_vars={}))
def test_nested_empty_config(config_name, nested_config_name, nested_config):
    config = file_config.make_config(
        config_name, {nested_config_name: file_config.var(nested_config)}
    )
    schema = file_config.build_schema(config)
    assert len(schema["properties"]) == 1
    assert len(schema["required"]) == 1
    nested_config_schema = schema["properties"][nested_config_name]
    assert nested_config_schema["type"] == "object"
    assert len(nested_config_schema["properties"]) == 0
    assert len(nested_config_schema["required"]) == 0


@given(class_name())
def test_string_var(config_name):
    type_ = str
    schema = file_config.schema_builder._build_string_type(type_)
    assert schema["type"] == "string"

    config = file_config.make_config(config_name, {"test": file_config.var(type_)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "string"

    config = file_config.make_config(
        config_name, {"test": file_config.var(type_, min=0, max=1)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["minLength"] == 0
    assert schema["properties"]["test"]["maxLength"] == 1

    for key, value in (("unique", True), ("contains", 1)):
        config = file_config.make_config(
            config_name, {"test": file_config.var(type_, **{key: value})}
        )

        with pytest.warns(UserWarning):
            file_config.build_schema(config)


@given(class_name())
def test_regex_var(config_name):
    type_ = file_config.Regex(r"test")
    schema = file_config.schema_builder._build_string_type(type_)
    assert schema["type"] == "string"
    assert schema["pattern"] == "test"

    config = file_config.make_config(config_name, {"test": file_config.var(type_)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "string"
    assert "pattern" in schema["properties"]["test"]
    assert schema["properties"]["test"]["pattern"] == "test"

    config = file_config.make_config(
        config_name, {"test": file_config.var(type_, min=0, max=1)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["minLength"] == 0
    assert schema["properties"]["test"]["maxLength"] == 1

    for key, value in (("unique", True), ("contains", 1)):
        config = file_config.make_config(
            config_name, {"test": file_config.var(type_, **{key: value})}
        )

        with pytest.warns(UserWarning):
            file_config.build_schema(config)


@given(class_name())
def test_integer_var(config_name):
    type_ = int
    schema = file_config.schema_builder._build_integer_type(type_)
    assert schema["type"] == "integer"

    config = file_config.make_config(config_name, {"test": file_config.var(type_)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "integer"

    config = file_config.make_config(
        config_name, {"test": file_config.var(type_, min=0, max=1)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["minimum"] == 0
    assert schema["properties"]["test"]["maximum"] == 1

    for key, value in (("unique", True), ("contains", 1)):
        config = file_config.make_config(
            config_name, {"test": file_config.var(type_, **{key: value})}
        )

        with pytest.warns(UserWarning):
            file_config.build_schema(config)


@given(class_name())
def test_number_var(config_name):
    type_ = float
    schema = file_config.schema_builder._build_number_type(type_)
    assert schema["type"] == "number"

    config = file_config.make_config(config_name, {"test": file_config.var(type_)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "number"

    config = file_config.make_config(
        config_name, {"test": file_config.var(type_, min=1.0, max=1.1)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["minimum"] == 1.0
    assert schema["properties"]["test"]["maximum"] == 1.1

    for key, value in (("unique", True), ("contains", 1)):
        config = file_config.make_config(
            config_name, {"test": file_config.var(type_, **{key: value})}
        )

        with pytest.warns(UserWarning):
            file_config.build_schema(config)


@given(class_name())
def test_enum_var(config_name):
    class IntTestEnum(enum.Enum):
        A = 0
        B = 1

    class StrTestEnum(enum.Enum):
        A = "0"
        B = "1"

    class FloatTestEnum(enum.Enum):
        A = 0.0
        B = 1.0

    config = file_config.make_config(
        config_name, {"test": file_config.var(IntTestEnum)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "integer"
    assert "enum" in schema["properties"]["test"]
    assert [0, 1] == schema["properties"]["test"]["enum"]

    config = file_config.make_config(
        config_name, {"test": file_config.var(StrTestEnum)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "string"
    assert "enum" in schema["properties"]["test"]
    assert ["0", "1"] == schema["properties"]["test"]["enum"]

    config = file_config.make_config(
        config_name, {"test": file_config.var(FloatTestEnum)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "number"
    assert "enum" in schema["properties"]["test"]
    assert [0.0, 1.0] == schema["properties"]["test"]["enum"]


@given(class_name())
def test_bool_var(config_name):
    type_ = bool
    assert file_config.schema_builder._build_bool_type(type_)["type"] == "boolean"
    config = file_config.make_config(config_name, {"test": file_config.var(bool)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "boolean"


@given(class_name())
def test_null_var(config_name):
    type_ = type(None)
    assert file_config.schema_builder._build_null_type(type_)["type"] == "null"
    config = file_config.make_config(config_name, {"test": file_config.var(type_)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "null"


@given(class_name())
def test_array_var(config_name):
    schema = file_config.schema_builder._build_array_type(list)
    assert schema["type"] == "array"

    config = file_config.make_config(config_name, {"test": file_config.var(list)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "array"
    assert "items" in schema["properties"]["test"]

    config = file_config.make_config(
        config_name, {"test": file_config.var(typing.List[str])}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "array"
    assert "items" in schema["properties"]["test"]
    assert schema["properties"]["test"]["items"]["type"] == "string"

    config = file_config.make_config(
        config_name,
        {"test": file_config.var(list, min=0, max=1, unique=True, contains=["1"])},
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["minItems"] == 0
    assert schema["properties"]["test"]["maxItems"] == 1
    assert schema["properties"]["test"]["uniqueItems"] == True
    assert schema["properties"]["test"]["contains"] == ["1"]


@given(class_name())
def test_object_var(config_name):
    schema = file_config.schema_builder._build_object_type(dict)
    assert schema["type"] == "object"

    config = file_config.make_config(config_name, {"test": file_config.var(dict)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "object"

    config = file_config.make_config(
        config_name,
        {"test": file_config.var(typing.Dict[file_config.Regex(r"test"), int])},
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "object"
    assert "test" in schema["properties"]["test"]["patternProperties"]
    assert (
        schema["properties"]["test"]["patternProperties"]["test"]["type"] == "integer"
    )

    config = file_config.make_config(
        config_name, {"test": file_config.var(dict, min=0, max=1)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["minProperties"] == 0
    assert schema["properties"]["test"]["maxProperties"] == 1

    with pytest.raises(ValueError):
        config = file_config.make_config(
            config_name, {"test": file_config.var(typing.Dict[int, int])}
        )
        file_config.build_schema(config)


@given(class_name())
def test_union_var(config_name):
    config = file_config.make_config(
        config_name, {"test": file_config.var(typing.Union[str, int])}
    )
    schema = file_config.build_schema(config)
    assert "anyOf" in schema["properties"]["test"]
    assert isinstance(schema["properties"]["test"]["anyOf"], list)
    assert len(schema["properties"]["test"]["anyOf"]) == 2
    assert schema["properties"]["test"]["anyOf"][0]["type"] == "string"
    assert schema["properties"]["test"]["anyOf"][-1]["type"] == "integer"


def test_unhandled_types():
    for unhandled_type in (complex,):
        with pytest.warns(UserWarning):
            file_config.schema_builder._build_type(unhandled_type, None)


@given(class_name())
def test_var_modifier_exceptions(config_name):
    with pytest.raises(ValueError):
        file_config.schema_builder._build_attribute_modifiers(None, {})

    config = file_config.make_config(config_name, {"test": file_config.var(str, min=True)})
    with pytest.raises(ValueError):
        file_config.build_schema(config)

def test_generic_build():
    config = file_config.make_config("A", {"test": file_config.var(str)})
    # build schema for config instance
    schema = file_config.schema_builder._build(config)
    assert schema["type"] == "object"
    assert "required" in schema

    # build schema for instance var
    # TODO: potentially support config var (non-instance)?
    instance = config(test="test")
    schema = file_config.schema_builder._build(instance.test)
    assert schema["type"] == "string"

    # build schema for builtin
    schema = file_config.schema_builder._build(str)
    assert schema["type"] == "string"

    # build schema for regex
    schema = file_config.schema_builder._build(file_config.Regex(r"test"))
    assert schema["type"] == "string"
    assert schema["pattern"] == "test"

    # build schema for arbitrary value
    schema = file_config.schema_builder._build("test")
    assert schema["type"] == "string"