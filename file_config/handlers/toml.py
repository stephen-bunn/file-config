# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class TOMLHandler(BaseHandler):

    name = "toml"
    packages = ("tomlkit",)

    def on_tomlkit_dumps(self, tomlkit, dictionary):
        return tomlkit.dumps(dictionary)

    def on_tomlkit_loads(self, tomlkit, content):
        return tomlkit.parse(content)
