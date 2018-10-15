# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class JSONHandler(BaseHandler):
    """ The JSON serialization handler.
    """

    name = "json"
    packages = ("ujson", "json")
    options = {"indent": 0, "sort_keys": False}

    def on_json_dumps(self, json, dictionary, **kwargs):
        """ The :mod:`json` dumps method.

        :param module json: The ``json`` module
        :param dict dictionary: The dictionary instance to serialize
        :param int indent: The amount of spaces to use for indentation,
            defaults to 0, optional
        :returns: The json serialization of the given ``dictionary``
        :rtype: str
        """

        return json.dumps(dictionary, **kwargs)

    def on_json_loads(self, json, content):
        """ The :mod:`json` loads method.

        :param module json: The ``json`` module
        :param str content: The content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return json.loads(content)

    def on_ujson_dumps(self, ujson, dictionary, **kwargs):
        """ The `ujson <https://pypi.org/project/ujson/>`_ dumps method.

        :param module ujson: The ``ujson`` module
        :param dict dictionary: The dictionary instance to serialize
        :param int indent: The amount of spaces to use for indentation,
            defaults to 0, optional
        :returns: The json serialization of the given ``dictionary``
        :rtype: str
        """

        return ujson.dumps(dictionary, **kwargs)

    def on_ujson_loads(self, ujson, content):
        """ The `ujson <https://pypi.org/project/ujson/>`_ loads method.

        :param module ujson: The ``ujson`` module
        :param str content: The content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return ujson.loads(content)
