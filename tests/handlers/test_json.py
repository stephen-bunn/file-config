# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

from hypothesis import given
from hypothesis.strategies import data

import file_config

from .. import config, builder


@given(config(), data())
def test_json_reflective(config, data):
    instance = data.draw(builder.build_config(config))
    content = instance.dumps_json(prefer="json")
    assert isinstance(content, str)
    new_instance = config.loads_json(content, prefer="json")
    assert isinstance(new_instance, config)
    assert new_instance == instance


@given(config(), data())
def test_rapidjson_reflective(config, data):
    instance = data.draw(builder.build_config(config))
    content = instance.dumps_json(prefer="rapidjson")
    assert isinstance(content, str)
    new_instance = config.loads_json(content, prefer="rapidjson")
    assert isinstance(new_instance, config)
    assert new_instance == instance
