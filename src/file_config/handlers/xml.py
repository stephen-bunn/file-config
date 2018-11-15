# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

from ._common import BaseHandler
from ..contrib import XMLParser


class XMLHandler(BaseHandler):

    name = "xml"
    packages = ("lxml",)
    options = {"root": None, "pretty": False}

    def on_lxml_dumps(self, lxml, config, dictionary, **kwargs):
        root = kwargs.pop("root")
        if not isinstance(root, str):
            root = config.__name__

        return XMLParser.from_dict(dictionary, root=root).to_xml(
            pretty=kwargs.pop("pretty", False)
        )

    def on_lxml_loads(self, lxml, config, content, **kwargs):
        return XMLParser.from_xml(content).to_dict()
