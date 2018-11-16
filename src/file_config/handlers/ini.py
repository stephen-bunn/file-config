# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import warnings

from ._common import BaseHandler
from ..contrib.ini_parser import INIParser


class INIHandler(BaseHandler):
    """ The INI serialization handler.

    .. important:: INI files **cannot** support arrays of mappings.
        Using these in your config and trying to dump to ini will throw a
        :class:`ValueError` and will fail serialization.

        If you need to use a config with arrays of mappings use
        `toml <https://github.com/toml-lang/toml>`_ instead.
        This use case is one of the many things toml does better than traditional
        config files.
    """

    name = "ini"
    packages = ("configparser",)
    options = {"root": None, "delimiter": ":", "empty_sections": False}

    def on_configparser_dumps(self, configparser, config, dictionary, **kwargs):
        """ The :mod:`configparser` dumps method.

        :param module configparser: The ``configparser`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary instance to serialize
        :param str root: The top-level section of the ini file,
            defaults to ``config.__name__``, optional
        :param str delimiter: The delimiter character used for representing nested
            dictionaries, defaults to ":", optional
        :return: The ini serialization of the given ``dictionary``
        :rtype: str
        """

        root_section = kwargs.pop("root")
        if not isinstance(root_section, str):
            root_section = config.__name__

        delimiter = kwargs.pop("delimiter", ":")
        if delimiter in root_section:
            warnings.warn(
                f"root section {root_section!r} contains delimiter character "
                f"{delimiter!r}, loading from the resulting content will likely fail"
            )

        try:
            return INIParser.from_dict(
                dictionary,
                root_section=root_section,
                delimiter=kwargs.pop("delimiter", ":"),
                empty_sections=kwargs.pop("empty_sections", False),
            ).to_ini()
        except ValueError:
            raise ValueError("INI cannot handle this config, try using toml instead")

    def on_configparser_loads(self, configparser, config, content, **kwargs):
        """ The :mod:`configparser` loads method.

        :param module configparser: The ``configparser`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :return: The deserialized dictionary
        :rtype: dict
        """

        return INIParser.from_ini(content).to_dict(
            delimiter=kwargs.pop("delimiter", ":")
        )
