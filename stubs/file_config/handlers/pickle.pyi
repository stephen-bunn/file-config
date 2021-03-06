# Stubs for file_config.handlers.pickle (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from ._common import BaseHandler
from typing import Any

class PickleHandler(BaseHandler):
    name: str = ...
    packages: Any = ...
    options: Any = ...
    def on_pickle_dumps(self, pickle: Any, config: Any, dictionary: Any, **kwargs: Any): ...
    def on_pickle_loads(self, pickle: Any, config: Any, content: Any, **kwargs: Any): ...
