from decimal import Decimal
from typing import List, MutableMapping, Optional, Dict, Tuple

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
    if wide_focal_length == telephoto_focal_length:
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
        mount='マイクロフォーサーズ',
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


def dict_to_lens_for_o(record: Dict[str, str], record2: Dict[str, str]) -> Lens:
    """辞書型をレンズデータに変換する

    Parameters
    ----------
    record: Dict[str, str]
        辞書型
    record2: Dict[str, str]
        辞書型

    Returns
    -------
        レンズデータ
    """

    # 35mm判換算焦点距離
    result1 = regex(record['焦点距離'], r'換算 *(\d+) *- *(\d+)mm相当')
    result2 = regex(record['焦点距離'], r'換算 *(\d+)mm相当')
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
    result1 = regex(record['最短撮影距離'], r'(\d+\.\d+) *m.*(\d+\.\d+) *m')
    result2 = regex(record['最短撮影距離'], r'(\d+\.\d+) *m')
    if len(result1) > 0:
        wide_min_focus_distance = int(Decimal(result1[0]).scaleb(3))
        telephoto_min_focus_distance = int(Decimal(result1[1]).scaleb(3))
    else:
        wide_min_focus_distance = int(Decimal(result2[0]).scaleb(3))
        telephoto_min_focus_distance = wide_min_focus_distance

    # 換算最大撮影倍率
    max_photographing_magnification = 0.0
    for key, val in record.items():
        if '最大撮影倍率' not in key:
            continue
        result = regex(val, r'(\d+\.\d+)倍相当')
        for x in result:
            max_photographing_magnification = max(max_photographing_magnification, float(x))
        result = regex(val, r'換算 *(\d+\.\d+)倍')
        for x in result:
            max_photographing_magnification = max(max_photographing_magnification, float(x))

    # フィルターサイズ
    filter_diameter = -1
    for key, val in record.items():
        if 'フィルターサイズ' not in key:
            continue
        result = regex(val, r'(\d+)mm')
        if len(result) > 0:
            filter_diameter = int(result[0])

    # 最大径と全長
    overall_diameter = 0.0
    overall_length = 0.0
    for key, val in record.items():
        if '最大径' not in key:
            continue
        if '全長' not in key and '長さ' not in key:
            continue
        result = regex(val, r'(\d+\.?\d*)')
        if len(result) >= 2:
            overall_diameter = float(result[0])
            overall_length = float(result[1])
            break

    # 防塵防滴
    is_drip_proof = False
    for key, val in record.items():
        if '防滴' in key:
            is_drip_proof = True
            break

    # 手ブレ補正
    has_image_stabilization = 'IS' in record['レンズ名']

    # インナーズーム
    is_inner_zoom = False
    if wide_focal_length == telephoto_focal_length:
        is_inner_zoom = True
    elif record['品番'] in ['7-14_28pro', '40-150_28pro']:
        is_inner_zoom = True

    # 質量
    result = regex(record['質量'], r'([\d,]+)(g|ｇ| g)')
    weight = int(result[0].replace(',', ''))

    # メーカー希望小売価格
    price = int(regex(record2['希望小売価格'], r'([0-9,]+)円')[0].replace(',', ''))

    return Lens(
        id=0,
        maker='OLYMPUS',
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
        mount='マイクロフォーサーズ',
    )


