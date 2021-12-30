from decimal import Decimal
from typing import List, Tuple, Dict

from pandas import DataFrame, Series

from service.i_scraping_service import IScrapingService
from service.ulitity import convert_columns, extract_numbers, regex


def get_leica_lens_list(scraping: IScrapingService) -> DataFrame:
    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str]] = []
    page_index = 0
    while True:
        page_url = f'https://leica-camera.com/en-US/photography/lenses/sl?field_pim_categories=&page={page_index}'
        page = scraping.get_page(page_url, cache=False)
        article_elements = page.find_all('article.content-teasers-item')
        if len(article_elements) == 0:
            break
        page_index += 1
        for article_element in article_elements:
            lens_name = article_element.find('div.field--name-external-field-main-product-title'
                                             ).full_text
            if 'SL' not in lens_name:
                continue
            if 'Leica' not in lens_name:
                continue
            if 'hood' in lens_name:
                continue
            lens_url = 'https://leica-camera.com' + article_element.find('a.node-link').attrs['href']
            lens_list.append((lens_name, lens_url))

    # レンズの生情報を取得する
    lens_raw_data_list: List[Dict[str, any]] = []
    for lens_name, lens_url in lens_list:
        page = scraping.get_page(lens_url)
        temp: Dict[str, str] = {'レンズ名': lens_name, 'URL': lens_url}
        for tr_element in page.find_all('tr'):
            td_elements = tr_element.find_all('td')
            if len(td_elements) < 2:
                continue
            temp[td_elements[0].text] = td_elements[1].text
        lens_raw_data_list.append(temp)
    df = DataFrame.from_records(lens_raw_data_list)

    # 変換用に整形
    df['maker'] = 'LEICA'
    df['mount'] = 'ライカL'
    df = convert_columns(df, {
        'レンズ名': 'name',
        'URL': 'url',
        'Order Number': 'Order number',
        'Largest scale': 'Largest reproduction ratio',
        'Filter thread': 'Filter mount',
        'Length': 'Length to bayonet mount',
        'Diameter': 'Largest diameter',
        'Black, anodized': 'Order number',
        'Length to bayonet flange': 'Length to bayonet mount',
        'Focus range': 'Working range',
    }, [
        'Field angle (diagonal, horizontal, vertical)',
        'Number of lenses/groups',
        'Number of asph. surfaces / lenses',
        'Entrance pupil position',
        'Smallest object field',
        'Setting/function',
        'Aperture setting range',
        'Lowest value',
        'Bayonet/sensor format',
        'View angle (diagonal/horizontal/vertical) Full-frame (24 × 36 mm)',
        'Number of lenses/assemblies',
        'Number of aspherical surfaces',
        'Position of the entrance pupil before the bayonet',
        'Setting',
        'Setting/Function',
        'Smallest aperture',
        'Bayonet',
        'Lens hood',
        'Full-frame (24 × 36 mm)',
        'Angle of view (diagonal, horizontal, vertical)',
        'Number of elements/groups',
        'Position of entrance pupil',
        'Smallest value',
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
    w: List[int] = []
    t: List[int] = []
    for record in list(df['Working range'].values):
        match_result = regex(record, r'(\d+,\d*) m to infinity.+(\d+,\d*) m to infinity')
        if len(match_result) > 0:
            w.append(int(Decimal(match_result[0].replace(',', '.')).scaleb(3)))
            t.append(int(Decimal(match_result[1].replace(',', '.')).scaleb(3)))
            continue
        match_result = regex(record, r'(\d+\.?\d*) m to infinity')
        if len(match_result) > 0:
            w.append(int(Decimal(match_result[0]).scaleb(3)))
            t.append(int(Decimal(match_result[0]).scaleb(3)))
            continue
        match_result = regex(record, r'∞ to (\d+\.?\d*) m')
        if len(match_result) > 0:
            w.append(int(Decimal(match_result[0]).scaleb(3)))
            t.append(int(Decimal(match_result[0]).scaleb(3)))
            continue
        match_result = regex(record, r'(\d+\.?\d*)mm to infinity')
        if len(match_result) > 0:
            w.append(int(match_result[0]))
            t.append(int(match_result[0]))
            continue
        w.append(0)
        t.append(0)
    df['wide_min_focus_distance'] = w
    df['telephoto_min_focus_distance'] = t
    del df['Working range']

    # max_photographing_magnification
    m: List[float] = []
    for record in df.iterrows():
        series: Series = record[1]
        denominator = regex(series['Largest reproduction ratio'].replace(',', '.'), r'1:(\d+\.?\d*)')
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
    for record in df.iterrows():
        record = record[1]
        is_drip_proof.append(False)
        if record['O.I.S. Performance as per CIPA']:
            has_image_stabilization.append(True)
        else:
            has_image_stabilization.append(False)
        if record['name'] in ['Leica APO-Vario-Elmarit-SL 90-280 f/2.8-4'] or \
                record['wide_focal_length'] == record['telephoto_focal_length']:
            is_inner_zoom.append(True)
        else:
            is_inner_zoom.append(False)
    df['is_drip_proof'] = is_drip_proof
    df['has_image_stabilization'] = has_image_stabilization
    df['is_inner_zoom'] = is_inner_zoom
    del df['O.I.S. Performance as per CIPA']

    # overall_diameter, overall_length
    overall_diameter = []
    overall_length = []
    for record in df.iterrows():
        record = record[1]
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

    df['price'] = 0
    return df
