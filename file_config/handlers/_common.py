# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import abc
import sys
import importlib


class BaseHandler(abc.ABC):
    @property
    def imported(self):
        if not hasattr(self, "_imported"):
            self._imported = self._discover_import()
        return self._imported

    @property
    def handler(self):
        if not hasattr(self, "_handler"):
            self._handler = sys.modules[self.imported]
        return self._handler

    @abc.abstractproperty
    def name(self):
        raise NotImplementedError(f"subclasses must implement 'name'")

    @abc.abstractproperty
    def packages(self):
        raise NotImplementedError(f"subclasses must implement 'packages'")

    @classmethod
    def available(self):
        for module_name in self.packages:
            if importlib.util.find_spec(module_name):
                return True
        return False

    def _discover_import(self):
        for module_name in self.packages:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                importlib.import_module(module_name)
                imported_hook = getattr(self, f"on_{module_name}_imported", None)
                if callable(imported_hook):
                    imported_hook(sys.modules[module_name])
                return module_name
        raise ModuleNotFoundError(f"no modules in {self.packages!r} found")

    def dumps(self, instance):
        dumps_hook_name = f"on_{self.imported}_dumps"
        dumps_hook = getattr(self, dumps_hook_name, None)
        if not callable(dumps_hook):
            raise ValueError(
                f"no dumps handler for {self.imported!r}, requires method "
                f"{dumps_hook_name!r} in {self!r}"
            )
        return dumps_hook(self.handler, instance)

    def loads(self, content):
        loads_hook_name = f"on_{self.imported}_loads"
        loads_hook = getattr(self, loads_hook_name, None)
        if not callable(loads_hook):
            raise ValueError(
                f"no loads handler for {self.imported!r}, requires method "
                f"{loads_hook_name!r} in {self!r}"
            )
        return loads_hook(self.handler, content)

    def dump(self, instance, file_object):
        file_object.write(self.dumps(instance))

    def load(self, file_object):
        return self.loads(file_object.read())
