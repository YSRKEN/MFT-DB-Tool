from pprint import pprint
from typing import List, Tuple, Dict

from pandas import DataFrame

from service.i_scraping_service import IScrapingService
from service.ulitity import convert_columns


def get_leica_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str]] = []
    page_list = [
        'https://us.leica-camera.com/Photography/Leica-SL/SL-Lenses/Prime-Lenses',
        'https://us.leica-camera.com/Photography/Leica-SL/SL-Lenses/Vario-Lenses'
    ]
    for page_url in page_list:
        page = scraping.get_page(page_url)
        for div_element in page.find_all('div.h2-text-image-multi-layout.module.no-border'):
            h2_element = div_element.find('h2.headline-40')
            if h2_element is None:
                continue
            span_element = h2_element.find('span')
            if span_element is None:
                continue
            a_element = div_element.find('a.red_cta')
            if a_element is None:
                continue
            lens_name = h2_element.full_text.replace(span_element.full_text, '').replace('\n', ' ')\
                .replace('–', '-').strip()
            lens_url = 'https://us.leica-camera.com' + a_element.attrs['href']
            if 'f/' not in lens_name and '-SL' not in lens_name:
                continue
            lens_list.append((lens_name, lens_url))

    # レンズの生情報を取得する
    lens_raw_data_list: List[Dict[str, any]] = []
    for lens_name, lens_url in lens_list:
        page = scraping.get_page(lens_url)
        temp: Dict[str, str] = {'レンズ名': lens_name, 'URL': lens_url}
        section_element = page.find('section.tech-specs')
        if section_element is not None:
            for tr_element in section_element.find_all('tr'):
                td_elements = tr_element.find_all('td')
                if len(td_elements) < 2:
                    continue
                temp[td_elements[0].text] = td_elements[1].text
            lens_raw_data_list.append(temp)
    df = DataFrame.from_records(lens_raw_data_list)

    # 変換用に整形
    df['maker'] = 'LEICA'
    df['mount'] = 'ライカLマウント'
    df = convert_columns(df, {
        'Order Number': 'Order number',
        'Order-number': 'Order number',
        'Focus range': 'Working range',
        'Largest scale': 'Largest reproduction ratio',
        'Filter thread': 'Filter mount',
        'Length': 'Length to bayonet mount',
        'Length to bayonet flange': 'Length to bayonet mount',
        'Diameter': 'Largest diameter',
    }, [
        'View angle (diagonal/horizontal/vertical) Full-frame (24 × 36 mm)',
        'Field angle (diagonal, horizontal, vertical)',
        'Angle of view (diagonal, horizontal, vertical)',
        'Number of lenses/assemblies',
        'Number of lenses/groups',
        'Number of elements/groups',
        'Number of aspherical surfaces',
        'Number of aspherical lenses',
        'Number of asph. surfaces / lenses',
        'Position of the entrance pupil before the bayonet',
        'Position of entrance pupil',
        'Setting',
        'Setting/Function',
        'Setting/function',
        'Aperture setting range',
        'Smallest aperture',
        'Lowest value',
        'Smallest value',
        'Bayonet',
        'Bayonet/sensor format',
        ' Bayonet/sensor format',
        'Lens mount/sensor format',
        'Lens hood',
        'O.I.S. Performance as per CIPA',
        'Entrance pupil position',
        'Smallest object field',
    ])

    return df
