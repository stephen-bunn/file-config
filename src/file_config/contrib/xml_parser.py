# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import collections

import attr
from lxml import etree
from defusedxml.lxml import fromstring


@attr.s
class XMLParser(object):
    """ A custom XML parser which is reflective between xml and dictionaries.

    .. warning:: This parser **requires** ``type`` to be set on every value element.
        This is the only way the XML can be correctly parsed and understood by the
        loading config.

        So this parser is really effective at being reflective with itself. However, it
        might require hacking to make it work with xml documents that are not built from
        a config instance in the first place.
    """

    tree = attr.ib(type=etree.Element)

    @classmethod
    def _build_base(cls, element):
        """ Builds a base value from the given etree element.

        :param lxml.etree.Element element: The element to build from
        :return: The built value
        """

        return __builtins__[element.get("type")](element.text)

    @classmethod
    def _build_list(cls, list_element, dict_type=collections.OrderedDict):
        """ Builds a list entry from a list parent element.

        :param lxml.etree.Element list_element: The element to build from
        :param class dict_type: The dictionary class to build with, defaults to
            :class:`collections.OrderedDict`, optional
        :return: The built list
        :rtype: list
        """

        result = []
        for element in list_element:
            if "type" in element.attrib:
                result.append(cls._build_base(element))
            else:
                if all((_.tag == element.tag) for _ in element):
                    result.append(cls._build_list(element))
                else:
                    result.append(cls._build_dict(element, dict_type=dict_type))
        return result

    @classmethod
    def _build_dict(cls, root_element, dict_type=collections.OrderedDict):
        """ Builds a dictionary entry from a dictionary parent element.

        :param lxml.etree.Element root_element: The element to build from
        :param dict_type: The dictionary class to build with, defaults to
            :class:`collections.OrderedDict`, optional
        :return: The built dictionary
        :rtype: dict
        """

        result = dict_type()
        for element in root_element:
            if "type" in element.attrib:
                result[element.tag] = cls._build_base(element)
            else:
                if all((_.tag == element.tag) for _ in element):
                    result[element.tag] = cls._build_list(element, dict_type=dict_type)
                else:
                    result[element.tag] = cls._build_dict(element, dict_type=dict_type)
        return result

    @classmethod
    def _build_base_etree(cls, parent, key, value):
        """ Builds a element from a base dictionary entry.

        :param lxml.etree.Element parent: The parent element to add to
        :param str key: The key of the entry
        :param value: The value of th entry
        :return: The built element
        :rtype: lxml.etree.Element
        """

        element = etree.Element(key, type=type(value).__name__)
        element.text = str(value)
        return element

    @classmethod
    def _build_list_etree(cls, parent, items):
        """ Builds a element for a list of items.

        :param lxml.etree.Element parent: The parent element to add to
        :param list items: The list to build elements for
        :return: The built list element
        :rtype: lxml.etree.Element
        """

        for item in items:
            if isinstance(item, dict):
                dict_element = etree.Element(parent.tag)
                parent.append(cls._build_dict_etree(dict_element, item))
            elif isinstance(item, (list, tuple, set, frozenset)):
                parent.append(cls._build_list_etree(parent, item))
            else:
                parent.append(cls._build_base_etree(parent, parent.tag, item))
        return parent

    @classmethod
    def _build_dict_etree(cls, parent, dictionary):
        """ Builds a element for a dictionary.

        :param lxml.etree.Element: The parent element to add to
        :param dict dictionary: The dictionary to build from
        :return: The built dictionary element
        :rtype: lxml.etree.Element
        """

        for (key, value) in dictionary.items():
            if isinstance(value, dict):
                parent.append(cls._build_dict_etree(etree.Element(key), value))
            elif isinstance(value, (list, tuple, set, frozenset)):
                list_parent = etree.Element(key)
                parent.append(cls._build_list_etree(list_parent, value))
            else:
                parent.append(cls._build_base_etree(parent, key, value))
        return parent

    @classmethod
    def from_dict(cls, dictionary, root="root"):
        """ Create an instance of ``XMLParser`` from a given dictionary.

        :param dict dictionary: The dictionary to build from
        :param root: The name of the root element to use, defaults to "root", optional
        :return: The new ``XMLParser`` instance
        :rtype: XMLParser
        """

        return cls(cls._build_dict_etree(etree.Element(root), dictionary))

    @classmethod
    def from_xml(cls, content, encoding="utf-8"):
        """ Create an instance of ``XMLParser`` from some xml content.

        :param str content: The xml content to build from
        :param str encoding: The encoding to use for reading the xml content
        :return: The new ``XMLParser`` instance
        :rtype: XMLParser
        """

        parser = etree.XMLParser(encoding=encoding)
        return cls(fromstring(content.encode(encoding), parser=parser))

    def to_dict(self, dict_type=collections.OrderedDict):
        """ Get the dictionary representation of the current parser.

        :param class dict_type: The dictionary type to build
        :return: The resulting dictionary
        :rtype: dict
        """

        return self._build_dict(self.tree, dict_type=dict_type)

    def to_xml(self, pretty=False, xml_declaration=False, encoding="utf-8"):
        """ Get the xml string of the current parser.

        :param bool pretty: Pretty format the resulting xml string
        :param bool xml_declaration: Add xml declaration header to resulting xml content
        :param str encoding: The encoding to use for the resulting xml content
        :return: The xml string of the current parser
        :rtype: str
        """

        return etree.tostring(
            self.tree,
            pretty_print=pretty,
            xml_declaration=xml_declaration,
            encoding=encoding.upper(),
        ).decode(encoding)
