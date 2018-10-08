# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

import fnmatch
import warnings

from ._common import BaseHandler


class TOMLHandler(BaseHandler):
    """ The TOML serialization handler.
    """

    name = "toml"
    packages = ("tomlkit", "pytoml")
    options = {"inline_tables": []}

    def on_tomlkit_dumps(self, tomlkit, dictionary, **kwargs):
        """ The `tomlkit <https://pypi.org/project/tomlkit/>`_ dumps method.
        """

        inline_tables = set(kwargs.get("inline_tables", []))

        def _dump_dict(dictionary, source, source_path=[]):
            for (key, value) in dictionary.items():
                if isinstance(value, dict):
                    # checks the current path with fnmatch to see if current table
                    # should be an inline table
                    is_inline = any(
                        [
                            fnmatch.fnmatch(".".join(source_path + [key]), pattern)
                            for pattern in inline_tables
                        ]
                    )
                    if is_inline:
                        table = tomlkit.inline_table()
                        # NOTE: manual dictionary assignment because `tomlkit` does not
                        # impelment `dict.update`
                        for (inline_key, inline_value) in value.items():
                            if isinstance(inline_value, dict):
                                table[inline_key] = _dump_dict(
                                    inline_value,
                                    tomlkit.inline_table(),
                                    source_path=source_path + [inline_key],
                                )
                            else:
                                table[inline_key] = inline_value
                        source[key] = table
                    else:
                        source[key] = _dump_dict(
                            value, tomlkit.table(), source_path=source_path + [key]
                        )
                else:
                    source[key] = value
            return source

        return tomlkit.dumps(_dump_dict(dictionary, tomlkit.document()))

    def on_tomlkit_loads(self, tomlkit, content):
        """ The `tomlkit <https://pypi.org/project/tomlkit/>`_ loads method.
        """

        return tomlkit.parse(content)

    def on_pytoml_dumps(self, pytoml, dictionary, **kwargs):
        """ The `pytoml <https://pypi.org/project/pytoml/>`_ dumps method.
        """

        inline_tables = set(kwargs.get("inline_tables", []))
        if len(inline_tables) > 0:
            warnings.warn(
                "pytoml does not support 'inline_tables' argument, use tomlkit instead"
            )
        return pytoml.dumps(dictionary)

    def on_pytoml_loads(self, pytoml, content):
        """ The `pytoml <https://pypi.org/project/pytoml/>`_ loads method.
        """

        return pytoml.loads(content)
