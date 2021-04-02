from pprint import pprint
from typing import List, Tuple, Dict

from pandas import DataFrame

from model.DomObject import DomObject
from service.i_scraping_service import IScrapingService
from service.ulitity import extract_numbers


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
            print(lens_mount + '  ' + lens_name)
            print('  ' + lens_link)

            page = scraping.get_page(lens_link)
            temp_dict: Dict[str, str] = {
                'mount': lens_mount,
                'name': lens_name,
                'url': lens_link
            }
            temp_dict.update(item_page_to_raw_dict(page, lens_mount))
            lens_raw_data_list.append(temp_dict)
    for lens_name, lens_link in lens_list_old:
        print(lens_name)
        print('  ' + lens_link)

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

    return df

    # 変換用に整形
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
