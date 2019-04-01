# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import file_config
from hypothesis import given, settings

from ..strategies import config_instance


@settings(deadline=None)
@given(config_instance(allow_nan=False))
def test_json_reflective(instance):
    content = instance.dumps_json(prefer="json")
    assert isinstance(content, str)
    loaded = instance.__class__.loads_json(content)
    assert isinstance(loaded, instance.__class__)
    assert loaded == instance


@settings(deadline=None)
@given(config_instance(allow_nan=False))
def test_rapidjson_reflective(instance):
    content = instance.dumps_json(prefer="rapidjson")
    assert isinstance(content, str)
    loaded = instance.__class__.loads_json(content)
    assert isinstance(loaded, instance.__class__)
    assert loaded == instance
