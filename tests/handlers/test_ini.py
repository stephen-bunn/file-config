# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import typing
from textwrap import dedent

import pytest
import file_config
from hypothesis import given
from hypothesis.strategies import from_regex


@file_config.config
class A:
    @file_config.config
    class B:
        bar = file_config.var(str)

    foo = file_config.var(str)
    bar = file_config.var(B)


@given(from_regex(r"\A[a-zA-Z]\Z", fullmatch=True))
def test_ini_root(root):
    instance = A(foo="test", bar=A.B(bar="test"))
    content = instance.dumps_ini(root=root)
    assert content[1 : len(root) + 1] == root


def test_ini_delimiter():
    instance = A(foo="test", bar=A.B(bar="test"))
    content = instance.dumps_ini(delimiter="-")
    assert content.split("\n")[3] == "[A:bar]"

    with pytest.warns(UserWarning):
        instance.dumps_ini(delimiter="-", root="test-root")


def test_ini_exceptions():
    @file_config.config
    class Alpha:
        foo = file_config.var(typing.List[dict])

    instance = Alpha(foo=[{"test": "test"}])
    with pytest.raises(ValueError):
        instance.dumps_ini()
