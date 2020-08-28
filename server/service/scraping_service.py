from typing import List, MutableMapping, Optional

from requests_html import HTMLSession, BaseParser, Element, HTML

from service.i_database_service import IDataBaseService


class DomObject:
    """DOMオブジェクト"""
    def __init__(self, base_parser: BaseParser):
        self.base_parser = base_parser

    def find(self, query: str) -> Optional['DomObject']:
        temp = self.base_parser.find(query, first=True)
        if temp is None:
            return None
        return DomObject(temp)

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
    def __init__(self, database: IDataBaseService):
        self.session = HTMLSession()
        self.database = database
        self.database.query('CREATE TABLE IF NOT EXISTS page_cache (url TEXT PRIMARY KEY, text TEXT)')

    def get_page(self, url: str) -> DomObject:
        cache_data = self.database.select('SELECT text from page_cache WHERE url=?', (url,))
        if len(cache_data) == 0:
            temp: HTML = self.session.get(url).html
            print(f'caching... [{url}]')
            self.database.query('INSERT INTO page_cache (url, text) VALUES (?, ?)',
                                (url, temp.raw_html.decode(temp.encoding)))
            return DomObject(temp)
        else:
            return DomObject(HTML(html=cache_data[0]['text']))
