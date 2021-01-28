from typing import Optional, List, MutableMapping

# noinspection PyProtectedMember
from lxml.html import HtmlElement
from model.DomObject import DomObject


class LxmlDomObject(DomObject):
    """DOMオブジェクト"""

    def __init__(self, dom: HtmlElement):
        self.dom = dom

    def find(self, query: str) -> Optional['DomObject']:
        temp = self.dom.cssselect(query)
        if len(temp) == 0:
            return None
        return LxmlDomObject(temp[0])

    def find_all(self, query: str) -> List['DomObject']:
        return [LxmlDomObject(x) for x in self.dom.cssselect(query)]

    @property
    def text(self) -> str:
        return self.dom.text

    @property
    def full_text(self) -> str:
        return self.dom.text_content()

    @property
    def attrs(self) -> MutableMapping:
        return self.dom.attrib
