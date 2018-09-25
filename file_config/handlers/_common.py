# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import abc
import sys
import importlib
from typing import Any, List, TextIO


class BaseHandler(abc.ABC):

    @property
    def imported(self) -> Any:
        if not hasattr(self, "_imported"):
            self._imported = self._discover_import()
        return self._imported

    @property
    def handler(self) -> Any:
        if not hasattr(self, "_handler"):
            self._handler = sys.modules[self.imported]
        return self._handler

    @abc.abstractproperty
    def name(self) -> str:
        raise NotImplementedError(f"subclasses must implement 'name'")

    @abc.abstractproperty
    def packages(self) -> List[str]:
        raise NotImplementedError(f"subclasses must implement 'packages'")

    def _discover_import(self):
        for module_name in self.packages:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                sys.modules[module_name] = module
                imported_hook = getattr(self, f"on_{module_name}_imported", None)
                if callable(imported_hook):
                    imported_hook(sys.modules[module_name])
                return module_name
        raise ModuleNotFoundError(f"no modules in {self.packages!r} found")

    def dumps(self, instance: Any) -> Any:
        dumps_hook_name = f"on_{self.imported}_dumps"
        dumps_hook = getattr(self, dumps_hook_name, None)
        if not callable(dumps_hook):
            raise ValueError(
                f"no dumps handler for {self.imported!r}, requires method "
                f"{dumps_hook_name!r} in {self!r}"
            )
        return dumps_hook(self.handler, instance)

    def loads(self, content: Any) -> Any:
        loads_hook_name = f"on_{self.imported}_loads"
        loads_hook = getattr(self, loads_hook_name, None)
        if not callable(loads_hook):
            raise ValueError(
                f"no loads handler for {self.imported!r}, requires method "
                f"{loads_hook_name!r} in {self!r}"
            )
        return loads_hook(self.handler, content)

    def dump(self, instance: Any, file_object: TextIO):
        file_object.write(self.dumps(instance))

    def load(self, file_object: TextIO) -> Any:
        return self.loads(file_object.read())
