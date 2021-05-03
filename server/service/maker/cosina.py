from decimal import Decimal
from typing import List, Tuple, Dict

from pandas import DataFrame

from service.i_scraping_service import IScrapingService
from service.ulitity import extract_numbers, regex

lens_name_table = {
    '10.5mm F0.95': 'Voigtlander NOKTON 10.5mm F0.95 Aspherical',
    '17.5mm F0.95': 'Voigtlander NOKTON 17.5mm F0.95 Aspherical',
    '25mm Type2': 'Voigtlander NOKTON 25mm F0.95 TypeII',
    '29mm': 'Voigtlander SUPER NOKTON 29mm F0.8 Aspherical',
    '42.5mm F0.95': 'Voigtlander NOKTON 42.5mm F0.95',
    'mft60mm': 'Voigtlander NOKTON 60mm F0.95',
}


def get_cosina_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str]] = []
    page = scraping.get_page('http://www.cosina.co.jp/seihin/voigtlander/mft-mount/index.html',
                             encoding='cp932', cache=False)
    for a_element in page.find_all('td > a'):
        lens_name = a_element.find('img').attrs['alt']
        lens_url = 'http://www.cosina.co.jp/seihin/voigtlander/mft-mount/' + a_element.attrs['href']
        if 'mm' in lens_name and 'mft' in a_element.attrs['href']:
            if lens_name not in lens_name_table:
                print(lens_name)
                raise Exception('未対応のレンズが含まれています')
            lens_list.append((lens_name_table[lens_name], lens_url))

    # レンズの情報を取得する
    temp_list: List[Dict[str, any]] = []
    for lens_name, lens_url in lens_list:
        page = scraping.get_page(lens_url, encoding='cp932')
        temp: Dict[str, str] = {'レンズ名': lens_name, 'URL': lens_url}
        for tr_element in page.find_all('tr'):
            td_elements = tr_element.find_all('td')
            if len(td_elements) < 2:
                continue
            if 'bgcolor' not in td_elements[0].attrs:
                continue
            if td_elements[0].full_text == '' or td_elements[1].full_text == '':
                continue
            temp[td_elements[0].full_text] = td_elements[1].full_text
        for h2_element in page.find_all('h2'):
            text = h2_element.text
            if '希望小売価格' in text:
                temp['希望小売価格'] = text.replace('\n', '')
        temp_list.append(temp)
    df = DataFrame.from_records(temp_list)

    # 変換用に整形
    df['maker'] = 'COSINA'

    df['name'] = df['レンズ名']
    del df['レンズ名']

    df['product_number'] = ''

    w, t = extract_numbers(df['焦点距離'], [], [r'(\d+\.?\d*)mm'])
    df['wide_focal_length'] = [int(Decimal(x) * 2) for x in w]
    df['telephoto_focal_length'] = [int(Decimal(x) * 2) for x in w]
    del df['焦点距離']
    del df['画角']
    del df['レンズ構成']

    w, t = extract_numbers(df['name'], [], [r'F(\d+\.?\d*)'])
    df['wide_f_number'] = [float(x) for x in w]
    df['telephoto_f_number'] = [float(x) for x in t]
    del df['口径比']
    del df['最小絞り']
    del df['絞り羽根枚数']

    w, t = extract_numbers(df['最短撮影距離'], [], [r'(\d+\.?\d+)m'])
    df['wide_min_focus_distance'] = [int(Decimal(x).scaleb(3)) for x in w]
    df['telephoto_min_focus_distance'] = [int(Decimal(x).scaleb(3)) for x in t]
    del df['最短撮影距離']

    m: List[str] = []
    for record in df['最大撮影倍率']:
        m.append(regex(record, r'1(:|：)(\d+\.?\d*)')[1])
    df['max_photographing_magnification'] = [float(str((Decimal(1.0) / Decimal(x)).quantize(Decimal('0.01')))) for x in m]
    del df['最大撮影倍率']

    m: List[int] = []
    for record in df['フィルターサイズ']:
        m.append(int(regex(record, r'(\d+)mm')[0]))
    df['filter_diameter'] = m
    del df['フィルターサイズ']

    df['is_drip_proof'] = False
    df['has_image_stabilization'] = False
    df['is_inner_zoom'] = True

    di, le = extract_numbers(df['最大径×全長'], [r'φ(\d+\.?\d*)×(\d+\.?\d*)mm'], [])
    df['overall_diameter'] = di
    df['overall_length'] = le
    del df['最大径×全長']

    weight, _ = extract_numbers(df['重量'], [], [r'(\d+)g'])
    df['weight'] = weight
    del df['重量']

    price, _ = extract_numbers(df['希望小売価格'], [], [r'￥([\d,]+)'])
    df['price'] = [int(x.replace(',', '')) for x in price]
    del df['希望小売価格']

    df['mount'] = 'マイクロフォーサーズ'
    df['url'] = df['URL']
    del df['レンズフード']
    del df['その他：']
    del df['URL']

    return df
