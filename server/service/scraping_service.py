from decimal import Decimal
from typing import List, MutableMapping, Optional, Dict

from pandas import DataFrame
from requests_html import HTMLSession, BaseParser, Element, HTML

from constant import Lens
from service.i_database_service import IDataBaseService
from service.ulitity import regex


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


def dict_to_lens_for_p(record: Dict[str, str]) -> Lens:
    """辞書型をレンズデータに変換する

    Parameters
    ----------
    record: Dict[str, str]
        辞書型

    Returns
    -------
        レンズデータ
    """

    # 35mm判換算焦点距離
    result1 = regex(record['35mm判換算焦点距離'], r'(\d+)mm～(\d+)mm')
    result2 = regex(record['35mm判換算焦点距離'], r'(\d+)mm')
    if len(result1) > 0:
        wide_focal_length = int(result1[0])
        telephoto_focal_length = int(result1[1])
    else:
        wide_focal_length = int(result2[0])
        telephoto_focal_length = wide_focal_length

    # F値
    result1 = regex(record['レンズ名'], r'F(\d+\.?\d*)-(\d+\.?\d*)')
    result2 = regex(record['レンズ名'], r'F(\d+\.?\d*)')
    if len(result1) > 0:
        wide_f_number = float(result1[0])
        telephoto_f_number = float(result1[1])
    else:
        wide_f_number = float(result2[0])
        telephoto_f_number = wide_f_number

    # 最短撮影距離(m単位のものをmm単位に変換していることに注意)
    result1 = regex(record['最短撮影距離'], r'(\d+\.?\d*)m / (\d+\.?\d*)m')
    result2 = regex(record['最短撮影距離'], r'(\d+\.?\d*)m')
    if len(result1) > 0:
        wide_min_focus_distance = int(Decimal(result1[0]).scaleb(3))
        telephoto_min_focus_distance = int(Decimal(result1[1]).scaleb(3))
    else:
        wide_min_focus_distance = int(Decimal(result2[0]).scaleb(3))
        telephoto_min_focus_distance = wide_min_focus_distance

    # 換算最大撮影倍率
    result = regex(record['最大撮影倍率'], r'：(\d+\.?\d*)')
    max_photographing_magnification = float(result[0])

    # フィルターサイズ
    result = regex(record['フィルターサイズ'], r'φ(\d+)mm')
    if len(result) > 0:
        filter_diameter = int(result[0])
    else:
        filter_diameter = -1

    # 最大径と全長
    result = regex(record['最大径×全長'], r'(\d+\.?\d*)mm[^\d]*(\d+\.?\d*)mm')
    overall_diameter = float(result[0])
    overall_length = float(result[1])

    # 防塵防滴
    is_drip_proof = record['防塵・防滴'].find('○') >= 0 or record['防塵・防滴'].find('〇') >= 0

    # 手ブレ補正
    has_image_stabilization = record['手ブレ補正'].find('O.I.S.') >= 0

    # インナーズーム
    is_inner_zoom = False
    if wide_focal_length == wide_focal_length:
        is_inner_zoom = True
    elif record['品番'] in ['H-F007014', 'H-E08018', 'H-PS45175']:
        is_inner_zoom = True

    # 質量
    result = regex(record['質量'], r'([\d,]+)g')
    weight = int(result[0].replace(',', ''))

    # メーカー希望小売価格
    result = regex(record['メーカー希望小売価格'], r'([\d,]+) *円')
    price = int(result[0].replace(',', ''))

    return Lens(
        id=0,
        maker='Panasonic',
        name=record['レンズ名'],
        product_number=record['品番'],
        wide_focal_length=wide_focal_length,
        telephoto_focal_length=telephoto_focal_length,
        wide_f_number=wide_f_number,
        telephoto_f_number=telephoto_f_number,
        wide_min_focus_distance=wide_min_focus_distance,
        telephoto_min_focus_distance=telephoto_min_focus_distance,
        max_photographing_magnification=max_photographing_magnification,
        filter_diameter=filter_diameter,
        is_drip_proof=is_drip_proof,
        has_image_stabilization=has_image_stabilization,
        is_inner_zoom=is_inner_zoom,
        overall_diameter=overall_diameter,
        overall_length=overall_length,
        weight=weight,
        price=price,
    )


def get_p_lens_list(scraping: ScrapingService) -> List[Lens]:
    """Panasonic製レンズの情報を取得する

    Parameters
    ----------
    scraping: ScrapingService
        データスクレイピング用クラス

    Returns
    -------
        スクレイピング後のレンズデータ一覧
    """
    # 情報ページを開く
    page = scraping.get_page('https://panasonic.jp/dc/comparison.html')

    # tableタグからデータを収集する
    df = DataFrame()
    for table_element in page.find_all('table'):
        if 'LUMIX G' not in table_element.full_text:
            continue
        df['レンズ名'] = [x.text for x in table_element.find_all('th p')]
        for tr_element in table_element.find_all('tbody > tr'):
            key = tr_element.find('th').text
            value = [x.text for x in tr_element.find_all('td')]
            df[key] = value
        break

    # tableタグの各行を、Lens型のデータに変換する
    return [dict_to_lens_for_p(x) for x in df.to_dict(orient='records')]
