# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

from collections import OrderedDict

from ._common import BaseHandler


class YAMLHandler(BaseHandler):
    """ The YAML serialization handler.
    """

    name = "yaml"
    packages = ("yaml",)
    options = {}

    def on_yaml_imported(self, yaml):
        """ The `pyyaml <https://pypi.org/project/pyyaml/>`_ import hook.

        :param module yaml: The ``yaml`` module
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

    def on_yaml_dumps(self, yaml, config, dictionary, **kwargs):
        """ The `pyyaml <https://pypi.org/project/pyyaml/>`_ dumps method.

        :param module yaml: The ``yaml`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary to seralize
        :returns: The serialized content
        :rtype: str
        """

        return yaml.dump(dictionary)

    def on_yaml_loads(self, yaml, config, content, **kwargs):
        """ The `pyyaml <https://pypi.org/project/pyyaml/>`_ loads method.

        :param module yaml: The ``yaml`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return yaml.load(content)
