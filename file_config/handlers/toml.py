# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class TOMLHandler(BaseHandler):

    name = "toml"
    packages = ("tomlkit",)

    def on_tomlkit_dumps(self, tomlkit, dictionary: dict) -> str:
        return tomlkit.dumps(dictionary)

    def on_tomlkit_loads(self, tomlkit, content: str) -> dict:
        return tomlkit.parse(content)
