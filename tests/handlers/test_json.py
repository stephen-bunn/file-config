# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

from hypothesis import given

from ..strategies import config


@given(config())
def test_json_reflective(config):
    config_instance = config()
    json_content = config_instance.dumps_json()
    assert isinstance(json_content, str)
    new_instance = config.loads_json(json_content)
    assert isinstance(new_instance, config)
    assert new_instance == config_instance
