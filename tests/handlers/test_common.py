# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import uuid

import pytest
from hypothesis import given, settings

import file_config
from file_config.handlers._common import BaseHandler

from ..strategies import config_instance


def test_handler_invalid():
    class A(BaseHandler):
        pass

    class B(BaseHandler):
        name = "test"
        packages = ("6ae1bdca-4a3d-4f58-bc9e-a389b3a56d48",)
        options = {}

    # requires abstract methods for handlers
    with pytest.raises(TypeError):
        A()

    # rquires given packages to exist on usage
    with pytest.raises(ModuleNotFoundError):
        B()._discover_import()
    assert not B.available()


@settings(deadline=None)
@given(config_instance(allow_nan=False))
def test_handler_exceptions(instance):
    class A(BaseHandler):
        name = "tes"
        packages = ("json",)
        options = {}

    # make sure given preferred packages are in handler.packages
    with pytest.raises(ValueError):
        A()._prefer_package(uuid.uuid4().hex)

    # requires on_json_dumps
    with pytest.raises(ValueError):
        A().dumps(instance.__class__, file_config.to_dict(instance))

    # requires on_json_loads
    with pytest.raises(ValueError):
        A().loads(instance.__class__, "{}")

    # raise warning when unhandled format options are given
    with pytest.warns(UserWarning):
        file_config.handlers.json.JSONHandler().dumps(
            instance.__class__,
            file_config.to_dict(instance),
            unhandled_format_option=None,
        )
