# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class MessagePackHandler(BaseHandler):

    name = "msgpack"
    packages = ("msgpack",)

    def on_msgpack_dumps(self, msgpack, dictionary: dict) -> str:
        return msgpack.dumps(dictionary)

    def on_msgpack_loads(self, msgpack, content: str) -> dict:
        return msgpack.loads(content, raw=False)
