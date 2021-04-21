from decimal import Decimal
from pprint import pprint
from typing import List, Tuple, Dict

from pandas import DataFrame

from service.i_scraping_service import IScrapingService
from service.ulitity import convert_columns, extract_numbers, regex


def get_leica_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str]] = []
    page_list = [
        'https://us.leica-camera.com/Photography/Leica-SL/SL-Lenses/Prime-Lenses',
        'https://us.leica-camera.com/Photography/Leica-SL/SL-Lenses/Vario-Lenses'
    ]
    for page_url in page_list:
        page = scraping.get_page(page_url, cache=False)
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
        'レンズ名': 'name',
        'URL': 'url',
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

    # product_number
    df['product_number'] = df['Order number'].map(lambda x: x.replace(' ', ''))
    del df['Order number']

    # wide_focal_length, telephoto_focal_length
    w, t = extract_numbers(df['name'], [r'SL(\d+)-(\d+) f', r'SL (\d+)-(\d+) f'],
                           [r'SL(\d+) f', r'SL (\d+) f', r'SL 1:\d+\.?\d*/(\d+)'])
    df['wide_focal_length'] = w
    df['telephoto_focal_length'] = t

    # wide_f_number, telephoto_f_number
    w, t = extract_numbers(df['name'], [r'f/(\d+\.?\d*)-(\d+\.?\d*)'],
                           [r'f/(\d+\.?\d*)', r'SL 1:(\d+\.?\d*)/\d+'])
    df['wide_f_number'] = w
    df['telephoto_f_number'] = t

    # wide_min_focus_distance, telephoto_min_focus_distance
    w, t = extract_numbers(df['Working range'], [],
                           [r'(\d+\.?\d*)mm to', r'(\d+\.?\d*) m to', r'to (\d+\.?\d*) m'])
    # 微調整
    for i in range(0, len(df)):
        if 'mm to' not in df['Working range'].values[i]:
            w[i] = str(int(Decimal(w[i]).scaleb(3)))
            t[i] = str(int(Decimal(t[i]).scaleb(3)))
    df['wide_min_focus_distance'] = [int(x) for x in w]
    df['telephoto_min_focus_distance'] = [int(x) for x in t]
    del df['Working range']

    # max_photographing_magnification
    m: List[float] = []
    for record in df.to_records():
        denominator = regex(record['Largest reproduction ratio'], r'1:(\d+\.?\d*)')
        m.append(float((Decimal('1') / Decimal(denominator[0])).quantize(Decimal('0.01'))))
    df['max_photographing_magnification'] = m
    del df['Largest reproduction ratio']

    # filter_diameter
    df['filter_diameter'] = df['Filter mount'].map(lambda x: int(x.replace('E', '')))
    del df['Filter mount']

    # is_drip_proof, has_image_stabilization, is_inner_zoom
    is_drip_proof = []
    has_image_stabilization = []
    is_inner_zoom = []
    for record in df.to_records():
        is_drip_proof.append(False)
        if record['name'] in ['VARIO-ELMARIT-SL24-90 f/2.8-4 ASPH.', 'APO VARIO-ELMARIT-SL90-280 f/2.8-4']:
            has_image_stabilization.append(True)
        else:
            has_image_stabilization.append(False)
        if record['name'] in ['APO VARIO-ELMARIT-SL90-280 f/2.8-4'] or \
                record['wide_focal_length'] == record['telephoto_focal_length']:
            is_inner_zoom.append(True)
        else:
            is_inner_zoom.append(False)
    df['is_drip_proof'] = is_drip_proof
    df['has_image_stabilization'] = has_image_stabilization
    df['is_inner_zoom'] = is_inner_zoom

    # overall_diameter, overall_length
    overall_diameter = []
    overall_length = []
    for record in df.to_records():
        if '/' in record['Largest diameter']:
            diameter = regex(record['Largest diameter'].replace('\u2009', ' '), r'(\d+\.?\d*)/\d+ mm')
        elif ':' in record['Largest diameter']:
            diameter = regex(record['Largest diameter'].replace('\u2009', ' '), r': (\d+\.?\d*) mm')
        else:
            diameter = regex(record['Largest diameter'].replace('\u2009', ' '), r'(\d+\.?\d*) mm')
        if '/' in record['Length to bayonet mount']:
            length = regex(record['Length to bayonet mount'].replace('\u2009', ' '), r'(\d+\.?\d*)/\d+ mm')
        elif ':' in record['Length to bayonet mount']:
            length = regex(record['Length to bayonet mount'].replace('\u2009', ' '), r': (\d+\.?\d*) mm')
        else:
            length = regex(record['Length to bayonet mount'].replace('\u2009', ' '), r'(\d+\.?\d*) mm')
        overall_diameter.append(float(diameter[0]))
        overall_length.append(float(length[0]))
    df['overall_diameter'] = overall_diameter
    df['overall_length'] = overall_length
    del df['Largest diameter']
    del df['Length to bayonet mount']

    # weight
    weight: List[float] = []
    for i in range(0, len(df)):
        f = df['Weight'].values[i].replace('\u2009', ' ')
        result = regex(f, r'([\d.]+) g')
        if len(result) > 0:
            result2 = regex(f, r'([\d.]+)/[\d.]+ g')
            if len(result2) > 0:
                weight.append(int(result2[0].replace('.', '')))
            else:
                weight.append(int(result[0].replace('.', '')))
        else:
            weight.append(int(f))
    df['weight'] = weight
    del df['Weight']

    df['price'] = -1
    return df
