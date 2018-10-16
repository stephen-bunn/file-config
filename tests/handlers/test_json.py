# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import json
import ujson

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
