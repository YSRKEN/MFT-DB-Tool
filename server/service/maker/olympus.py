import warnings
from decimal import Decimal
from typing import List, Tuple, Dict

from pandas import DataFrame
from pandas.core.common import SettingWithCopyWarning

from model.DomObject import DomObject
from service.i_scraping_service import IScrapingService
from service.ulitity import extract_numbers, regex


def get_olympus_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    page = scraping.get_page('https://www.olympus-imaging.jp/product/dslr/mlens/index.html', cache=False)
    lens_list: List[Tuple[str, str]] = []
    for a_element in page.find_all('h2.productName > a'):
        lens_name = a_element.text.split('/')[0].replace('\n', '')
        if 'M.ZUIKO' not in lens_name:
            continue
        lens_product_number = a_element.attrs['href'].replace('/product/dslr/mlens/', '').replace('/index.html', '')
        lens_list.append((lens_name, lens_product_number))

    page = scraping.get_page('https://www.olympus-imaging.jp/product/dslr/record/index.html', cache=False)
    for a_element in page.find_all('div.section'):
        div_element = a_element.find('div.mb15 > h2')
        a_element2 = a_element.find('li > a')
        if div_element is None or a_element2 is None:
            continue
        lens_name = div_element.text
        if 'M.ZUIKO DIGITAL' not in lens_name:
            continue
        lens_product_number = a_element2.attrs['href'].replace('/product/dslr/mlens/', '').replace('/index.html', '')
        lens_list.append((lens_name, lens_product_number))

    # レンズごとに情報を取得する
    lens_data_list: List[Dict[str, str]] = []
    for lens_name, lens_product_number in lens_list:
        # 詳細ページから情報を取得する
        if lens_product_number != '14-42_35-56':
            spec_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/spec.html'
        else:
            spec_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/spec/index.html'
        page = scraping.get_page(spec_url)
        temp_dict: Dict[str, str] = {}
        for tr_element in page.find('table').find_all('tr'):
            tr_element: DomObject = tr_element

            # th側は、spanで囲まれてたりstrongで囲まれてたりするクソ仕様なので、力技で解決させた
            th_element = tr_element.find('th > span')
            if th_element is None:
                th_element = tr_element.find('th > strong')
            if th_element is None:
                th_element = tr_element.find('th')

            # td側はそのまま
            td_element = tr_element.find('td')

            # 合体
            temp_dict[th_element.text] = td_element.text

        # 製品トップページから情報を取得する
        index_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/index.html'
        page = scraping.get_page(index_url)
        temp_dict['URL'] = index_url
        table_element = page.find('table')
        # 詳細ページとはth・tdの拾い方を変えているのは、
        # M.ZUIKO DIGITAL ED 30mm F3.5 Macroの製品トップページの時のみ、
        # 希望小売価格「だけ」が取得できない不具合があったため
        for th_element, td_element in zip(table_element.find_all('th'), table_element.find_all('td')):
            th_element2 = th_element.find('span')
            if th_element2 is None:
                th_element2 = th_element.find('strong')
            if th_element2 is None:
                th_element2 = th_element
            temp_dict[th_element2.text] = td_element.text

        # 必要な列を追加
        temp_dict['name'] = lens_name
        temp_dict['product_number'] = lens_product_number

        # 不要な列を削除
        del_column_list = [
            'レンズ構成',
            'フォーカシング方式',
            'AF方式',
            '特長',
            'マウント規格',
            '画角',
            '最近接撮影範囲',
            '絞り羽枚数',
            '同梱品',
            '主な同梱品',
            '別売りアクセサリー',
            '別売アクセサリー',
            '製品名',
            'JANコード',
            'JAN',
            '発売日',
            'オンラインショップ',
            'フード',
            '最大口径比',
            '最小口径比',
            '最大口径比／最小口径比',
            '35mm判換算最大撮影倍率',
            '最大撮影倍率（35mm判換算）',
            '手ぶれ補正性能',
            'ズーム',
            'ズーム方式',
        ]
        for column in del_column_list:
            if column in temp_dict:
                del temp_dict[column]

        # 一部列だけ列名を変更しないと結合できないので対処
        if '大きさ　最大径×長さ' in temp_dict:
            temp_dict['大きさ 最大径×全長'] = temp_dict['大きさ　最大径×長さ']
            del temp_dict['大きさ　最大径×長さ']
        if '大きさ　最大径 × 全長' in temp_dict:
            temp_dict['大きさ 最大径×全長'] = temp_dict['大きさ　最大径 × 全長']
            del temp_dict['大きさ　最大径 × 全長']
        if '大きさ　最大径×全長' in temp_dict:
            temp_dict['大きさ 最大径×全長'] = temp_dict['大きさ　最大径×全長']
            del temp_dict['大きさ　最大径×全長']
        if '大きさ 最大径 x 全長' in temp_dict:
            temp_dict['大きさ 最大径×全長'] = temp_dict['大きさ 最大径 x 全長']
            del temp_dict['大きさ 最大径 x 全長']
        if '防滴性能 / 防塵機構' in temp_dict:
            temp_dict['防滴処理'] = temp_dict['防滴性能 / 防塵機構']
            del temp_dict['防滴性能 / 防塵機構']
        if '価格' in temp_dict:
            temp_dict['希望小売価格'] = temp_dict['価格']
            del temp_dict['価格']
        lens_data_list.append(temp_dict)

    df = DataFrame.from_records(lens_data_list)

    # 変換用に整形
    df['maker'] = 'OLYMPUS'

    # focal_length
    w, t = extract_numbers(df['焦点距離'], [r'(\d+)-(\d+)mm', r'(\d+) - (\d+)mm'], [r'(\d+)mm'])
    df['wide_focal_length'] = [int(x) * 2 for x in w]
    df['telephoto_focal_length'] = [int(x) * 2 for x in t]
    # M.ZUIKO DIGITAL　ED 150-400mm F4.5 TC1.25x IS PROは内蔵テレコンを持つので、その対策
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', SettingWithCopyWarning)
        df.telephoto_focal_length[df.product_number == '150-400_45ispro'] = 1000
    del df['焦点距離']

    # f_number
    w, t = extract_numbers(df['name'], [r'F(\d+\.?\d*)-(\d+\.?\d*)'], [r'F(\d+\.?\d*)'])
    df['wide_f_number'] = [float(x) for x in w]
    df['telephoto_f_number'] = [float(x) for x in t]

    # min_focus_distance
    w, t = extract_numbers(df['最短撮影距離'],
                           [r'(\d+\.?\d+)m（.+） / (\d+\.?\d+)m（.+）',
                            r'(\d+\.?\d+)m \(.+\) / (\d+\.?\d+)m \(.+\)',
                            r'(\d+\.?\d+)m.+／(\d+\.?\d+)m.+'],
                           [r'(\d+\.?\d+)m', r'(\d+\.?\d+) m'])
    df['wide_min_focus_distance'] = [int(Decimal(x).scaleb(3)) for x in w]
    df['telephoto_min_focus_distance'] = [int(Decimal(x).scaleb(3)) for x in t]
    del df['最短撮影距離']

    # max_photographing_magnification
    w, t = extract_numbers(df['最大撮影倍率'],
                           [r'(\d+\.?\d+)倍（35mm判換算 ?(\d+\.?\d+)倍相当）',
                            r'(\d+\.?\d+)倍（Wide） / (\d+\.?\d+)倍（Tele）',
                            r'(\d+\.?\d+)倍（Wide）/ (\d+\.?\d+)倍（Tele）'],
                           [r'^(\d+\.?\d+)倍'])
    m: List[float] = []
    for a, b, text in zip(w, t, df['最大撮影倍率'].values):
        if a == b:
            mm = float(Decimal(a) * 2)
        elif '換算' in text:
            mm = max(float(Decimal(a)), float(Decimal(b)))
        else:
            mm = max(float(Decimal(a)), float(Decimal(b))) * 2
        m.append(mm)
    df['max_photographing_magnification'] = m
    del df['最大撮影倍率']

    # filter_diameter
    filter_diameter: List[float] = []
    for f in df['フィルターサイズ']:
        if f != f:
            filter_diameter.append(-1)
            continue
        result = regex(f, r'(\d+.?\d*)mm')
        if len(result) > 0:
            filter_diameter.append(float(result[0]))
        else:
            filter_diameter.append(-1)
    df['filter_diameter'] = filter_diameter
    del df['フィルターサイズ']

    # is_drip_proof
    df['is_drip_proof'] = df['防滴処理'].map(lambda x: x == x and x != '')
    del df['防滴処理']

    # has_image_stabilization
    df['has_image_stabilization'] = df['name'].map(lambda x: 'IS' in x)
    del df['レンズ内手ぶれ補正機構']

    # is_inner_zoom
    i: List[bool] = []
    for record in df.to_records():
        if record['wide_focal_length'] == record['telephoto_focal_length']:
            i.append(True)
            continue
        if record['product_number'] in ['7-14_28pro', '40-150_28pro', '150-400_45ispro']:
            i.append(True)
            continue
        i.append(False)
    df['is_inner_zoom'] = i

    # overall_diameter, overall_length
    d, le = extract_numbers(df['大きさ 最大径×全長'], [
        r'φ(\d+.?\d*)x(\d+.?\d*)mm',
        r'Ø(\d+.?\d*)×(\d+.?\d*)mm',
        r'Φ (\d+.?\d*) mm  ｘ (\d+.?\d*) mm',
        r'⌀(\d+.?\d*) x (\d+.?\d*)mm',
        r'Ø(\d+.?\d*) × (\d+.?\d*)mm',
        r'Ø(\d+.?\d*) x (\d+.?\d*)mm',
        r'Ø(\d+.?\d*)mm x (\d+.?\d*)mm',
        r'Ø(\d+.?\d*)x (\d+.?\d*)mm',
        r'Ø(\d+.?\d*)x(\d+.?\d*)mm',
        r'⌀(\d+.?\d*)×(\d+.?\d*)mm',
        r'Ø(\d+.?\d*)mm × (\d+.?\d*)mm'], [])
    df['overall_diameter'] = [float(x) for x in d]
    df['overall_length'] = [float(x) for x in le]
    del df['大きさ 最大径×全長']

    # weight
    weight: List[float] = []
    for f in df['質量']:
        result = regex(f, r'([\d,]+)[^\d]*(g|ｇ)')
        if len(result) > 0:
            weight.append(int(result[0].replace(',', '')))
        else:
            weight.append(-1)
    df['weight'] = weight
    del df['質量']

    # price
    price: List[float] = []
    for f in df['希望小売価格']:
        result = regex(f, r'([\d,]+)円')
        if len(result) > 0:
            price.append(int(result[0].replace(',', '')))
        else:
            price.append(-1)
    df['price'] = price
    del df['希望小売価格']

    # mount・url
    df['mount'] = 'マイクロフォーサーズ'
    df['url'] = df['URL']
    del df['URL']
    return df
