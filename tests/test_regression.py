# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

from typing import Dict, List

import pytest
import file_config


def test_issue19():
    @file_config.config
    class Config(object):
        hooks = file_config.var(Dict[str, List[str]])

    file_config.build_schema(Config)


def test_config_read_from_file_keeps_defaults():
    from textwrap import dedent

    @file_config.config
    class TestConfig:
        foo = file_config.var(str, default="Default", required=False)
        bar = file_config.var(str, default="Default", required=False)

    yaml = dedent(
        """\
      foo: goofy
    """
    )

    json = dedent(
        """\
      {"foo": "goofy"}
    """
    )

    internal_cfg = TestConfig(foo="goofy")
    yaml_cfg = TestConfig.loads_yaml(yaml)
    json_cfg = TestConfig.loads_json(json)

    assert internal_cfg.foo == "goofy" and internal_cfg.bar == "Default"
    assert json_cfg.foo == "goofy" and json_cfg.bar == "Default"
    assert yaml_cfg.foo == "goofy" and yaml_cfg.bar == "Default"


def test_complex_config_deserialization_allows_nulls():
    from textwrap import dedent

    @file_config.config
    class TestConfig:
        @file_config.config
        class InnerConfig:
            foo = file_config.var(str, default="Default", required=False)

        inner = file_config.var(InnerConfig, required=False)
        bar = file_config.var(str, default="Default", required=False)

    yaml = dedent(
        """\
      bar: goofy
    """
    )

    yaml_cfg = TestConfig.loads_yaml(yaml)

    assert yaml_cfg.bar == "goofy"
    assert yaml_cfg.inner is None


def test_complex_config_deserialization_handles_inner_configs():
    from textwrap import dedent

    @file_config.config
    class TestConfig:
        @file_config.config
        class InnerConfig:
            foo = file_config.var(str, default="Default", required=False)

        inner = file_config.var(InnerConfig, required=False, default=InnerConfig)
        bar = file_config.var(str, default="Default", required=False)

    yaml = dedent(
        """\
        bar: goofy
    """
    )
    yaml_cfg = TestConfig.loads_yaml(yaml)

    assert yaml_cfg.bar == "goofy"
    assert yaml_cfg.inner is not None and isinstance(
        yaml_cfg.inner, TestConfig.InnerConfig
    )
    assert yaml_cfg.inner.foo == "Default"

