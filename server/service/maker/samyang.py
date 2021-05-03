from pprint import pprint
from typing import List, Tuple, Dict

from pandas import DataFrame

from service.i_scraping_service import IScrapingService


def get_samyang_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str]] = []
    page = scraping.get_page('https://www.kenko-tokina.co.jp/camera-lens/samyang/', cache=False)
    for li_element in page.find_all('li.col.list_item'):
        lens_name = li_element.find('h3 > a').text
        lens_url = li_element.find('h3 > a').attrs['href']
        if 'data-spec3' in li_element.attrs:
            mount_info = li_element.attrs['data-spec3']
            if 'マイクロフォーサーズ' in mount_info:
                lens_list.append((lens_name, lens_url))

    # レンズの情報を取得する
    temp_list: List[Dict[str, any]] = []
    for lens_name, lens_url in lens_list:
        page = scraping.get_page(lens_url)
        print(lens_name)
    return DataFrame()
