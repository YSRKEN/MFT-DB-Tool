from decimal import Decimal
from typing import List

import pandas
from pandas import DataFrame

from model.DomObject import DomObject
from model.Lens import Lens
from service.i_scraping_service import IScrapingService
from service.ulitity import regex


def cleansing(s: str):
    return s.strip()


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
    df1.rename(columns={
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
        'メーカー希望小売価格': 'price'
    }, inplace=True)
    del df1['レンズ構成']
    del df1['絞り羽根 / 形状']
    del df1['最小絞り値']
    del df1['レンズコーティング']
    del df1['対角線画角']
    del df1['レンズキャップ']
    df1['mount'] = 'マイクロフォーサーズ'

    df2.rename(columns={
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
    }, inplace=True)
    del df2['レンズ構成']
    del df2['マウント']
    del df2['絞り羽根 / 形状']
    del df2['開放絞り']
    del df2['最小絞り']
    df2['mount'] = 'ライカL'

    # 結合
    df = pandas.concat([df1, df2])

    # 変換用に整形
    df['maker'] = 'Panasonic'

    # focal_length
    wide_focal_length: List[int] = []
    telephoto_focal_length: List[int] = []
    for focal_length in df['focal_length'].values:
        result = regex(focal_length, r'(\d+)mm～(\d+)mm')
        if len(result) > 0:
            wide_focal_length.append(int(result[0]))
            telephoto_focal_length.append(int(result[1]))
            continue
        result = regex(focal_length, r'(\d+)-(\d+)mm')
        if len(result) > 0:
            wide_focal_length.append(int(result[0]))
            telephoto_focal_length.append(int(result[1]))
            continue
        result = regex(focal_length, r'(\d+)mm')
        wide_focal_length.append(int(result[0]))
        telephoto_focal_length.append(int(result[0]))
    df['wide_focal_length'] = wide_focal_length
    df['telephoto_focal_length'] = telephoto_focal_length
    del df['focal_length']

    # f_number
    wide_f_number: List[float] = []
    telephoto_f_number: List[float] = []
    for name in df['name'].values:
        result = regex(name, r'F(\d+\.?\d*)-(\d+\.?\d*)')
        if len(result) > 0:
            wide_f_number.append(float(result[0]))
            telephoto_f_number.append(float(result[1]))
            continue
        result = regex(name, r'F(\d+\.?\d*)')
        wide_f_number.append(float(result[0]))
        telephoto_f_number.append(float(result[0]))
    df['wide_f_number'] = wide_f_number
    df['telephoto_f_number'] = telephoto_f_number

    # min_focus_distance
    wide_min_focus_distance: List[float] = []
    telephoto_min_focus_distance: List[float] = []
    for min_focus_distance in df['min_focus_distance'].values:
        result = regex(min_focus_distance, r'(\d+\.?\d+)m / (\d+\.?\d+)m')
        if len(result) > 0:
            wide_min_focus_distance.append(int(Decimal(result[0]).scaleb(3)))
            telephoto_min_focus_distance.append(int(Decimal(result[1]).scaleb(3)))
            continue
        result = regex(min_focus_distance, r'(\d+\.?\d+)m～∞.*(\d+\.?\d+)m～∞')
        if len(result) > 0:
            wide_min_focus_distance.append(int(Decimal(result[0]).scaleb(3)))
            telephoto_min_focus_distance.append(int(Decimal(result[1]).scaleb(3)))
            continue
        result = regex(min_focus_distance, r'(\d+\.?\d+)m')
        if len(result) > 0:
            wide_min_focus_distance.append(int(Decimal(result[0]).scaleb(3)))
            telephoto_min_focus_distance.append(int(Decimal(result[0]).scaleb(3)))
            continue
        result = regex(min_focus_distance, r'(\d+\.?\d+)m～∞')
        wide_min_focus_distance.append(int(Decimal(result[0]).scaleb(3)))
        telephoto_min_focus_distance.append(int(Decimal(result[0]).scaleb(3)))
    df['wide_min_focus_distance'] = wide_min_focus_distance
    df['telephoto_min_focus_distance'] = telephoto_min_focus_distance
    del df['min_focus_distance']

    return df
