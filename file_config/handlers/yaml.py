# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from collections import OrderedDict

from ._common import BaseHandler


class YAMLHandler(BaseHandler):

    name = "yaml"
    packages = ("yaml",)

    def on_yaml_imported(self, yaml):
        def represent_ordereddict(dumper, data):
            """ A custom data representer for ``OrderedDict`` instances.

            .. note:: Credit to https://stackoverflow.com/a/16782282/7828560.

            :param dumper: The dumper object
            :type dumper: object
            :param data: The ``OrderedDict`` instance
            :type data: OrderedDict
            :return: The yaml mapping node
            :rtype: yaml.nodes.MappingNode
            """

            values = []
            for (key, value) in data.items():
                values.append(
                    (dumper.represent_data(key), dumper.represent_data(value))
                )
            return yaml.MappingNode("tag:yaml.org,2002:map", values)

        yaml.add_representer(OrderedDict, represent_ordereddict)

    def on_yaml_dumps(self, yaml, instance):
        return yaml.dump(instance)

    def on_yaml_loads(self, yaml, content):
        return yaml.load(content)
