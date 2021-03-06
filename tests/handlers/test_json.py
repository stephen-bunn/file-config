# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import io

from hypothesis import given, settings
from hypothesis.strategies import text, booleans, characters

import file_config

from ..strategies import config_instance


@settings(deadline=None)
@given(config_instance(allow_nan=False))
def test_json_reflective(instance):
    content = instance.dumps_json(prefer="json")
    assert isinstance(content, str)
    loaded = instance.__class__.loads_json(content)
    assert isinstance(loaded, instance.__class__)
    assert loaded == instance

    fake_io = io.StringIO()
    instance.dump_json(fake_io, prefer="json")
    fake_io.seek(0)

    loaded = instance.__class__.load_json(fake_io)
    assert loaded == instance


@settings(deadline=None)
@given(config_instance(allow_nan=False))
def test_rapidjson_reflective(instance):
    content = instance.dumps_json(prefer="rapidjson")
    assert isinstance(content, str)
    loaded = instance.__class__.loads_json(content)
    assert isinstance(loaded, instance.__class__)
    assert loaded == instance

    fake_io = io.StringIO()
    instance.dump_json(fake_io, prefer="rapidjson")
    fake_io.seek(0)

    loaded = instance.__class__.load_json(fake_io)
    assert loaded == instance


@settings(deadline=None)
@given(config_instance(allowed_strategies=[characters(), text(), booleans()]))
def test_ujson_reflective(instance):
    content = instance.dumps_json(prefer="ujson")
    assert isinstance(content, str)
    loaded = instance.__class__.loads_json(content)
    assert isinstance(loaded, instance.__class__)
    assert loaded == instance

    fake_io = io.StringIO()
    instance.dump_json(fake_io, prefer="ujson")
    fake_io.seek(0)

    loaded = instance.__class__.load_json(fake_io)
    assert loaded == instance
