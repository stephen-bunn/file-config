# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import enum

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


@given(class_name(), characters(), characters())
def test_var_metadata(config_name, title, description):
    config = file_config.make_config(
        config_name, {"test": file_config.var(title=title, description=description)}
    )
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["title"] == title
    assert schema["properties"]["test"]["description"] == description


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

        config = file_config.make_config(
            config_name, {"test": file_config.var(type_, min=0, max=1)}
        )
        schema = file_config.build_schema(config)
        assert schema["properties"]["test"]["minimum"] == 0
        assert schema["properties"]["test"]["maximum"] == 1

        # warning on unique modifier
        with pytest.warns(UserWarning):
            config = file_config.make_config(
                config_name, {"test": file_config.var(type_, unique=True)}
            )
            schema = file_config.build_schema(config)

        # warning on contains modifier
        with pytest.warns(UserWarning):
            config = file_config.make_config(
                config_name, {"test": file_config.var(type_, contains=1)}
            )
            schema = file_config.build_schema(config)


@given(class_name())
def test_number_var(config_name):
    for type_ in (float,):
        config = file_config.make_config(config_name, {"test": file_config.var(type_)})
        schema = file_config.build_schema(config)
        assert schema["properties"]["test"]["type"] == "number"

        # modifiers
        config = file_config.make_config(
            config_name, {"test": file_config.var(type_, min=1.0, max=1.1)}
        )
        schema = file_config.build_schema(config)
        assert schema["properties"]["test"]["minimum"] == 1.0
        assert schema["properties"]["test"]["maximum"] == 1.1

        # warning on unique modifier
        with pytest.warns(UserWarning):
            config = file_config.make_config(
                config_name, {"test": file_config.var(type_, unique=True)}
            )
            schema = file_config.build_schema(config)

        # warning on contains modifier
        with pytest.warns(UserWarning):
            config = file_config.make_config(
                config_name, {"test": file_config.var(type_, contains=1)}
            )
            schema = file_config.build_schema(config)


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
    assert file_config.schema_builder._build_bool_type(bool)["type"] == "boolean"
    config = file_config.make_config(config_name, {"test": file_config.var(bool)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "boolean"


@given(class_name())
def test_null_var(config_name):
    null_type = type(None)
    assert file_config.schema_builder._build_null_type(null_type)["type"] == "null"
    config = file_config.make_config(config_name, {"test": file_config.var(null_type)})
    schema = file_config.build_schema(config)
    assert schema["properties"]["test"]["type"] == "null"

