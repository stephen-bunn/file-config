# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import io

import attr
from hypothesis import given, assume, settings
from hypothesis.strategies import integers

import file_config

from ..strategies import config_instance


@settings(deadline=None)
@given(config_instance(allow_nan=False))
def test_msgpack_reflective(instance):
    for arg in instance.__attrs_attrs__:
        instance_arg = getattr(instance, arg.name)
        if isinstance(instance_arg, int):
            # deal with message pack limitations in integer limits
            assume(instance_arg >= -(2 ** 64) and instance_arg <= (2 ** 64) - 1)

    content = instance.dumps_msgpack(prefer="msgpack")
    assert isinstance(content, bytes)
    loaded = instance.__class__.loads_msgpack(content)
    assert isinstance(loaded, instance.__class__)
    assert loaded == instance

    fake_io = io.BytesIO()
    instance.dump_msgpack(fake_io, prefer="msgpack")
    fake_io.seek(0)

    loaded = instance.__class__.load_msgpack(fake_io)
    assert loaded == instance
