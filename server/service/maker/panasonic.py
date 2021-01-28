from typing import List

import pandas
from pandas import DataFrame

from model.DomObject import DomObject
from model.Lens import Lens
from service.i_scraping_service import IScrapingService


def cleansing(s: str):
    return s.strip()


def get_panasonic_lens_list(scraping: IScrapingService) -> List[Lens]:
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
        '最大撮影倍率': 'photographing_magnification',
        '手ブレ補正': 'image_stabilization',
        'フィルターサイズ': 'filter_diameter',
        '最大径×全長': 'size',
        '質量': 'weight',
        '防塵・防滴': 'drip_proof',
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
        '手ブレ補正': 'image_stabilization',
        'フィルター径': 'filter_diameter',
        '防塵・防滴': 'drip_proof',
        '最大撮影倍率': 'photographing_magnification',
        '最大径×全長': 'size',
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

    df.to_csv('df.csv', index=False, encoding='utf_8_sig')

    return []
