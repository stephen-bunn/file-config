# Stubs for file_config.contrib.xml_parser (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any

class XMLParser:
    tree: Any = ...
    @classmethod
    def _build_base(cls, element: Any): ...
    @classmethod
    def _build_list(cls, list_element: Any, dict_type: Any = ...): ...
    @classmethod
    def _build_dict(cls, root_element: Any, dict_type: Any = ...): ...
    @classmethod
    def _build_base_etree(cls, parent: Any, key: Any, value: Any): ...
    @classmethod
    def _build_list_etree(cls, parent: Any, items: Any): ...
    @classmethod
    def _build_dict_etree(cls, parent: Any, dictionary: Any): ...
    @classmethod
    def from_dict(cls, dictionary: Any, root: str = ...): ...
    @classmethod
    def from_xml(cls, content: Any, encoding: str = ...): ...
    def to_dict(self, dict_type: Any = ...): ...
    def to_xml(self, pretty: bool = ..., xml_declaration: bool = ..., encoding: str = ...): ...
    def __init__(self, tree: Any) -> None: ...
    def __ne__(self, other: Any) -> None: ...
    def __eq__(self, other: Any) -> None: ...
    def __lt__(self, other: Any) -> None: ...
    def __le__(self, other: Any) -> None: ...
    def __gt__(self, other: Any) -> None: ...
    def __ge__(self, other: Any) -> None: ...
