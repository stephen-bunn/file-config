# Stubs for file_config.handlers.json (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from ._common import BaseHandler
from typing import Any

class JSONHandler(BaseHandler):
    name: str = ...
    packages: Any = ...
    options: Any = ...
    def on_json_dumps(self, json: Any, config: Any, dictionary: Any, **kwargs: Any): ...
    def on_json_loads(self, json: Any, config: Any, content: Any, **kwargs: Any): ...
    def on_ujson_dumps(self, ujson: Any, config: Any, dictionary: Any, **kwargs: Any): ...
    def on_ujson_loads(self, ujson: Any, config: Any, content: Any, **kwargs: Any): ...
    def on_rapidjson_dumps(self, rapidjson: Any, config: Any, dictionary: Any, **kwargs: Any): ...
    def on_rapidjson_loads(self, rapidjson: Any, config: Any, content: Any, **kwargs: Any): ...