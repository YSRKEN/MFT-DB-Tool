from typing import List, Tuple, Dict

from pandas import DataFrame

from model.DomObject import DomObject
from service.i_scraping_service import IScrapingService


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

    # レンズごとに情報を取得する
    lens_data_list: List[Dict[str, str]] = []
    for lens_name, lens_product_number in lens_list:
        # 詳細ページから情報を取得する
        spec_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/spec.html'
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
        lens_data_list.append(temp_dict)

    df = DataFrame.from_records(lens_data_list)
    return df
