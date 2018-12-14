# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import io
import re
import collections
import configparser

DEFAULT_DELIMITER = ":"


class INIParser(configparser.ConfigParser):
    """ A custom INI (config) parser which obeys the Mozilla files specification.

    .. important:: This parser conforms to what Mozilla says configuration files and
        their encoded values and types should look like.
        You can find their specification `here <https://bit.ly/2DksT5u>`_

    .. warning:: This parser is very unstable across the extremely wide range of ways
        that INI files can be represented. Mainly this was just created to be reflective
        with it's own results rather than building a new :mod:`configparser`.

        So building a config instance that parses things like ``tox.ini`` might take a
        bit of hacking to work.
    """

    # characters that require the string to be quoted
    requires_quotes = (" ", "\t", "=")
    quoted_string_regex = re.compile(r"^(\'.*\')|(\".*\")$")

    @classmethod
    def _encode_var(cls, var):
        """ Encodes a variable to the appropriate string format for ini files.

        :param var: The variable to encode
        :return: The ini representation of the variable
        :rtype: str
        """

        if isinstance(var, str):
            if any(_ in var for _ in cls.requires_quotes):
                # NOTE: quoted strings should just use '"' according to the spec
                return '"' + var.replace('"', '\\"') + '"'
            return var
        else:
            return str(var)

    @classmethod
    def _decode_var(cls, string):
        """ Decodes a given string into the appropriate type in Python.

        :param str string: The string to decode
        :return: The decoded value
        """

        str_match = cls.quoted_string_regex.match(string)
        if str_match:
            return string.strip("'" if str_match.groups()[0] else '"')
        elif string.isdigit():
            return int(string)
        elif string.lower() in ("true", "false"):
            return string.lower() == "true"
        elif string.lstrip("-").isdigit():
            try:
                return int(string)
            except ValueError:
                # case where we mistake something like "--0" a a int
                return string
        elif "." in string.lstrip("-"):
            try:
                return float(string)
            except ValueError:
                # one off case where we mistake a single "." as a float
                return string
        else:
            return string

    @classmethod
    def _build_dict(
        cls, parser_dict, delimiter=DEFAULT_DELIMITER, dict_type=collections.OrderedDict
    ):
        """ Builds a dictionary of ``dict_type`` given the ``parser._sections`` dict.

        :param dict parser_dict: The ``parser._sections`` mapping
        :param str delimiter: The delimiter for nested dictionaries,
            defaults to ":", optional
        :param class dict_type: The dictionary type to use for building the dict,
            defaults to :class:`collections.OrderedDict`, optional
        :return: The resulting dictionary
        :rtype: dict
        """

        result = dict_type()
        for (key, value) in parser_dict.items():
            if isinstance(value, dict):
                nestings = key.split(delimiter)

                # build nested dictionaries if they don't exist (up to 2nd to last key)
                base_dict = result
                for nested_key in nestings[:-1]:
                    if nested_key not in base_dict:
                        base_dict[nested_key] = dict_type()
                    base_dict = base_dict[nested_key]

                base_dict[nestings[-1]] = cls._build_dict(
                    parser_dict.get(key), delimiter=delimiter, dict_type=dict_type
                )
            else:
                if "\n" in value:
                    result[key] = [
                        cls._decode_var(_) for _ in value.lstrip("\n").split("\n")
                    ]
                else:
                    result[key] = cls._decode_var(value)
        return result

    @classmethod
    def _build_parser(
        cls,
        dictionary,
        parser,
        section_name,
        delimiter=DEFAULT_DELIMITER,
        empty_sections=False,
    ):
        """ Populates a parser instance with the content of a dictionary.

        :param dict dictionary: The dictionary to use for populating the parser instance
        :param configparser.ConfigParser parser: The parser instance
        :param str section_name: The current section name to add the dictionary keys to
        :param str delimiter: The nested dictionary delimiter character,
            defaults to ":", optional
        :param bool empty_sections: Flag to allow the representation of empty sections
            to exist, defaults to False, optional
        :return: The populated parser
        :rtype: configparser.ConfigParser
        """

        for (key, value) in dictionary.items():
            if isinstance(value, dict):
                nested_section = delimiter.join([section_name, key])
                is_empty = all(isinstance(_, dict) for _ in value.values())
                if not is_empty or empty_sections:
                    parser.add_section(nested_section)
                cls._build_parser(value, parser, nested_section, delimiter=delimiter)
            elif isinstance(value, (list, tuple, set, frozenset)):
                if any(isinstance(_, dict) for _ in value):
                    raise ValueError(
                        f"INI files cannot support arrays with mappings, "
                        f"found in key {key!r}"
                    )
                parser.set(
                    section_name, key, "\n".join(cls._encode_var(_) for _ in value)
                )
            else:
                parser.set(section_name, key, cls._encode_var(value))
        return parser

    @classmethod
    def from_dict(
        cls,
        dictionary,
        root_section="root",
        delimiter=DEFAULT_DELIMITER,
        empty_sections=False,
    ):
        """ Create an instance of ``INIParser`` from a given dictionary.

        :param dict dictionary: The dictionary to create an instance from
        :param str root_section: The root key of the ini content, defaults to "root",
            optional
        :param str delimiter: The delimiter character to use for nested dictionaries,
            defaults to ":", optional
        :param bool empty_sections: Flag to allow representation of empty sections to
            exist, defaults to False, optional
        :return: The new ``INIParser`` instance
        :rtype: INIParser
        """

        parser = cls()
        parser.add_section(root_section)
        return cls._build_parser(
            dictionary,
            parser,
            root_section,
            delimiter=delimiter,
            empty_sections=empty_sections,
        )

    @classmethod
    def from_ini(cls, content):
        """ Create an instance of ``INIParser`` from some ini content string.

        :param str content: The ini content to create an instance from
        :return: The new ``INIParser`` instance
        :rtype: INIParser
        """

        parser = cls()
        parser.read_string(content)
        return parser

    def to_dict(self, delimiter=DEFAULT_DELIMITER, dict_type=collections.OrderedDict):
        """ Get the dictionary representation of the current parser.

        :param str delimiter: The delimiter used for nested dictionaries,
            defaults to ":", optional
        :param class dict_type: The dictionary type to use for building the dictionary
            reperesentation, defaults to collections.OrderedDict, optional
        :return: The dictionary representation of the parser instance
        :rtype: dict
        """

        root_key = self.sections()[0]
        return self._build_dict(
            self._sections, delimiter=delimiter, dict_type=dict_type
        ).get(root_key, {})

    def to_ini(self):
        """ Get the ini string of the current parser.

        :return: The ini string of the current parser
        :rtype: str
        """

        fake_io = io.StringIO()
        self.write(fake_io)
        return fake_io.getvalue()
