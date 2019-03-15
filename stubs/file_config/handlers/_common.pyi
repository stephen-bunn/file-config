# Stubs for file_config.handlers._common (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

import abc
from typing import Any, Optional

class BaseHandler(abc.ABC, metaclass=abc.ABCMeta):
    @property
    _imported: Any = ...
    def imported(self): ...
    @property
    _handler: Any = ...
    def handler(self): ...
    def name(self) -> Any: ...
    def packages(self) -> Any: ...
    def options(self) -> Any: ...
    @classmethod
    def available(self): ...
    def _discover_import(self): ...
    packages: Any = ...
    def _prefer_package(self, package: Any) -> None: ...
    def dumps(self, config: Any, instance: Any, prefer: Optional[Any] = ..., **kwargs: Any): ...
    def loads(self, config: Any, content: Any, prefer: Optional[Any] = ...): ...
    def dump(self, config: Any, instance: Any, file_object: Any, prefer: Optional[Any] = ..., **kwargs: Any) -> None: ...
    def load(self, config: Any, file_object: Any, prefer: Optional[Any] = ...): ...
