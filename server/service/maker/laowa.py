from typing import List, Tuple, Dict

from pandas import DataFrame

from service.i_scraping_service import IScrapingService
from service.ulitity import convert_columns


def get_laowa_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str]] = []
    page = scraping.get_page('https://www.laowa.jp/cat1/')
    for div_element in page.find_all('div.product3'):
        h3_element = div_element.find('h3')
        if h3_element is None:
            continue
        a_element = div_element.find('a')
        if a_element is None:
            continue
        lens_name = h3_element.text
        lens_url = a_element.attrs['href']
        if 'LAOWA' in lens_name and 'mm' in lens_name:
            lens_list.append((lens_name, lens_url))

    # レンズの情報を取得する
    lens_raw_data_list: List[Dict[str, any]] = []
    for lens_name, lens_url in lens_list:
        print(lens_name)
        page = scraping.get_page(lens_url)
        temp: Dict[str, str] = {'レンズ名': lens_name, 'URL': lens_url}
        section_element = page.find('div.productTable')
        if section_element is not None:
            for tr_element in section_element.find_all('tr'):
                td_elements = tr_element.find_all('td')
                if len(td_elements) < 2:
                    continue
                temp[td_elements[0].text] = td_elements[1].text
            lens_raw_data_list.append(temp)
    df = DataFrame.from_records(lens_raw_data_list)

    # 変換用に整形
    df['maker'] = 'LAOWA'
    df = convert_columns(df, {
        'レンズ名': 'name', 'URL': 'url', 'フォーマット': '対応フォーマット', '対応マウント': 'マウント',
        '寸法（鏡筒直径×長さ）': 'サイズ', '最小フォーカシングディスタンス': '最短撮影距離',
        '最大倍率比': '最大撮影倍率', '最大倍率': '最大撮影倍率',
        }, [
        '開放F値', '画角', 'レンズ構成', 'シフト機能', '最大イメージサークル', '絞り羽根枚数', 'フォーカス', 'JAN',
        '発売日', '絞り羽枚数', 'フォーカシング', 'フィルタースレッド', 'ワーキングディスタンス', '最大口径比',
        '絞り羽根枚数（F）', '絞り羽根枚数（T）', 'シフト量', '最小ワーキングディスタンス',
    ])
    del df[None]
    return df

