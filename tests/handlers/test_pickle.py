# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import file_config
from hypothesis import given, settings

from ..strategies import config_instance


@settings(deadline=None)
@given(config_instance(allow_nan=False))
def test_pickle_reflective(instance):
    content = instance.dumps_pickle()
    assert isinstance(content, bytes)
    loaded = instance.__class__.loads_pickle(content)
    assert isinstance(loaded, instance.__class__)
    assert loaded == instance
