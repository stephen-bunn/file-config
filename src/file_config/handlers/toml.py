# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

import fnmatch
import warnings

from ._common import BaseHandler


class TOMLHandler(BaseHandler):
    """ The TOML serialization handler.
    """

    name = "toml"
    packages = ("tomlkit", "toml", "pytoml")
    options = {"inline_tables": []}

    def on_tomlkit_dumps(self, tomlkit, config, dictionary, **kwargs):
        """ The `tomlkit <https://pypi.org/project/tomlkit/>`_ dumps method.

        :param module tomlkit: The ``tomlkit`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary to serialize
        :param list inline_tables: A list glob patterns to use for derminining which
            dictionaries should be rendered as inline tables, defaults to [], optional
        :returns: The TOML serialization
        :rtype: str

        Dumping inline tables uses :mod:`fnmatch` to compare ``.`` delimited dictionary
        path glob patterns to filter tables

        >>> config.dumps_toml(prefer="tomlkit")
        name = "My Project"
        type = "personal-project"
        keywords = ["example", "test"]
        [dependencies]
        [dependencies.a-dependency]
        name = "A Dependency"
        version = "v12"
        >>> config.dumps_toml(prefer="tomlkit", inline_tables=["dependencies"])
        name = "My Project"
        type = "personal-project"
        keywords = ["example", "test"]
        dependencies = {a-dependency = {name = "A Dependency",version = "v12"}}
        >>> config.dumps_toml(prefer="tomlkit", inline_tables=["dependencies.*"])
        name = "My Project"
        type = "personal-project"
        keywords = ["example", "test"]
        [dependencies]
        a-dependency = {name = "A Dependency",version = "v12"}
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

    def on_tomlkit_loads(self, tomlkit, config, content, **kwargs):
        """ The `tomlkit <https://pypi.org/project/tomlkit/>`_ loads method.

        :param module tomlkit: The ``tomlkit`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return tomlkit.parse(content)

    def on_toml_dumps(self, toml, config, dictionary, **kwargs):
        """ The `toml <https://pypi.org/project/toml/>`_ dumps method.

        :param module toml: The ``toml`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary to serialize
        :param list inline_tables: A list glob patterns to use for derminining which
            dictionaries should be rendered as inline tables, defaults to [], optional
        :returns: The TOML serialization
        :rtype: str

        Dumping inline tables uses :mod:`fnmatch` to compare ``.`` delimited dictionary
        path glob patterns to filter tables

        >>> config.dumps_toml(prefer="toml")
        name = "My Project"
        type = "personal-project"
        keywords = [ "example", "test",]
        [dependencies.a-dependency]
        name = "A Dependency"
        version = "v12"
        >>> config.dumps_toml(prefer="toml", inline_tables=["dependencies"])
        name = "My Project"
        type = "personal-project"
        keywords = [ "example", "test",]
        dependencies = {a-dependency = {name = "A Dependency",version = "v12"}
        }
        >>> config.dumps_toml(prefer="toml", inline_tables=["dependencies.*"])
        name = "My Project"
        type = "personal-project"
        keywords = [ "example", "test",]
        [dependencies]
        a-dependency = { name = "A Dependency", version = "v12" }
        """

        inline_tables = set(kwargs.get("inline_tables", []))

        def _dump_dict(dictionary, source, source_path=[]):
            for (key, value) in dictionary.items():
                if isinstance(value, dict):
                    is_inline = any(
                        [
                            fnmatch.fnmatch(".".join(source_path + [key]), pattern)
                            for pattern in inline_tables
                        ]
                    )
                    if is_inline:
                        source[key] = toml.TomlDecoder().get_empty_inline_table()
                    else:
                        source[key] = {}
                    source[key].update(
                        _dump_dict(value, {}, source_path=source_path + [key])
                    )
                else:
                    source[key] = value
            return source

        encoder = toml.TomlEncoder(preserve=True)
        return toml.dumps(_dump_dict(dictionary, {}), encoder=encoder)

    def on_toml_loads(self, toml, config, content, **kwargs):
        """ The `toml <https://pypi.org/project/toml/>`_ loads method.

        :param module toml: The ``toml`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return toml.loads(content)

    def on_pytoml_dumps(self, pytoml, config, dictionary, **kwargs):
        """ The `pytoml <https://pypi.org/project/pytoml/>`_ dumps method.

        :param module pytoml: The ``pytoml`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary to serialize
        :returns: The TOML serialization
        :rtype: str
        """

        inline_tables = set(kwargs.get("inline_tables", []))
        if len(inline_tables) > 0:
            warnings.warn("pytoml does not support 'inline_tables' argument")
        return pytoml.dumps(dictionary)

    def on_pytoml_loads(self, pytoml, config, content, **kwargs):
        """ The `pytoml <https://pypi.org/project/pytoml/>`_ loads method.

        :param module pytoml: The ``pytoml`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :returns: The deserialized dictionary
        :rtype: dict
        """

        return pytoml.loads(content)
