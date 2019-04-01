# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import io
from textwrap import dedent
from collections import OrderedDict

import file_config
from hypothesis import given, settings
from hypothesis.strategies import characters, integers, booleans, floats, none

from ..strategies import config_instance


@settings(deadline=None)
@given(config_instance(allow_nan=False))
def test_yaml_reflective(instance):
    content = instance.dumps_yaml(prefer="yaml")
    assert isinstance(content, str)
    loaded = instance.__class__.loads_yaml(content)
    assert isinstance(loaded, instance.__class__)
    assert loaded == instance

    fake_io = io.StringIO()
    instance.dump_yaml(fake_io, prefer="yaml")
    fake_io.seek(0)

    loaded = instance.__class__.load_yaml(fake_io)
    assert loaded == instance


def test_yaml_ordereddict():
    @file_config.config
    class A:
        foo = file_config.var(OrderedDict)

    instance = A(foo=OrderedDict([("test", "test")]))
    content = instance.dumps_yaml()
    assert content == dedent(
        """\
        foo:
          test: test
    """
    )
