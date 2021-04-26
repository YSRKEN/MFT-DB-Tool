from decimal import Decimal
from typing import List, Tuple, Dict

from pandas import DataFrame

from service.i_scraping_service import IScrapingService
from service.ulitity import convert_columns, extract_numbers, regex


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
        page = scraping.get_page(lens_url)
        temp: Dict[str, str] = {'レンズ名': lens_name, 'URL': lens_url}
        section_element = page.find('div.productTable')
        if section_element is not None:
            for tr_element in section_element.find_all('tr'):
                td_elements = tr_element.find_all('td')
                if len(td_elements) < 2:
                    continue
                if td_elements[0].full_text is None or td_elements[1].full_text is None:
                    continue
                temp[td_elements[0].full_text] = td_elements[1].full_text
            # 特殊処理
            if temp['レンズ名'] == 'LAOWA 15mm F4 WIDE ANGLE MACRO':
                if 'Nikon' in temp['質量']:
                    # 記述が入れ替わっているので対策
                    temp2 = temp.copy()
                    temp2['マウント'] = temp['質量']
                    temp = temp2
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
        '絞り羽根枚数（F）', '絞り羽根枚数（T）', 'シフト量', '最小ワーキングディスタンス', '対応フォーマット',
    ])
    if None in df:
        del df[None]
    if '' in df:
        del df['']

    mount_list: List[str] = []
    for mount_temp in df['マウント']:
        if 'マイクロフォーサーズ' in mount_temp:
            mount_list.append('マイクロフォーサーズ')
        elif 'Leica L' in mount_temp:
            mount_list.append('ライカLマウント')
        else:
            mount_list.append('')
    df['mount'] = mount_list
    df = df[df['mount'] != '']
    del df['マウント']

    w_list, t_list = extract_numbers(df['焦点距離'], [r'(\d+\.?\d*)-(\d+\.?\d*)mm'], [r'(\d+\.?\d*)mm'])
    w_list2: List[int] = []
    t_list2: List[int] = []
    for w, t, mount in zip(w_list, t_list, list(df['mount'])):
        if mount == 'マイクロフォーサーズ':
            w_list2.append(int((Decimal(w) * 2).quantize(Decimal('1'))))
            t_list2.append(int((Decimal(t) * 2).quantize(Decimal('1'))))
        elif mount == 'ライカLマウント':
            w_list2.append(int(w))
            t_list2.append(int(t))
    df['wide_focal_length'] = w_list2
    df['telephoto_focal_length'] = t_list2
    del df['焦点距離']

    w, t = extract_numbers(df['name'], [r'F(\d+\.?\d*)-(\d+\.?\d*)'], [r'F(\d+\.?\d*)'])
    df['wide_f_number'] = [float(x) for x in w]
    df['telephoto_f_number'] = [float(x) for x in t]

    w_fd_list: List[int] = []
    t_fd_list: List[int] = []
    for fd in df['最短撮影距離'].values:
        result = regex(fd, r'(\d+.?\d*)mm～(\d+.?\d*)mm')
        if len(result) > 0:
            w_fd_list.append(int(result[0]))
            t_fd_list.append(int(result[1]))
            continue
        result = regex(fd, r'(\d+.?\d*)cm')
        if len(result) > 0:
            w_fd_list.append(int(Decimal(result[0]) * 10))
            t_fd_list.append(int(Decimal(result[0]) * 10))
            continue
        result = regex(fd, r'(\d+.?\d*)cｍ')
        if len(result) > 0:
            w_fd_list.append(int(Decimal(result[0]) * 10))
            t_fd_list.append(int(Decimal(result[0]) * 10))
            continue
        result = regex(fd, r'(\d+.?\d*)mm')
        if len(result) > 0:
            w_fd_list.append(int(result[0]))
            t_fd_list.append(int(result[0]))
            continue
        w_fd_list.append(0)
        t_fd_list.append(0)
    df['wide_min_focus_distance'] = w_fd_list
    df['telephoto_min_focus_distance'] = t_fd_list
    del df['最短撮影距離']

    return df

