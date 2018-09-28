# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class MsgpackHandler(BaseHandler):

    name = "msgpack"
    packages = ("msgpack",)

    def on_msgpack_dumps(self, msgpack, dictionary):
        return msgpack.dumps(dictionary)

    def on_msgpack_loads(self, msgpack, content):
        return msgpack.loads(content, raw=False)
