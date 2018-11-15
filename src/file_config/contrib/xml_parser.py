# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import collections

import attr
from lxml import etree


@attr.s
class XMLParser(object):

    tree = attr.ib(type=etree.Element)

    @classmethod
    def _build_base(cls, element):
        return __builtins__[element.get("type")](element.text)

    @classmethod
    def _build_list(cls, list_element, dict_type=collections.OrderedDict):
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
        element = etree.Element(key, type=type(value).__name__)
        element.text = str(value)
        return element

    @classmethod
    def _build_list_etree(cls, parent, items):
        for item in items:
            if isinstance(item, dict):
                dict_element = etree.Element(parent.tag)
                parent.append(cls._build_dict_etree(item, dict_element))
            elif isinstance(item, (list, tuple, set, frozenset)):
                parent.append(cls._build_list_etree(parent, item))
            else:
                parent.append(cls._build_base_etree(parent, parent.tag, item))
        return parent

    @classmethod
    def _build_dict_etree(cls, dictionary, tree):
        # TODO: compress _build_list_etree and _build_dict_etree logic
        for (key, value) in dictionary.items():
            if isinstance(value, dict):
                tree.append(cls._build_dict_etree(value, etree.Element(key)))
            elif isinstance(value, (list, tuple, set, frozenset)):
                list_parent = etree.Element(key)
                tree.append(cls._build_list_etree(list_parent, value))
            else:
                tree.append(cls._build_base_etree(tree, key, value))
        return tree

    @classmethod
    def from_dict(cls, dictionary, root="root"):
        return cls(cls._build_dict_etree(dictionary, etree.Element(root)))

    @classmethod
    def from_xml(cls, content):
        return cls(etree.XML(content))

    def to_dict(self):
        return self._build_dict(self.tree)

    def to_xml(self, pretty=False):
        return etree.tostring(self.tree, pretty_print=pretty).decode("utf-8")
