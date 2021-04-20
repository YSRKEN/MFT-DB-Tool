import time

import lxml
import requests

from model import DomObject
from model.LxmlDomObject import LxmlDomObject
from service.i_scraping_service import IScrapingService
from service.i_database_service import IDataBaseService


class LxmlScrapingService(IScrapingService):
    """スクレイピング用のラッパークラス"""

    def __init__(self, database: IDataBaseService):
        self.database = database
        self.database.query('CREATE TABLE IF NOT EXISTS page_cache (url TEXT PRIMARY KEY, text TEXT)')

    def get_page(self, url: str, encoding='', cache=True) -> DomObject:
        cache_data = self.database.select('SELECT text from page_cache WHERE url=?', (url,))
        if len(cache_data) == 0 or not cache:
            response = requests.get(url)
            if encoding != '':
                response.encoding = encoding
            text = response.text.encode(response.encoding, 'ignore').decode(response.encoding, 'ignore') \
                .encode(response.encoding, 'ignore')
            time.sleep(1)
            if cache:
                print(f'caching... [{url}]')
                self.database.query('INSERT INTO page_cache (url, text) VALUES (?, ?)', (url, text))
            return LxmlDomObject(lxml.html.fromstring(text))
        else:
            return LxmlDomObject(lxml.html.fromstring(cache_data[0]['text']))
