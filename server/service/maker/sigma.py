from decimal import Decimal
from typing import List, Tuple, Dict

from pandas import DataFrame

from model.DomObject import DomObject
from service.i_scraping_service import IScrapingService
from service.ulitity import extract_numbers, regex


def item_page_to_raw_dict(page: DomObject, lens_mount: str) -> Dict[str, any]:
    if lens_mount == '':
        if 'マイクロフォーサーズ' not in page.full_text:
            return {}
        else:
            lens_mount_ = 'マイクロフォーサーズ'
    else:
        lens_mount_ = lens_mount
    output: Dict[str, any] = {}
    for div_element in page.find_all('div.p-spec-table__fields'):
        key_div_element = div_element.find('div.p-spec-table__header > h3')
        if key_div_element is None:
            key_div_element = div_element.find('header.p-spec-table__header > h3')
        key = key_div_element.text
        div_element2 = div_element.find('div.p-spec-table__td')
        ul_element = div_element2.find('ul')
        if ul_element is None:
            # 項目が1個しかないので簡単
            value = div_element2.text.strip().strip('\n').replace('\n', ' ')
            output[key] = value
        else:
            # レンズマウントごとに分類されるので注意する
            for li_element in ul_element.find_all('li'):
                if lens_mount_ == 'マイクロフォーサーズ' and 'マイクロフォーサーズ' in li_element.full_text:
                    value = li_element.full_text.replace('マイクロフォーサーズマウント', '').strip().strip('\n').replace('\n', ' ')
                    output[key] = value
                if lens_mount_ == 'ライカLマウント' and 'L マウント' in li_element.full_text:
                    value = li_element.full_text.replace('L マウント', '').strip().strip('\n').replace('\n', ' ')
                    output[key] = value
    return output


