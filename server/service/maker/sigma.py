from pprint import pprint
from typing import List, Tuple, Dict

from pandas import DataFrame

from model.DomObject import DomObject
from service.i_scraping_service import IScrapingService
from service.ulitity import extract_numbers


def get_sigma_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    page = scraping.get_page('https://www.sigma-global.com/jp/lenses/', cache=False)
    lens_list_mft: List[Tuple[str, str]] = []
    lens_list_l: List[Tuple[str, str]] = []
    for li_element in page.find('div.p-lens-search__main').find_all('li'):
        lens_link = 'https://www.sigma-global.com/' + li_element.find('a').attrs['href']
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
            print(lens_mount + '  ' + lens_name)
            print('  ' + lens_link)
    for lens_name, lens_link in lens_list_old:
        print(lens_name)
        print('  ' + lens_link)
    df = DataFrame.from_records(lens_raw_data_list)
    return df




    # レンズごとに情報を取得する
    lens_raw_data_list: List[Dict[str, any]] = []
    for lens_list, lens_mount in [(lens_list_mft, 'マイクロフォーサーズ'), (lens_list_l, 'ライカLマウント')]:
        for lens_name, lens_link in lens_list:
            # ざっくり情報を取得する
            page = scraping.get_page(lens_link + 'specifications/')
            temp_dict: Dict[str, str] = {
                'マウント': lens_mount
            }
            th_text = ''
            for tr_element in page.find('table').find_all('tr'):
                th_elements = tr_element.find_all('th')
                if len(th_elements) > 0:
                    th_text = th_elements[0].text
                td_elements = tr_element.find_all('td')
                if len(td_elements) == 1:
                    temp_dict[th_text] = td_elements[0].text
                elif len(td_elements) == 2:
                    temp_dict[th_text + ' ' + td_elements[0].text] = td_elements[1].text
            temp_dict['レンズ名'] = lens_name
            temp_dict['URL'] = lens_link

            page = scraping.get_page(lens_link + 'features/')
            if '防塵防滴' in page.full_text:
                temp_dict['防塵防滴'] = '○'

            if lens_mount == 'マイクロフォーサーズ':
                temp_dict['最大径 × 長さ'] = temp_dict['最大径 × 長さ マイクロフォーサーズ']
                temp_dict['質量'] = temp_dict['質量 マイクロフォーサーズ']
            if lens_mount == 'ライカLマウント':
                temp_dict['最大径 × 長さ'] = temp_dict['最大径 × 長さ Lマウント']
                temp_dict['質量'] = temp_dict['質量 Lマウント']

            lens_raw_data_list.append(temp_dict)

    for lens_name, lens_link in lens_list_old:
        # ざっくり情報を取得する
        page = scraping.get_page(lens_link)
        temp_dict: Dict[str, str] = {}
        for tr_element in page.find('table').find_all('tr'):
            th_elements = tr_element.find_all('th')
            if len(th_elements) > 0:
                th_text = th_elements[0].text.replace('\t', '').strip()
            else:
                continue
            td_elements = tr_element.find_all('td')
            if len(td_elements) == 1:
                temp_dict[th_text] = td_elements[0].text.strip()
        temp_dict['レンズ名'] = lens_name
        temp_dict['URL'] = lens_link

        if '最大倍率' in temp_dict:
            temp_dict['最大撮影倍率'] = temp_dict['最大倍率']

        for key, val in temp_dict.items():
            if '対応マウント' in key:
                if 'マイクロフォーサーズ' in temp_dict[key]:
                    temp_dict2 = temp_dict.copy()
                    temp_dict2['マウント'] = 'マイクロフォーサーズ'
                    temp_dict2['最大径 × 長さ'] = temp_dict2['最大径×全長']
                    lens_raw_data_list.append(temp_dict2)
                if 'ライカLマウント' in temp_dict[key]:
                    temp_dict2 = temp_dict.copy()
                    temp_dict2['マウント'] = 'ライカLマウント'
                    temp_dict2['最大径 × 長さ'] = temp_dict2['最大径×全長']
                    lens_raw_data_list.append(temp_dict2)
                break

    df = DataFrame.from_records(lens_raw_data_list)

    # 不要な列を削除
    del_column_list = [
        'レンズ構成枚数',
        '画角 ソニー Eマウント',
        '画角 キヤノンEF-Mマウント',
        '画角 マイクロフォーサーズ',
        '画角 Lマウント',
        '絞り羽根枚数',
        '最小絞り',
        '最大径 × 長さ ソニーEマウント',
        '最大径 × 長さ キヤノンEF-Mマウント',
        '質量 ソニーEマウント',
        '質量 キヤノンEF-Mマウント',
        '付属品',
        '最大径 × 長さ ソニー Eマウント',
        '質量 ソニー Eマウント',
        '画角 (35mm)',
        '画角（35mm判）',
        '画角',
        '最大径 × 長さ シグマSAマウント',
        '質量 シグマSAマウント',
        '画角（35mm判） Lマウント',
        '画角（35mm判） ソニー Eマウント',
        'レンズ構成',
        'JANコードナンバー',
        '対応マウント',
        '最大径×全長',
        '最大倍率',
        '最大径 × 長さ マイクロフォーサーズ',
        '最大径 × 長さ Lマウント',
        '質量 マイクロフォーサーズ',
        '質量 Lマウント'
    ]
    for column in del_column_list:
        if column in df:
            del df[column]

    # 変換用に整形
    print(df)
    df['maker'] = 'SIGMA'
    df['name'] = df['レンズ名']
    del df['レンズ名']
    df['product_number'] = df['エディションナンバー']
    del df['エディションナンバー']

    w, t = extract_numbers(df['レンズ名'], [r'(\d+)-(\d+)mm'], [r'(\d+)mm'])
    wide_focal_length: List[int] = []
    telephoto_focal_length: List[int] = []
    for wf, tf, mount, name in zip(w, t, df['マウント']. df['name']):
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
    df['wide_focal_length'] = df['wide_focal_length']
    df['telephoto_focal_length'] = df['telephoto_focal_length']

    return df
