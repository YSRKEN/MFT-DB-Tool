from decimal import Decimal
from typing import List, Dict, Tuple

import pandas
from pandas import DataFrame, Series

from service.i_scraping_service import IScrapingService
from service.ulitity import regex, extract_numbers


def cleansing(s: str):
    """文字列を正規化する"""
    return s.strip()


def convert_columns(df: DataFrame, rename_columns: Dict[str, str], delete_columns: List[str]) -> DataFrame:
    """DataFrameのカラム名を変換する

    Parameters
    ----------
    df DataFrame
    rename_columns リネームするカラム名
    delete_columns 削除するカラム名

    Returns
    -------
    加工後のDataFrame
    """
    df2 = df.rename(columns=rename_columns)
    for d_column in delete_columns:
        del df2[d_column]
    return df2


def get_panasonic_lens_list(scraping: IScrapingService) -> DataFrame:
    # 情報ページを開く
    page = scraping.get_page('https://panasonic.jp/dc/comparison.html', cache=False)

    # tableタグからデータを収集する
    df1 = DataFrame()
    for table_element in page.find_all('table'):
        if 'LUMIX G' not in table_element.full_text:
            continue
        df1['レンズ名'] = [cleansing(x.text) for x in table_element.find_all('th p')]
        df1['URL'] = ['https://panasonic.jp' + x.attrs['href'] for x in table_element.find_all('th a')]
        for tr_element in table_element.find_all('tbody > tr'):
            key = cleansing(tr_element.find('th').text)
            value = [cleansing(x.text) for x in tr_element.find_all('td')]
            df1[key] = value
        break

    df2 = DataFrame()
    for table_element in page.find_all('table'):
        if 'LUMIX S' not in table_element.full_text:
            continue
        df2['レンズ名'] = [cleansing(x.text) for x in table_element.find_all('th p')]
        df2['URL'] = ['https://panasonic.jp' + x.attrs['href'] for x in table_element.find_all('th a')]
        for tr_element in table_element.find_all('tbody > tr'):
            if tr_element.find('th') is None:
                continue
            key = cleansing(tr_element.find('th').text)
            value = [cleansing(x.text) for x in tr_element.find_all('td')]
            df2[key] = value
        # なぜか、「最大径×全長」だけ記述位置が異なるので対策
        key = cleansing(table_element.find('tbody > th').text)
        value = [cleansing(x.text) for x in table_element.find_all('tbody > td')]
        df2[key] = value
        break

    # データを加工し、結合できるように整える
    df1 = convert_columns(df1, {
        'レンズ名': 'name',
        'URL': 'url',
        '品番': 'product_number',
        '35mm判換算焦点距離': 'focal_length',
        '最短撮影距離': 'min_focus_distance',
        '最大撮影倍率': 'max_photographing_magnification',
        '手ブレ補正': 'has_image_stabilization',
        'フィルターサイズ': 'filter_diameter',
        '最大径×全長': 'overall_size',
        '質量': 'weight',
        '防塵・防滴': 'is_drip_proof',
        'メーカー希望小売価格': 'price',
    }, [
        'レンズ構成',
        '絞り羽根 / 形状',
        '最小絞り値',
        'レンズコーティング',
        '対角線画角',
        'レンズキャップ',
    ])
    df1['mount'] = 'マイクロフォーサーズ'

    df2 = convert_columns(df2, {
        'レンズ名': 'name',
        'URL': 'url',
        '品番': 'product_number',
        '焦点距離': 'focal_length',
        '撮影距離範囲': 'min_focus_distance',
        '手ブレ補正': 'has_image_stabilization',
        'フィルター径': 'filter_diameter',
        '防塵・防滴': 'is_drip_proof',
        '最大撮影倍率': 'max_photographing_magnification',
        '最大径×全長': 'overall_size',
        '質量': 'weight',
        'メーカー希望小売価格': 'price'
    }, [
        'レンズ構成',
        'マウント',
        '絞り羽根 / 形状',
        '開放絞り',
        '最小絞り',
    ])
    df2['mount'] = 'ライカL'

    # 結合
    df = pandas.concat([df1, df2])

    # 変換用に整形
    df['maker'] = 'Panasonic'

    # focal_length
    w, t = extract_numbers(df['focal_length'], [r'(\d+)mm～(\d+)mm', r'(\d+)-(\d+)mm'], [r'(\d+)mm'])
    df['wide_focal_length'] = [int(x) for x in w]
    df['telephoto_focal_length'] = [int(x) for x in t]
    del df['focal_length']

    # f_number
    w, t = extract_numbers(df['name'], [r'F(\d+\.?\d*)-(\d+\.?\d*)'], [r'F(\d+\.?\d*)'])
    df['wide_f_number'] = [float(x) for x in w]
    df['telephoto_f_number'] = [float(x) for x in t]

    # min_focus_distance
    w, t = extract_numbers(df['min_focus_distance'],
                           [r'(\d+\.?\d+)m / (\d+\.?\d+)m', r'(\d+\.?\d+)m～∞.*(\d+\.?\d+)m～∞'],
                           [r'(\d+\.?\d+)m', r'(\d+\.?\d+)m～∞'])
    df['wide_min_focus_distance'] = [int(Decimal(x).scaleb(3)) for x in w]
    df['telephoto_min_focus_distance'] = [int(Decimal(x).scaleb(3)) for x in t]
    del df['min_focus_distance']

    # max_photographing_magnification
    m: List[float] = []
    for record in df.to_records():
        temp = record['max_photographing_magnification'].replace('倍', '')
        if record['mount'] == 'マイクロフォーサーズ':
            m.append(float(Decimal(temp) * 2))
        else:
            m.append(float(temp))
    df['max_photographing_magnification'] = m

    # filter_diameter
    filter_diameter: List[float] = []
    for f in df['filter_diameter']:
        result = regex(f, r'(\d+.?\d*)mm')
        if len(result) > 0:
            filter_diameter.append(float(result[0]))
        else:
            filter_diameter.append(-1)
    df['filter_diameter'] = filter_diameter

    # is_drip_proof
    df['is_drip_proof'] = df['is_drip_proof'].map(lambda x: x == '○')

    # has_image_stabilization
    df['has_image_stabilization'] = df['has_image_stabilization'].map(lambda x: x != '－')

    # is_inner_zoom
    i: List[bool] = []
    for record in df.to_records():
        if record['wide_focal_length'] == record['telephoto_focal_length']:
            i.append(True)
            continue
        if record['product_number'] in ['H-F007014', 'H-E08018', 'H-PS45175', 'S-E70200', 'S-R70200']:
            i.append(True)
            continue
        i.append(False)
    df['is_inner_zoom'] = i

    # overall_diameter, overall_length
    d, le = extract_numbers(df['overall_size'], [r'(\d+\.?\d*)mm[^\d]*(\d+\.?\d*)mm'], [])
    df['overall_diameter'] = [float(x) for x in d]
    df['overall_length'] = [float(x) for x in le]
    del df['overall_size']

    # weight
    weight: List[float] = []
    for f in df['weight']:
        result = regex(f, r'([\d,]+)g')
        if len(result) > 0:
            weight.append(int(result[0].replace(',', '')))
        else:
            weight.append(-1)
    df['weight'] = weight

    # price
    price: List[float] = []
    for f in df['price']:
        result = regex(f, r'([\d,]+) *円')
        if len(result) > 0:
            price.append(int(result[0].replace(',', '')))
        else:
            price.append(-1)
    df['price'] = price
    return df
