# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

from ._common import BaseHandler


class MsgpackHandler(BaseHandler):
    """ The Message Pack serialization handler.
    """

    name = "msgpack"
    packages = ("msgpack",)
    options = {}

    def on_msgpack_dumps(self, msgpack, config, dictionary, **kwargs):
        """ The `msgpack <https://pypi.org/project/msgpack/>`_ dumps method.

        :param module msgpack: The ``msgpack`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary instance to serialize
        :returns: The serialized content
        :rtype: str
        """

        return msgpack.dumps(dictionary)

    def on_msgpack_loads(self, msgpack, config, content, **kwargs):
        """ The `msgpack <https://pypi.org/project/msgpack/>`_ loads method.

        :param module msgpack: The ``msgpack`` module
        :param class config: The loading config class
        :param dict content: The serialized content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return msgpack.loads(content, raw=False)