def get_sigma_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    page = scraping.get_page('https://www.sigma-global.com/jp/lenses/', cache=False)
    lens_list_mft: List[Tuple[str, str]] = []
    lens_list_l: List[Tuple[str, str]] = []
    for li_element in page.find('div.p-lens-search__main').find_all('li'):
        lens_link = li_element.find('a').attrs['href']
        if 'lenses' not in lens_link:
            continue
        h4_element = li_element.find('h4')
        if h4_element is None:
            continue
        lens_name = h4_element.text
        if 'micro-four-thirds' in li_element.attrs['data-lens-mount']:
            lens_list_mft.append((lens_name, lens_link))
        if 'l-mount' in li_element.attrs['data-lens-mount']:
            lens_list_l.append((lens_name, lens_link))

    page: DomObject = scraping.get_page('https://www.sigma-global.com/jp/lenses/discontinued/', cache=False)
    lens_list_old: List[Tuple[str, str]] = []
    for li_element in page.find_all('li.p-support-service__item'):
        a_element = li_element.find('a')
        lens_link = a_element.attrs['href']
        lens_name = a_element.find('h4 > span').text
        lens_list_old.append((lens_name, lens_link))

    # レンズごとに情報を取得する
    lens_raw_data_list: List[Dict[str, any]] = []
    for lens_list, lens_mount in [(lens_list_mft, 'マイクロフォーサーズ'), (lens_list_l, 'ライカLマウント')]:
        for lens_name, lens_link in lens_list:
            if 'lenses/c' in lens_link and '| Contemporary' not in lens_name:
                lens_name2 = lens_name + ' | Contemporary'
            elif 'lenses/a' in lens_link and '| Art' not in lens_name:
                lens_name2 = lens_name + ' | Art'
            else:
                lens_name2 = lens_name

            page = scraping.get_page(lens_link)
            temp_dict: Dict[str, str] = {
                'mount': lens_mount,
                'name': lens_name2,
                'url': lens_link
            }
            temp_dict.update(item_page_to_raw_dict(page, lens_mount))
            lens_raw_data_list.append(temp_dict)
    for lens_name, lens_link in lens_list_old:
        if 'DN' not in lens_name:
            # DNが含まれない＝ミラーレス用ではないので除外
            continue
        page = scraping.get_page(lens_link)
        temp_dict: Dict[str, str] = {
            'mount': 'マイクロフォーサーズ',
            'name': lens_name,
            'url': lens_link
        }
        temp_dict2 = item_page_to_raw_dict(page, '')
        if len(temp_dict2) > 0:
            temp_dict.update(temp_dict2)
            lens_raw_data_list.append(temp_dict)
    df = DataFrame.from_records(lens_raw_data_list)

    # 変換用に整形
    df['maker'] = 'SIGMA'
    df['product_number'] = df['エディションナンバー']
    del df['エディションナンバー']
    del df['レンズ構成枚数']
    del df['画角']
    del df['絞り羽根枚数']
    del df['最小絞り']
    del df['付属品']
    del df['対応マウント / バーコード']

    # focal_length
    w, t = extract_numbers(df['name'], [r'(\d+)-(\d+)mm'], [r'(\d+)mm'])
    wide_focal_length: List[int] = []
    telephoto_focal_length: List[int] = []
    for wf, tf, mount, name in zip(w, t, df['mount'], df['name']):
        if mount == 'マイクロフォーサーズ':
            wide_focal_length.append(int(wf) * 2)
            telephoto_focal_length.append(int(tf) * 2)
        else:
            if 'DC' in name:
                wide_focal_length.append(int(1.5 * int(wf)))
                telephoto_focal_length.append(int(1.5 * int(tf)))
            else:
                wide_focal_length.append(int(wf))
                telephoto_focal_length.append(int(tf))
    df['wide_focal_length'] = wide_focal_length
    df['telephoto_focal_length'] = telephoto_focal_length

    # f_number
    w, t = extract_numbers(df['name'], [r'F(\d+\.?\d*)-(\d+\.?\d*)'], [r'F(\d+\.?\d*)'])
    df['wide_f_number'] = [float(x) for x in w]
    df['telephoto_f_number'] = [float(x) for x in t]

    # min_focus_distance
    w, t = extract_numbers(df['最短撮影距離'],
                           [r'(\d+\.?\d*)-(\d+\.?\d*)cm', r'(\d+\.?\d*) \(W\)-(\d+\.?\d*) \(T\)cm',
                            r'(\d+\.?\d*)\(W\) - (\d+\.?\d*)\(T\)cm'],
                           [r'(\d+\.?\d*)cm'])

    df['wide_min_focus_distance'] = [int(Decimal(x).scaleb(1)) for x in w]
    df['telephoto_min_focus_distance'] = [int(Decimal(x).scaleb(1)) for x in t]
    del df['最短撮影距離']

    # max_photographing_magnification
    m: List[float] = []
    for record in df.to_records():
        temp = regex(record['最大撮影倍率'].replace('：', ':'), r'.*1:(\d+\.?\d*).*1:(\d+\.?\d*).*')
        if len(temp) > 0:
            if float(temp[0]) < float(temp[1]):
                denominator = temp[0]
            else:
                denominator = temp[1]
        else:
            temp = regex(record['最大撮影倍率'].replace('：', ':'), r'.*1:(\d+\.?\d*).*')
            denominator = temp[0]
        if record['mount'] == 'マイクロフォーサーズ':
            m.append(float((Decimal('2') / Decimal(denominator)).quantize(Decimal('0.01'))))
        else:
            if 'DC' in record['name']:
                m.append(float((Decimal('1.5') / Decimal(denominator)).quantize(Decimal('0.01'))))
            else:
                m.append(float((Decimal('1') / Decimal(denominator)).quantize(Decimal('0.01'))))
    df['max_photographing_magnification'] = m
    del df['最大撮影倍率']

    # filter_diameter
    filter_diameter: List[float] = []
    for f in df['フィルターサイズ']:
        if f == f:
            result = regex(f, r'(\d+.?\d*)mm')
            if len(result) > 0:
                filter_diameter.append(float(result[0]))
            else:
                filter_diameter.append(-1)
        else:
            filter_diameter.append(-1)
    df['filter_diameter'] = filter_diameter
    del df['フィルターサイズ']

    # is_drip_proof
    df['is_drip_proof'] = df['name'].map(lambda x: 'DC' in x or 'DG' in x)

    # has_image_stabilization
    df['has_image_stabilization'] = df['name'].map(lambda x: 'OS' in x)

    # is_inner_zoom
    is_inner_zoom: List[bool] = []
    for record in df.to_dict(orient='records'):
        is_inner_zoom.append(record['wide_focal_length'] == record['telephoto_focal_length'])
    df['is_inner_zoom'] = is_inner_zoom

    # overall_diameter, overall_length
    overall_diameter, overall_length = extract_numbers(df['最大径 × 長さ'], [r'(\d+\.?\d*)mm[^\d]*(\d+\.?\d*)mm'], [])
    for i in range(0, len(df)):
        # データが存在しない分については手動で埋める
        if df['name'].values[i] == '19mm F2.8 EX DN':
            overall_diameter[i] = '60.6'
            overall_length[i] = '45.7'
        elif df['name'].values[i] == '30mm F2.8 EX DN':
            overall_diameter[i] = '60.6'
            overall_length[i] = '38.6'
        elif df['name'].values[i] == '19mm F2.8 DN | Art':
            overall_diameter[i] = '60.8'
            overall_length[i] = '45.7'
        elif df['name'].values[i] == '30mm F2.8 DN | Art':
            overall_diameter[i] = '60.8'
            overall_length[i] = '40.5'
        elif df['name'].values[i] == '60mm F2.8 DN | Art':
            overall_diameter[i] = '60.8'
            overall_length[i] = '55.5'
    df['overall_diameter'] = [float(x) for x in overall_diameter]
    df['overall_length'] = [float(x) for x in overall_length]
    del df['最大径 × 長さ']

    # weight
    weight: List[float] = []
    for i in range(0, len(df)):
        f = df['質量'].values[i]
        if f != f:
            if df['name'].values[i] == '19mm F2.8 EX DN':
                weight.append(140)
            elif df['name'].values[i] == '30mm F2.8 EX DN':
                weight.append(130)
            elif df['name'].values[i] == '19mm F2.8 DN | Art':
                weight.append(160)
            elif df['name'].values[i] == '30mm F2.8 DN | Art':
                weight.append(140)
            elif df['name'].values[i] == '60mm F2.8 DN | Art':
                weight.append(190)
            continue
        result = regex(f, r'([\d,]+)g')
        if len(result) > 0:
            weight.append(int(result[0].replace(',', '')))
        else:
            weight.append(int(f))
    df['weight'] = weight
    del df['質量']

    # price
    price: List[float] = []
    for f in df['希望小売価格']:
        result = regex(f, r'([\d,]+) *円')
        if len(result) > 0:
            price.append(int(result[0].replace(',', '')))
        else:
            price.append(26240)  # アドホックな修正
    df['price'] = price
    del df['希望小売価格']

    return df
