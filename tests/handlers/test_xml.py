# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

from textwrap import dedent

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
def test_xml_root(root):
    instance = A(foo="test", bar=A.B(bar="test"))
    content = instance.dumps_xml(root=root)
    assert content[1 : len(root) + 1] == root


def test_xml_declaration():
    instance = A(foo="test", bar=A.B(bar="test"))
    content = instance.dumps_xml(xml_declaration=True)
    assert content.split("\n")[0] == "<?xml version='1.0' encoding='UTF-8'?>"

    content = instance.dumps_xml(xml_declaration=True, encoding="ASCII")
    assert content.split("\n")[0] == "<?xml version='1.0' encoding='ASCII'?>"


def test_xml_pretty():
    instance = A(foo="test", bar=A.B(bar="test"))
    content = instance.dumps_xml(pretty=True)
    assert content == dedent(
        """\
        <A>
          <foo type="str">test</foo>
          <bar>
            <bar type="str">test</bar>
          </bar>
        </A>
    """
    )
