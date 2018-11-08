# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

import json

from hypothesis import given
from hypothesis.strategies import data

import file_config

from .. import config, builder


@given(config(), data())
def test_json_dumps(config, data):
    instance = data.draw(builder.build_config(config))
    json_content = instance.dumps_json(prefer="json")
    assert isinstance(json_content, str)
    json.loads(json_content)


@given(config(), data())
def test_json_loads(config, data):
    instance = data.draw(builder.build_config(config))
    json_content = instance.dumps_json(prefer="json")
    new_instance = config.loads_json(json_content, prefer="json")
    assert isinstance(new_instance, config)
