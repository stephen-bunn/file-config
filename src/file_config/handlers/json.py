# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

from ._common import BaseHandler


class JSONHandler(BaseHandler):
    """ The JSON serialization handler.
    """

    name = "json"
    packages = ("rapidjson", "ujson", "json")
    options = {"indent": None, "sort_keys": False}

    def on_json_dumps(self, json, config, dictionary, **kwargs):
        """ The :mod:`json` dumps method.

        :param module json: The ``json`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary instance to serialize
        :param int indent: The amount of spaces to use for indentation,
            defaults to 0, optional
        :returns: The json serialization of the given ``dictionary``
        :rtype: str
        """

        return json.dumps(dictionary, **kwargs)

    def on_json_loads(self, json, config, content, **kwargs):
        """ The :mod:`json` loads method.

        :param module json: The ``json`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return json.loads(content)

    def on_ujson_dumps(self, ujson, config, dictionary, **kwargs):
        """ The `ujson <https://pypi.org/project/ujson/>`_ dumps method.

        :param module ujson: The ``ujson`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary instance to serialize
        :param int indent: The amount of spaces to use for indentation,
            defaults to 0, optional
        :returns: The json serialization of the given ``dictionary``
        :rtype: str
        """

        if not kwargs.get("indent", None):
            kwargs["indent"] = 0
        return ujson.dumps(dictionary, **kwargs)

    def on_ujson_loads(self, ujson, config, content, **kwargs):
        """ The `ujson <https://pypi.org/project/ujson/>`_ loads method.

        :param module ujson: The ``ujson`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return ujson.loads(content)

    def on_rapidjson_dumps(self, rapidjson, config, dictionary, **kwargs):
        """ The `rapidjson <https://pypi.org/project/python-rapidjson/>`_ dumps method.

        :param module rapidjson: The ``rapidjson`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary instance to serialize
        :param int indent: The amount of spaces to use for indentation,
            defaults to 0, optional
        :returns: The json serialization of the given ``dictionary``
        :rtype: str
        """

        return rapidjson.dumps(dictionary, **kwargs)

    def on_rapidjson_loads(self, rapidjson, config, content, **kwargs):
        """ The `rapidjson <https://pypi.org/project/python-rapidjson/>`_ loads method.

        :param module rapidjson: The ``rapidjson`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return rapidjson.loads(content)
