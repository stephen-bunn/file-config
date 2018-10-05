# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class JSONHandler(BaseHandler):
    """ The JSON serialization handler.
    """

    name = "json"
    packages = ("ujson", "json")

    def on_json_dumps(self, json, dictionary):
        """ The :mod:`json` dumps method.
        """

        return json.dumps(dictionary)

    def on_json_loads(self, json, content):
        """ The :mod:`json` loads method.
        """

        return json.loads(content)

    def on_ujson_dumps(self, ujson, dictionary):
        """ The `ujson <https://pypi.org/project/ujson/>`_ dumps method.
        """

        return ujson.dumps(dictionary)

    def on_ujson_loads(self, ujson, content):
        """ The `ujson <https://pypi.org/project/ujson/>`_ loads method.
        """

        return ujson.loads(content)
