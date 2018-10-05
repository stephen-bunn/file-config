# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import abc
import sys
import importlib


class BaseHandler(abc.ABC):
    """ The base handler that all handlers should inherit from.
    """

    @property
    def imported(self):
        """ The imported handler module.

        :return: The imported handler module.
        :rtype: module
        """

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
        """ A unique name for the handler.

        .. note:: Handler names are used as the suffix of the dynamically set methods
            for all config instances.

        :raises NotImplementedError: Must be implemented by subclasses
        """

        raise NotImplementedError(f"subclasses must implement 'name'")

    @abc.abstractproperty
    def packages(self):
        """ A tuple of supported packages to use as handler modules.

        :raises NotImplementedError: Must be implemented by subclasses
        """

        raise NotImplementedError(f"subclasses must implement 'packages'")

    @classmethod
    def available(self):
        """ True if any of the supported modules from ``packages`` is available for use.

        :return: True if any modules from ``packages`` exist
        :rtype: bool
        """

        for module_name in self.packages:
            if importlib.util.find_spec(module_name):
                return True
        return False

    def _discover_import(self):
        """ Discovers and imports the best available module from ``packages``.

        :raises ModuleNotFoundError: If no module is available
        :return: The name of the module to use
        :rtype: str
        """

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
        """ An abstract dumps method which dumps an instance into the subclasses format.

        :param object instance: The instance to dump
        :raises ValueError: If dump handler does not provide handler method
        :return: The dumped content
        :rtype: str
        """

        dumps_hook_name = f"on_{self.imported}_dumps"
        dumps_hook = getattr(self, dumps_hook_name, None)
        if not callable(dumps_hook):
            raise ValueError(
                f"no dumps handler for {self.imported!r}, requires method "
                f"{dumps_hook_name!r} in {self!r}"
            )
        return dumps_hook(self.handler, instance)

    def loads(self, content):
        """ An abstract loads method which loads an instance from some content.

        :param str content: The content to load from
        :raises ValueError: If load handler does not provided handler method
        :return: A dictionary converted from the given content
        :rtype: dict
        """

        loads_hook_name = f"on_{self.imported}_loads"
        loads_hook = getattr(self, loads_hook_name, None)
        if not callable(loads_hook):
            raise ValueError(
                f"no loads handler for {self.imported!r}, requires method "
                f"{loads_hook_name!r} in {self!r}"
            )
        return loads_hook(self.handler, content)

    def dump(self, instance, file_object):
        """ An abstract method that dumps to a given file object.

        :param object instance: The instance to dump
        :param file file_object: The file object to dump to
        """

        file_object.write(self.dumps(instance))

    def load(self, file_object):
        """ An abstract method that loads from a given file object.

        :param file file_object: The file object to load from
        :returns: A dictionary converted from the content of the given file object
        :rtype: dict
        """

        return self.loads(file_object.read())
