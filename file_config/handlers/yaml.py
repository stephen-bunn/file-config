# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from collections import OrderedDict

from ._common import BaseHandler


class YAMLHandler(BaseHandler):
    """ The YAML serialization handler.
    """

    name = "yaml"
    packages = ("yaml",)

    def on_yaml_imported(self, yaml):
        """ The `pyyaml <https://pypi.org/project/pyyaml/>`_ import hook.
        """

        def represent_ordereddict(dumper, data):
            """ A custom data representer for ``OrderedDict`` instances.

            .. note:: Credit to https://stackoverflow.com/a/16782282/7828560.

            :param object dumper: The dumper object
            :param collections.OrderedDict data: The ``OrderedDict`` instance
            :return: The yaml mapping node
            :rtype: yaml.MappingNode
            """

            values = []
            for (key, value) in data.items():
                values.append(
                    (dumper.represent_data(key), dumper.represent_data(value))
                )
            return yaml.MappingNode("tag:yaml.org,2002:map", values)

        yaml.add_representer(OrderedDict, represent_ordereddict)

    def on_yaml_dumps(self, yaml, instance):
        """ The `pyyaml <https://pypi.org/project/pyyaml/>`_ dumps method.
        """

        return yaml.dump(instance)

    def on_yaml_loads(self, yaml, content):
        """ The `pyyaml <https://pypi.org/project/pyyaml/>`_ loads method.
        """

        return yaml.load(content)
