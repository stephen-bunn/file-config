# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class JSONHandler(BaseHandler):
    """ The JSON serialization handler.
    """

    name = "json"
    packages = ("ujson", "json")
    options = {"indent": 0}

    def on_json_dumps(self, json, dictionary, **kwargs):
        """ The :mod:`json` dumps method.
        """

        return json.dumps(dictionary, indent=kwargs.get("indent", 0))

    def on_json_loads(self, json, content):
        """ The :mod:`json` loads method.
        """

        return json.loads(content)

    def on_ujson_dumps(self, ujson, dictionary, **kwargs):
        """ The `ujson <https://pypi.org/project/ujson/>`_ dumps method.
        """

        return ujson.dumps(dictionary, indent=kwargs.get("indent", 0))

    def on_ujson_loads(self, ujson, content):
        """ The `ujson <https://pypi.org/project/ujson/>`_ loads method.
        """

        return ujson.loads(content)