def get_o_lens_list(scraping: ScrapingService) -> List[Lens]:
    """OLYMPUS製レンズの情報を取得する

    Parameters
    ----------
    scraping: ScrapingService
        データスクレイピング用クラス

    Returns
    -------
        スクレイピング後のレンズデータ一覧
    """

    # レンズのURL一覧を取得する
    page = scraping.get_page('https://www.olympus-imaging.jp/product/dslr/mlens/index.html')
    lens_list: List[Tuple[str, str]] = []
    for a_element in page.find_all('h2.productName > a'):
        lens_name = a_element.text.split('/')[0].replace('\n', '')
        if 'M.ZUIKO' not in lens_name:
            continue
        lens_product_number = a_element.attrs['href'].replace('/product/dslr/mlens/', '').replace('/index.html', '')
        lens_list.append((lens_name, lens_product_number))

    # レンズごとに情報を取得する
    output: List[Lens] = []
    for lens_name, lens_product_number in lens_list:
        # ざっくり情報を取得する
        spec_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/spec.html'
        print(spec_url)
        page = scraping.get_page(spec_url)
        temp_dict: Dict[str, str] = {}
        for th_element, td_element in zip(page.find_all('th'), page.find_all('td')):
            if th_element is None or td_element is None:
                continue
            temp_dict[th_element.text] = td_element.text
        temp_dict['レンズ名'] = lens_name
        temp_dict['品番'] = lens_product_number

        index_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/index.html'
        print(f'  {index_url}')
        page = scraping.get_page(index_url)
        temp_dict2: Dict[str, str] = {}
        for th_element, td_element in zip(page.find_all('th'), page.find_all('td')):
            if th_element is None or td_element is None:
                continue
            temp_dict2[th_element.text] = td_element.text

        # 詳細な情報を取得する
        output.append(dict_to_lens_for_o(temp_dict, temp_dict2))
    return output


def dict_to_lens_for_s(record: Dict[str, str]) -> Lens:
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
    result1 = regex(record['レンズ名'], r'(\d+)mm～(\d+)mm')
    result2 = regex(record['レンズ名'], r'(\d+)mm')
    if len(result1) > 0:
        wide_focal_length = int(result1[0]) * 2
        telephoto_focal_length = int(result1[1]) * 2
    else:
        wide_focal_length = int(result2[0]) * 2
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

    # 最短撮影距離(cm単位のものをmm単位に変換していることに注意)
    result1 = regex(record['最短撮影距離'], r'(\d+\.?\d*)cm / (\d+\.?\d*)cm')
    result2 = regex(record['最短撮影距離'], r'(\d+\.?\d*)cm')
    if len(result1) > 0:
        wide_min_focus_distance = int(Decimal(result1[0]).scaleb(1))
        telephoto_min_focus_distance = int(Decimal(result1[1]).scaleb(1))
    else:
        wide_min_focus_distance = int(Decimal(result2[0]).scaleb(1))
        telephoto_min_focus_distance = wide_min_focus_distance

    # 換算最大撮影倍率
    result = regex(record['最大撮影倍率'], r'(\d+\.?\d*)：(\d+\.?\d*)')
    max_photographing_magnification = round(float(result[0]) / float(result[1]) * 2 * 100) / 100

    # フィルターサイズ
    result = regex(record['フィルターサイズ'], r'φ(\d+)mm')
    if len(result) > 0:
        filter_diameter = int(result[0])
    else:
        filter_diameter = -1

    # 最大径と全長
    result = regex(record['最大径 × 長さ マイクロフォーサーズ'], r'(\d+\.?\d*)mm[^\d]*(\d+\.?\d*)mm')
    overall_diameter = float(result[0])
    overall_length = float(result[1])

    # 防塵防滴
    is_drip_proof = False

    # 手ブレ補正
    has_image_stabilization = 'IS' in record['レンズ名']

    # インナーズーム
    is_inner_zoom = wide_focal_length == telephoto_focal_length

    # 質量
    result = regex(record['質量 マイクロフォーサーズ'], r'([\d,]+)g')
    weight = int(result[0].replace(',', ''))

    # メーカー希望小売価格
    result = regex(record['希望小売価格'], r'([\d,]+) *円')
    price = int(result[0].replace(',', ''))

    return Lens(
        id=0,
        maker='SIGMA',
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
        mount='マイクロフォーサーズ',
    )


