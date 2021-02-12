from pprint import pprint
from typing import List, Tuple, Dict

from pandas import DataFrame

from service.i_scraping_service import IScrapingService


def get_sigma_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    page = scraping.get_page('https://www.sigma-global.com/jp/lenses/#/all/micro-four-thirds/', cache=False)
    lens_list_mft: List[Tuple[str, str]] = []
    for li_element in page.find_all('li.micro-four-thirds'):
        lens_link = 'https://www.sigma-global.com/' + li_element.find('a').attrs['href']
        if 'product' not in lens_link:
            continue
        lens_name = li_element.find('b').text
        lens_list_mft.append((lens_name, lens_link))

    page = scraping.get_page('https://www.sigma-global.com/jp/lenses/#/all/l-mount/', cache=False)
    lens_list_l: List[Tuple[str, str]] = []
    for li_element in page.find_all('li.l-mount'):
        lens_link = 'https://www.sigma-global.com/' + li_element.find('a').attrs['href']
        if 'product' not in lens_link:
            continue
        lens_name = li_element.find('b').text
        lens_list_l.append((lens_name, lens_link))

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

            lens_raw_data_list.append(temp_dict)

    df = DataFrame.from_records(lens_raw_data_list)
    return df
