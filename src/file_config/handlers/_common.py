# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

import abc
import sys
import warnings
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
        """ The current imported serialization handler module.

        :return: The imported handler
        :rtype: module
        """

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

    @abc.abstractproperty
    def options(self):
        """ A dictionary of dumping options that should be supported by the handler.

        :raises NotImplementedError: Must be implemented by subclasses
        """

        raise NotImplementedError(f"subclasses must implement 'options'")

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

    def _discover_import(self, prefer=None):
        """ Discovers and imports the best available module from ``packages``.

        :raises ModuleNotFoundError: If no module is available
        :return: The name of the module to use
        :rtype: str
        """

        available_packages = self.packages
        if isinstance(prefer, str):
            available_packages = (prefer,)

        for module_name in available_packages:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                importlib.import_module(module_name)
                imported_hook = getattr(self, f"on_{module_name}_imported", None)
                if callable(imported_hook):
                    imported_hook(sys.modules[module_name])
                return module_name
        raise ModuleNotFoundError(f"no modules in {available_packages!r} found")

    def _prefer_package(self, package):
        """ Prefer a serializtion handler over other handlers.

        :param str package: The name of the package to use
        :raises ValueError: When the given package name is not one of the available
            supported serializtion packages for this handler
        :return: The name of the serialization handler
        :rtype: str
        """

        if isinstance(package, str) and package != self.imported:
            if package not in self.packages:
                raise ValueError(
                    f"preferred package {package!r} does not exist, allowed are "
                    f"{self.packages!r}"
                )
            # clear out current serialization handler (if exists)
            if hasattr(self, "_handler"):
                del self._handler
            # manually update imported handlers with a given preference
            self._imported = self._discover_import(prefer=package)
            return package
        return self.imported

    def dumps(self, config, instance, prefer=None, **kwargs):
        """ An abstract dumps method which dumps an instance into the subclasses format.

        :param class config: The config class of the instance
        :param object instance: The instance to dump
        :param str prefer: The preferred serialization module name
        :raises ValueError: If dump handler does not provide handler method
        :return: The dumped content
        :rtype: str
        """

        dumper = self._prefer_package(prefer)
        dumps_hook_name = f"on_{dumper}_dumps"
        dumps_hook = getattr(self, dumps_hook_name, None)
        if not callable(dumps_hook):
            raise ValueError(
                f"no dumps handler for {self.imported!r}, requires method "
                f"{dumps_hook_name!r} in {self!r}"
            )

        extras = self.options.copy()
        for (key, value) in kwargs.items():
            if key not in extras.keys():
                warnings.warn(
                    f"handler 'dumps_{self.name!s}' does not support {key!r} argument"
                )
            else:
                extras[key] = value
        return dumps_hook(self.handler, config, instance, **extras)

    def loads(self, config, content, prefer=None):
        """ An abstract loads method which loads an instance from some content.

        :param class config: The config class to load into
        :param str content: The content to load from
        :param str prefer: The preferred serialization module name
        :raises ValueError: If load handler does not provided handler method
        :return: A dictionary converted from the given content
        :rtype: dict
        """

        loader = self._prefer_package(prefer)
        loads_hook_name = f"on_{loader}_loads"
        loads_hook = getattr(self, loads_hook_name, None)
        if not callable(loads_hook):
            raise ValueError(
                f"no loads handler for {self.imported!r}, requires method "
                f"{loads_hook_name!r} in {self!r}"
            )
        return loads_hook(self.handler, config, content)

    def dump(self, config, instance, file_object, prefer=None, **kwargs):
        """ An abstract method that dumps to a given file object.

        :param class config: The config class of the instance
        :param object instance: The instance to dump
        :param file file_object: The file object to dump to
        :param str prefer: The preferred serialization module name
        """

        file_object.write(self.dumps(config, instance, prefer=prefer, **kwargs))

    def load(self, config, file_object, prefer=None):
        """ An abstract method that loads from a given file object.

        :param class config: The config class to load into
        :param file file_object: The file object to load from
        :param str prefer: The preferred serialization module name
        :returns: A dictionary converted from the content of the given file object
        :rtype: dict
        """

        return self.loads(config, file_object.read(), prefer=prefer)
