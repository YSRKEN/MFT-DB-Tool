from typing import List, MutableMapping

from requests_html import HTMLSession, BaseParser, Element


class DomObject:
    """DOMオブジェクト"""
    def __init__(self, base_parser: BaseParser):
        self.base_parser = base_parser

    def find(self, query: str) -> 'DomObject':
        return DomObject(self.base_parser.find(query, first=True))

    def find_all(self, query: str) -> List['DomObject']:
        return [DomObject(x) for x in self.base_parser.find(query)]

    @property
    def text(self) -> str:
        return self.base_parser.text

    @property
    def full_text(self) -> str:
        return self.base_parser.full_text

    # noinspection PyTypeChecker
    @property
    def attrs(self) -> MutableMapping:
        temp: Element = self.base_parser
        return temp.attrs


class ScrapingService:
    """スクレイピング用のラッパークラス"""
    def __init__(self):
        self.session = HTMLSession()

    def get_page(self, url: str) -> DomObject:
        return DomObject(self.session.get(url).html)
