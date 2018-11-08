# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import io
import functools
import collections

from ._common import BaseHandler


class INIHandler(BaseHandler):
    """ The INI serialization handler.
    """

    name = "ini"
    packages = ("configparser",)
    options = {"root_section": None}

    def on_configparser_dumps(self, configparser, config, dictionary, **kwargs):
        """ The :mod:`configparser` dumps method.

        :param module configparser: The ``configparser`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary instance to serialize
        :param str root_section: The top-level section of the ini file,
            defaults to ``config.__name__``, optional
        :return: The ini serialization of the given ``dictionary``
        :rtype: str
        """

        def _dump_dict(dictionary, source, source_path=[]):
            source_key = ".".join(source_path)
            if not all(isinstance(_, dict) for _ in dictionary.values()):
                source.add_section(source_key)
            for (key, value) in dictionary.items():
                if isinstance(value, dict):
                    _dump_dict(value, source, source_path=(source_path + [key]))
                elif isinstance(value, list):
                    items = []
                    for item in value:
                        if isinstance(value, dict):
                            _dump_dict(value, source, source_path=(source_path + [key]))
                        else:
                            items.append(item)
                    source.set(source_key, key, ",".join(items))
                else:
                    source.set(source_key, key, value)
            return source

        # get root section
        root_section = config.__name__
        if "root_section" in kwargs and isinstance(kwargs["root_section"], str):
            root_section = kwargs.pop("root_section")

        parser = configparser.RawConfigParser()
        parser = _dump_dict(dictionary, parser, [root_section])

        string_file = io.StringIO()
        parser.write(string_file)
        return string_file.getvalue()

    def on_configparser_loads(self, configparser, config, content, **kwargs):
        """ The :mod:`configparser` loads method.

        :param module configparser: The ``configparser`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :return: The deserialized dictionary
        :rtype: dict
        """

        def _deep_get(dictionary, keys, default=None):
            return functools.reduce(
                lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
                keys.split("."),
                dictionary,
            )

        def _deep_set(dictionary, keys, value, dict_type=collections.OrderedDict):
            keys = keys.split(".")
            for (index, key) in enumerate(keys):
                if key not in dictionary:
                    if index >= (len(keys) - 1):
                        dictionary[key] = value
                    else:
                        dictionary[key] = dict_type()
                dictionary = dictionary[key]
            return dictionary

        def _load_dict(dictionary, source, source_path=[]):
            for (key, value) in dictionary.items():
                if "." in key:
                    _deep_set(dictionary, key, value)
                else:
                    dictionary[key] = value
            return dictionary

        # get root section
        root_section = config.__name__
        if "root_section" in kwargs and isinstance(kwargs["root_section"], str):
            root_section = kwargs.pop("root_section")

        parser = configparser.ConfigParser()
        parser.read_string(content)
        print(_load_dict(parser._sections, collections.OrderedDict())[root_section])
        return _load_dict(parser._sections, collections.OrderedDict())[root_section]
