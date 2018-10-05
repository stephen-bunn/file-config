# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class TOMLHandler(BaseHandler):
    """ The TOML serialization handler.
    """

    name = "toml"
    packages = ("pytoml", "tomlkit")

    def on_pytoml_dumps(self, pytoml, dictionary):
        """ The `pytoml <https://pypi.org/project/pytoml/>`_ dumps method.
        """

        return pytoml.dumps(dictionary)

    def on_pytoml_loads(self, pytoml, content):
        """ The `pytoml <https://pypi.org/project/pytoml/>`_ loads method.
        """

        return pytoml.loads(content)

    def on_tomlkit_dumps(self, tomlkit, dictionary):
        """ The `tomlkit <https://pypi.org/project/tomlkit/>`_ dumps method.
        """

        return tomlkit.dumps(dictionary)

    def on_tomlkit_loads(self, tomlkit, content):
        """ The `tomlkit <https://pypi.org/project/tomlkit/>`_ loads method.
        """

        return tomlkit.parse(content)