def get_s_lens_list(scraping: ScrapingService) -> List[Lens]:
    """SIGMA製レンズの情報を取得する

    Parameters
    ----------
    scraping: ScrapingService
        データスクレイピング用クラス

    Returns
    -------
        スクレイピング後のレンズデータ一覧
    """

    # レンズのURL一覧を取得する
    page = scraping.get_page('https://www.sigma-global.com/jp/lenses/#/all/micro-four-thirds/')
    lens_list: List[Tuple[str, str]] = []
    for li_element in page.find_all('li.micro-four-thirds'):
        lens_link = 'https://www.sigma-global.com/' + li_element.find('a').attrs['href']
        if 'product' not in lens_link:
            continue
        lens_name = li_element.text.splitlines()[1]
        lens_list.append((lens_name, lens_link))

    # レンズごとに情報を取得する
    output: List[Lens] = []
    for lens_name, lens_link in lens_list:
        # ざっくり情報を取得する
        page = scraping.get_page(lens_link + 'specifications/')
        temp_dict: Dict[str, str] = {}
        th_text = ''
        for tr_element in page.find('table').find_all('tr'):
            th_elements = tr_element.find_all('th')
            if len(th_elements) > 0:
                th_text = th_elements[0].text
            td_elements = tr_element.find_all('td')
            if len(td_elements) == 1:
                temp_dict[th_text] = td_elements[0].text
            elif len(td_elements) == 2:
                temp_dict[th_text + ' ' + td_elements[0].text] = td_elements[1].text
        temp_dict['レンズ名'] = lens_name
        temp_dict['品番'] = lens_link.split('/')[-2]

        # 詳細な情報を取得する
        output.append(dict_to_lens_for_s(temp_dict))
    return output


def get_t_lens_list():
    return [
        Lens(
            id=0,
            maker='TAMRON',
            name='14-150mm F/3.5-5.8 Di III (Model C001)',
            product_number='C001',
            wide_focal_length=28,
            telephoto_focal_length=300,
            wide_f_number=3.5,
            telephoto_f_number=5.8,
            wide_min_focus_distance=500,
            telephoto_min_focus_distance=500,
            max_photographing_magnification=0.53,
            filter_diameter=52,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=False,
            overall_diameter=63.5,
            overall_length=80.4,
            weight=285,
            price=65000,
            mount='マイクロフォーサーズ',
        )
    ]


