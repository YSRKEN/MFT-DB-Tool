import math
from decimal import Decimal
from pprint import pprint
from typing import List, Tuple, Dict

from pandas import DataFrame

from service.i_scraping_service import IScrapingService
from service.ulitity import extract_numbers, regex


def get_samyang_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str, str]] = []
    page = scraping.get_page('https://www.kenko-tokina.co.jp/camera-lens/samyang/', cache=False)
    for li_element in page.find_all('li.col.list_item'):
        lens_name = li_element.find('h3 > a').text
        lens_url = li_element.find('h3 > a').attrs['href']
        if 'data-spec3' in li_element.attrs:
            mount_info = li_element.attrs['data-spec3']
            if 'マイクロフォーサーズ' in mount_info:
                lens_list.append((lens_name, lens_url, 'マイクロフォーサーズ'))

    # レンズの情報を取得する
    temp_list: List[Dict[str, any]] = []
    for lens_name, lens_url, lens_mount in lens_list:
        page = scraping.get_page(lens_url)
        for table_element in page.find_all('table'):
            temp: Dict[str, any] = {
                'name': lens_name,
                'url': lens_url,
                'mount': lens_mount
            }
            for tr_element in table_element.find_all('tr'):
                th_element = tr_element.find('th')
                td_element = tr_element.find('td')
                if th_element.text == '大きさ' or th_element.text == '全長' or th_element.text == '質量' or th_element.text == '重さ':
                    # 大きさや質量はマウント毎に異なるので特殊処理を実施
                    temp2 = td_element.html.replace('<td>', '').replace('</td>', '').replace('\n', '').split('<br>')
                    temp3 = ''
                    for temp4 in temp2:
                        if 'マイクロフォーサーズ' in temp4:
                            temp3 = temp4
                            break
                    if temp3 == '':
                        for temp4 in temp2:
                            if 'ソニーE' in temp4:
                                temp3 = temp4
                                break
                        if temp3 == '':
                            temp3 = temp2[0]
                    temp[th_element.text] = temp3.replace('\n', '')
                else:
                    temp[th_element.text] = td_element.text
            if len(temp) > 0:
                temp_list.append(temp)
    df = DataFrame.from_records(temp_list)

    # 変換用に整形
    df['maker'] = 'SAMYANG'
    df['price'] = 0
    del df['レンズ構成']
    del df['レンズフード']
    del df['マウント']
    del df['JANコード']
    del df['フォーマットサイズ']
    del df['絞り羽根']
    del df['絞り羽根枚数']
    del df['付属品']
    del df['JANコード：']

    w, t = extract_numbers(df['焦点距離'], [], [r'(\d+\.?\d*)mm'])
    df['wide_focal_length'] = [int(Decimal(x) * 2) for x in w]
    df['telephoto_focal_length'] = [int(Decimal(x) * 2) for x in w]
    del df['焦点距離']
    del df['画角']

    w, t = extract_numbers(df['name'], [], [r'F(\d+\.?\d*)'])
    df['wide_f_number'] = [float(x) for x in w]
    df['telephoto_f_number'] = [float(x) for x in t]
    del df['明るさ']
    del df['絞り']

    w: List[int] = []
    t: List[int] = []
    for fd in df['最短撮影距離'].values:
        result = regex(fd, r'(\d+.?\d*)cm')
        if len(result) > 0:
            w.append(int(Decimal(result[0]) * 10))
            t.append(int(Decimal(result[0]) * 10))
            continue
        result = regex(fd, r'(\d+.?\d*)( *)m')
        if len(result) > 0:
            w.append(int(Decimal(result[0]) * 1000))
            t.append(int(Decimal(result[0]) * 1000))
            continue
        w.append(0)
        t.append(0)
    df['wide_min_focus_distance'] = w
    df['telephoto_min_focus_distance'] = t
    del df['最短撮影距離']

    mag_list: List[float] = []
    for val1, val2 in zip(df['最大撮影倍率'].values, df['mount'].values):
        value = Decimal(0)
        while True:
            if val1 != val1:
                break
            result = regex(val1, r'(\d+.?\d*)倍')
            if len(result) > 0:
                value = Decimal(result[0])
                break
            break
        if val2 == 'マイクロフォーサーズ':
            mag_list.append(float(value * 2))
        else:
            mag_list.append(float(value))
    df['max_photographing_magnification'] = mag_list
    del df['最大撮影倍率']

    fd_list: List[float] = []
    for record in df.to_dict(orient='records'):
        text = record['フィルターサイズ']
        if text != text:
            text = record['フィルター径']
        result = regex(text, r'(\d+.?\d*)mm')
        if len(result) == 0:
            fd_list.append(-1)
            continue
        fd_list.append(int(result[0]))
    df['filter_diameter'] = fd_list
    del df['フィルターサイズ']
    del df['フィルター径']

    df['is_drip_proof'] = False
    df['has_image_stabilization'] = False

    i: List[bool] = []
    for record in df.to_records():
        if record['wide_focal_length'] == record['telephoto_focal_length']:
            i.append(True)
            continue
        i.append(False)
    df['is_inner_zoom'] = i

    diameter_list: List[float] = []
    length_list: List[float] = []
    for record in df.to_dict(orient='records'):
        text = record['大きさ']
        if text == text:
            result = regex(text, r'(\d+.?\d*)[^\d.]+(\d+.?\d*) *mm')
            if len(result) != 2:
                diameter_list.append(-1)
                length_list.append(-1)
            else:
                length_list.append(float(result[0].replace('×', '')))
                diameter_list.append(float(result[1]))
        else:
            text = record['最大径']
            if text == text:
                result = regex(text, r'(\d+.?\d*)')
                if len(result) > 0:
                    diameter_list.append(float(result[0]))
                else:
                    diameter_list.append(-1)
            else:
                diameter_list.append(-1)

            text = record['全長']
            if text == text:
                result = regex(text, r'(\d+.?\d*)')
                if len(result) > 0:
                    length_list.append(float(result[0]))
                else:
                    length_list.append(-1)
            else:
                length_list.append(-1)
    df['overall_diameter'] = diameter_list
    df['overall_length'] = length_list
    del df['大きさ']
    del df['最大径']
    del df['全長']

    weight_list: List[float] = []
    for record in df.to_dict(orient='records'):
        text = record['質量']
        if text != text:
            text = record['重さ']
        result = regex(text, r'(\d+.?\d*)g')
        if len(result) == 0:
            weight_list.append(-1)
            continue
        weight_list.append(int(float(result[0]) + 0.5))
    df['weight'] = weight_list
    del df['質量']
    del df['重さ']
    return df
