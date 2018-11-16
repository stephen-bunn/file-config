# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

from ._common import BaseHandler


class XMLHandler(BaseHandler):
    """ The XML serialization handler.
    """

    name = "xml"
    packages = ("lxml",)
    options = {
        "root": None,
        "pretty": False,
        "xml_declaration": False,
        "encoding": "utf-8",
    }

    def on_lxml_dumps(self, lxml, config, dictionary, **kwargs):
        """ The `lxml <https://pypi.org/project/lxml/>`_ dumps method.

        :param module lxml: The ``lxml`` module
        :param class config: The instance's config class
        :param dict dictionary: The dictionary to serialize
        :param str root: The root tag of the xml document, defaults to the config
            instance's name, optional
        :param bool pretty: Pretty format the resulting xml document, defaults to
            False, optional
        :param bool xml_declaration: Add the xml declaration header to the resulting
            xml document, defaults to False, optional
        :param str encoding: The encoding to use for the resulting xml document,
            defaults to "utf-8", optional
        :returns: The XML serialization
        :rtype: str
        """

        # NOTE: lazy import of XMLParser because class requires lxml to exist on import
        from ..contrib.xml_parser import XMLParser

        root = kwargs.pop("root")
        if not isinstance(root, str):
            root = config.__name__

        return XMLParser.from_dict(dictionary, root=root).to_xml(
            pretty=kwargs.pop("pretty", False),
            xml_declaration=kwargs.pop("xml_declaration", False),
            encoding=kwargs.pop("encoding", "utf-8"),
        )

    def on_lxml_loads(self, lxml, config, content, **kwargs):
        """ The `lxml <https://pypi.org/project/lxml/>`_ loads method.

        :param module lxml: The ``lxml`` module
        :param class config: The loading config class
        :param str content: The content to deserialize
        :param str encoding: The encoding to read the given xml document as, defaults to
            "utf-8", optional
        :returns: The deserialized dictionary
        :rtype: dict
        """

        # NOTE: lazy import of XMLParser because class requires lxml to exist on import
        from ..contrib.xml_parser import XMLParser

        return XMLParser.from_xml(
            content, encoding=kwargs.pop("encoding", "utf-8")
        ).to_dict()