def get_other_lens_list():
    return [
        Lens(
            id=0,
            maker='Tokina',
            name='Reflex 300mm F6.3 MF MACRO',
            product_number='reflex_300mm_f63_mf_macro',
            wide_focal_length=600,
            telephoto_focal_length=600,
            wide_f_number=6.3,
            telephoto_f_number=6.3,
            wide_min_focus_distance=800,
            telephoto_min_focus_distance=800,
            max_photographing_magnification=1,
            filter_diameter=55,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=66,
            overall_length=66,
            weight=298,
            price=40000,
            mount='マイクロフォーサーズ',
        ),
        Lens(
            id=0,
            maker='Tokina',
            name='ミラーレンズ400mm F8 N II',
            product_number='4961607419649',
            wide_focal_length=800,
            telephoto_focal_length=800,
            wide_f_number=8,
            telephoto_f_number=8,
            wide_min_focus_distance=1150,
            telephoto_min_focus_distance=1150,
            max_photographing_magnification=0.8,
            filter_diameter=67,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=74,
            overall_length=112,
            weight=495,
            price=22000,
            mount='マイクロフォーサーズ',
        ),
        Lens(
            id=0,
            maker='Cosina',
            name='Voigtlander NOKTON 10.5mm F0.95',
            product_number='mft-10_5mm',
            wide_focal_length=21,
            telephoto_focal_length=21,
            wide_f_number=0.95,
            telephoto_f_number=0.95,
            wide_min_focus_distance=170,
            telephoto_min_focus_distance=170,
            max_photographing_magnification=0.24,
            filter_diameter=72,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=77,
            overall_length=82.4,
            weight=585,
            price=148000,
            mount='マイクロフォーサーズ',
        ),
        Lens(
            id=0,
            maker='Cosina',
            name='Voigtlander NOKTON 17.5mm F0.95',
            product_number='mft-17_5mm',
            wide_focal_length=35,
            telephoto_focal_length=35,
            wide_f_number=0.95,
            telephoto_f_number=0.95,
            wide_min_focus_distance=150,
            telephoto_min_focus_distance=150,
            max_photographing_magnification=0.5,
            filter_diameter=58,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=63.4,
            overall_length=80.0,
            weight=540,
            price=118000,
            mount='マイクロフォーサーズ',
        ),
        Lens(
            id=0,
            maker='Cosina',
            name='Voigtlander NOKTON 25mm F0.95 Type II',
            product_number='mft-25mm-2',
            wide_focal_length=50,
            telephoto_focal_length=50,
            wide_f_number=0.95,
            telephoto_f_number=0.95,
            wide_min_focus_distance=170,
            telephoto_min_focus_distance=170,
            max_photographing_magnification=0.51,
            filter_diameter=52,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=60.6,
            overall_length=70.0,
            weight=435,
            price=105000,
            mount='マイクロフォーサーズ',
        ),
        Lens(
            id=0,
            maker='Cosina',
            name='Voigtlander NOKTON 42.5mm F0.95',
            product_number='mft-42_5mm',
            wide_focal_length=85,
            telephoto_focal_length=85,
            wide_f_number=0.95,
            telephoto_f_number=0.95,
            wide_min_focus_distance=230,
            telephoto_min_focus_distance=230,
            max_photographing_magnification=0.5,
            filter_diameter=58,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=64.3,
            overall_length=74.6,
            weight=571,
            price=118000,
            mount='マイクロフォーサーズ',
        ),
        Lens(
            id=0,
            maker='Cosina',
            name='Voigtlander NOKTON 60mm F0.95',
            product_number='mft-60mm',
            wide_focal_length=120,
            telephoto_focal_length=120,
            wide_f_number=0.95,
            telephoto_f_number=0.95,
            wide_min_focus_distance=340,
            telephoto_min_focus_distance=340,
            max_photographing_magnification=0.5,
            filter_diameter=77,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=82.5,
            overall_length=87.7,
            weight=860,
            price=145000,
            mount='マイクロフォーサーズ',
        ),

        Lens(
            id=0,
            maker='KOWA',
            name='KOWA PROMINAR 8.5mm F2.8',
            product_number='',
            wide_focal_length=17,
            telephoto_focal_length=17,
            wide_f_number=2.8,
            telephoto_f_number=2.8,
            wide_min_focus_distance=200,
            telephoto_min_focus_distance=200,
            max_photographing_magnification=0.14,
            filter_diameter=86,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=71.5,
            overall_length=86.8,
            weight=440,
            price=116000,
            mount='マイクロフォーサーズ',
        ),
        Lens(
            id=0,
            maker='KOWA',
            name='KOWA PROMINAR 12mm F1.8',
            product_number='',
            wide_focal_length=24,
            telephoto_focal_length=24,
            wide_f_number=1.8,
            telephoto_f_number=1.8,
            wide_min_focus_distance=200,
            telephoto_min_focus_distance=200,
            max_photographing_magnification=0.19,
            filter_diameter=72,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=76.5,
            overall_length=90.5,
            weight=475,
            price=109000,
            mount='マイクロフォーサーズ',
        ),
        Lens(
            id=0,
            maker='KOWA',
            name='KOWA PROMINAR 25mm F1.8',
            product_number='',
            wide_focal_length=50,
            telephoto_focal_length=50,
            wide_f_number=1.8,
            telephoto_f_number=1.8,
            wide_min_focus_distance=250,
            telephoto_min_focus_distance=250,
            max_photographing_magnification=0.28,
            filter_diameter=55,
            is_drip_proof=False,
            has_image_stabilization=False,
            is_inner_zoom=True,
            overall_diameter=60,
            overall_length=94,
            weight=400,
            price=89000,
            mount='マイクロフォーサーズ',
        )
    ]
