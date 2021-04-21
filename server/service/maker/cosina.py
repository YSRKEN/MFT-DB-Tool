from typing import List, Tuple, Dict

from pandas import DataFrame

from service.i_scraping_service import IScrapingService


lens_name_table = {
    '10.5mm F0.95': 'Voigtlander NOKTON 10.5mm F0.95 Aspherical',
    '17.5mm F0.95': 'Voigtlander NOKTON 17.5mm F0.95 Aspherical',
    '25mm Type2': 'Voigtlander NOKTON 25mm F0.95 TypeII',
    '29mm': 'Voigtlander SUPER NOKTON 29mm F0.8 Aspherical',
    '42.5mm F0.95': 'Voigtlander NOKTON 42.5mm F0.95',
    'mft60mm': 'Voigtlander NOKTON 60mm F0.95',
}


def get_cosina_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str]] = []
    page = scraping.get_page('http://www.cosina.co.jp/seihin/voigtlander/mft-mount/index.html',
                             encoding='cp932')
    for a_element in page.find_all('td > a'):
        lens_name = a_element.find('img').attrs['alt']
        lens_url = 'http://www.cosina.co.jp/seihin/voigtlander/mft-mount/' + a_element.attrs['href']
        if 'mm' in lens_name and 'mft' in a_element.attrs['href']:
            if lens_name not in lens_name_table:
                print(lens_name)
                raise Exception('未対応のレンズが含まれています')
            lens_list.append((lens_name_table[lens_name], lens_url))

    # レンズの情報を取得する
    temp_list: List[Dict[str, any]] = []
    for lens_name, lens_url in lens_list:
        page = scraping.get_page(lens_url, encoding='cp932')
        temp: Dict[str, str] = {'レンズ名': lens_name, 'URL': lens_url}
        for tr_element in page.find_all('tr'):
            td_elements = tr_element.find_all('td')
            if len(td_elements) < 2:
                continue
            if 'bgcolor' not in td_elements[0].attrs:
                continue
            if td_elements[0].full_text == '' or td_elements[1].full_text == '':
                continue
            temp[td_elements[0].full_text] = td_elements[1].full_text
        for h2_element in page.find_all('h2'):
            text = h2_element.text
            if '希望小売価格' in text:
                temp['希望小売価格'] = text.replace('\n', '')
        temp_list.append(temp)

    return DataFrame.from_records(temp_list)
