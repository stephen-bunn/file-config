# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import typing
from textwrap import dedent

import file_config
import pytest
from hypothesis import given, settings

from ..strategies import config_instance


# testing config for testing dumping options
@file_config.config
class A:
    @file_config.config
    class B:
        bar = file_config.var(str)

    foo = file_config.var(str)
    bar = file_config.var(typing.Dict[str, B])


def test_toml_inline_tables():
    instance = A(foo="test", bar={"test": A.B(bar="test")})
    content = instance.dumps_toml(prefer="toml")
    assert isinstance(content, str)
    assert content == dedent(
        """\
        foo = "test"

        [bar.test]
        bar = "test"
        """
    )
    inline_content = instance.dumps_toml(prefer="toml", inline_tables=["bar.*"])
    assert isinstance(inline_content, str)
    assert inline_content == dedent(
        """\
        foo = "test"

        [bar]
        test = { bar = "test" }
        """
    )


def test_tomlkit_inline_tables():
    instance = A(foo="test", bar={"test": A.B(bar="test")})
    content = instance.dumps_toml(prefer="tomlkit")
    assert isinstance(content, str)
    assert content == dedent(
        """\
        foo = "test"

        [bar]
        [bar.test]
        bar = "test"
        """
    )
    inline_content = instance.dumps_toml(prefer="tomlkit", inline_tables=["bar.*"])
    assert isinstance(inline_content, str)
    assert inline_content == dedent(
        """\
        foo = "test"

        [bar]
        test = {bar = "test"}
        """
    )


def test_pytoml_inline_tables():
    instance = A(foo="test", bar={"test": A.B(bar="test")})
    content = instance.dumps_toml(prefer="pytoml")
    assert isinstance(content, str)
    assert content == dedent(
        """\
        foo = "test"

        [bar]

        [bar.test]
        bar = "test"
        """
    )

    with pytest.warns(UserWarning):
        instance.dumps_toml(prefer="pytoml", inline_tables=["bar.*"])
