import re
from decimal import Decimal
from typing import List, Dict, Tuple

from constant import DATABASE_PATH
from service.i_database_service import IDataBaseService
from service.lens_service import Lens, LensService
from service.scraping_service import ScrapingService, get_p_lens_list
from service.sqlite_database_service import SqliteDataBaseService


def dict_to_lens_for_o(record: Dict[str, str], record2: Dict[str, str]) -> Lens:
    """辞書型をレンズデータに変換する

    Parameters
    ----------
    record: Dict[str, str]
        辞書型
    record2: Dict[str, str]
        辞書型

    Returns
    -------
        レンズデータ
    """

    wide_focal_length = 0
    telephoto_focal_length = 0
    m = re.match(r'.*換算 *(\d+) *- *(\d+)mm相当.*', record['焦点距離'])
    if m is not None:
        wide_focal_length = int(m.groups()[0])
        telephoto_focal_length = int(m.groups()[1])
    else:
        m = re.match(r'.*換算 *(\d+)mm相当.*', record['焦点距離'])
        if m is not None:
            wide_focal_length = int(m.groups()[0])
            telephoto_focal_length = int(m.groups()[0])

    wide_f_number = 0.0
    telephoto_f_number = 0.0
    m = re.match(r'.*F(\d+\.?\d*)-(\d+\.?\d*).*', record['レンズ名'])
    if m is not None:
        wide_f_number = float(m.groups()[0])
        telephoto_f_number = float(m.groups()[1])
    else:
        m = re.match(r'.*F(\d+\.?\d*).*', record['レンズ名'])
        if m is not None:
            wide_f_number = float(m.groups()[0])
            telephoto_f_number = float(m.groups()[0])

    wide_min_focus_distance = 0.0
    telephoto_min_focus_distance = 0.0
    m = re.match(r'.*(\d+\.\d+) *m.*(\d+\.\d+) *m.*', record['最短撮影距離'])
    if m is not None:
        wide_min_focus_distance = int(Decimal(m.groups()[0].replace('m', '')).scaleb(3))
        telephoto_min_focus_distance = int(Decimal(m.groups()[1].replace('m', '')).scaleb(3))
    else:
        m = re.match(r'.*(\d+\.\d+) *m.*', record['最短撮影距離'])
        if m is not None:
            wide_min_focus_distance = int(Decimal(m.groups()[0].replace('m', '')).scaleb(3))
            telephoto_min_focus_distance = wide_min_focus_distance
        else:
            exit()

    max_photographing_magnification = 0.0
    while True:
        m = re.match(r'.*換算 *(\d+\.\d+)倍.*', record['最大撮影倍率'])
        if m is not None:
            max_photographing_magnification = float(m.groups()[0])
            break
        m = re.match(r'.*(\d+\.\d+)倍相当.*', record['最大撮影倍率'])
        if m is not None:
            for x in m.groups():
                max_photographing_magnification = max(max_photographing_magnification, float(x))
            break
        if '35mm判換算最大撮影倍率' in record:
            m = re.match(r'.*(\d+\.\d+)倍相当.*', record['35mm判換算最大撮影倍率'])
            if m is not None:
                for x in m.groups():
                    max_photographing_magnification = max(max_photographing_magnification, float(x))
                break
            break
        if '最大撮影倍率（35mm判換算）' in record:
            m = re.match(r'.*(\d+\.\d+)倍相当.*', record['最大撮影倍率（35mm判換算）'])
            if m is not None:
                for x in m.groups():
                    max_photographing_magnification = max(max_photographing_magnification, float(x))
                break
            break

    overall_diameter = 0.0
    overall_length = 0.0
    for key, val in record.items():
        if '最大径' in key:
            if '全長' in key or '長さ' in key:
                m = re.search(r'(\d*\.?\d*) mm ｘ (\d*\.?\d*) *mm', val)
                if m is not None:
                    overall_diameter = float(m.groups()[0])
                    overall_length = float(m.groups()[1])
                    continue
                m = re.search(r'(\d*\.?\d*)mm x (\d*\.?\d*) *mm', val)
                if m is not None:
                    overall_diameter = float(m.groups()[0])
                    overall_length = float(m.groups()[1])
                    continue
                m = re.search(r'(\d*\.?\d*)mm × (\d*\.?\d*) *mm', val)
                if m is not None:
                    overall_diameter = float(m.groups()[0])
                    overall_length = float(m.groups()[1])
                    continue
                m = re.search(r'(\d*\.?\d*)[^\d]*(\d*\.?\d*) *mm', val)
                if m is not None:
                    overall_diameter = float(m.groups()[0])
                    overall_length = float(m.groups()[1])
                    continue
    if overall_diameter == 0.0 or overall_length == 0.0:
        exit()

    filter_diameter = -1
    if 'フィルターサイズ' in record:
        filter_diameter = int(record['フィルターサイズ'].replace('Ø', '').replace('Φ', '').replace('⌀', '').replace('mm', ''))

    weight = 0
    temp = record['質量'].replace('ｇ', 'g').replace(' g', 'g')
    m = re.search(r'(\d+)g', temp)
    if m is not None:
        weight = int(m.groups()[0])
    if weight == 0:
        exit()

    price = 0
    if '希望小売価格' in record2:
        m = re.search(r'([0-9,]+)円', record2['希望小売価格'])
        if m is not None:
            price = int(m.groups()[0].replace(',', ''))
    if price == 0:
        exit()

    return Lens(
        id=0,
        maker='OLYMPUS',
        name=record['レンズ名'],
        product_number=record['品番'],
        wide_focal_length=wide_focal_length,
        telephoto_focal_length=telephoto_focal_length,
        wide_f_number=wide_f_number,
        telephoto_f_number=telephoto_f_number,
        wide_min_focus_distance=wide_min_focus_distance,
        telephoto_min_focus_distance=telephoto_min_focus_distance,
        max_photographing_magnification=max_photographing_magnification,
        filter_diameter=filter_diameter,
        is_drip_proof=('防滴処理' in record),
        has_image_stabilization=('IS' in record['レンズ名']),
        is_inner_zoom=False,
        overall_diameter=overall_diameter,
        overall_length=overall_length,
        weight=weight,
        price=price,
    )


def get_o_lens_list(scraping: ScrapingService) -> List[Lens]:
    """OLYMPUS製レンズの情報を取得する

    Parameters
    ----------
    scraping: ScrapingService
        データスクレイピング用クラス

    Returns
    -------
        スクレイピング後のレンズデータ一覧
    """

    # レンズのURL一覧を取得する
    page = scraping.get_page('https://www.olympus-imaging.jp/product/dslr/mlens/index.html')
    lens_list: List[Tuple[str, str]] = []
    for a_element in page.find_all('h2.productName > a'):
        lens_name = a_element.text.split('/')[0].replace('\n', '')
        if 'M.ZUIKO' not in lens_name:
            continue
        lens_product_number = a_element.attrs['href'].replace('/product/dslr/mlens/', '').replace('/index.html', '')
        lens_list.append((lens_name, lens_product_number))

    # レンズごとに情報を取得する
    output: List[Lens] = []
    for lens_name, lens_product_number in lens_list:
        # ざっくり情報を取得する
        spec_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/spec.html'
        print(spec_url)
        page = scraping.get_page(spec_url)
        temp_dict: Dict[str, str] = {}
        for th_element, td_element in zip(page.find_all('th'), page.find_all('td')):
            if th_element is None or td_element is None:
                continue
            temp_dict[th_element.text] = td_element.text
        temp_dict['レンズ名'] = lens_name
        temp_dict['品番'] = lens_product_number

        index_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/index.html'
        print(f'  {index_url}')
        page = scraping.get_page(index_url)
        temp_dict2: Dict[str, str] = {}
        for th_element, td_element in zip(page.find_all('th'), page.find_all('td')):
            if th_element is None or td_element is None:
                continue
            temp_dict2[th_element.text] = td_element.text

        # 詳細な情報を取得する
        output.append(dict_to_lens_for_o(temp_dict, temp_dict2))
    return output


def main():
    database: IDataBaseService = SqliteDataBaseService(DATABASE_PATH)
    scraping = ScrapingService(database)

    # オリンパス製レンズについての情報を収集する
    o_lens_list = get_o_lens_list(scraping)
    for lens in o_lens_list:
        print(lens)

    exit()

    # パナソニック製レンズについての情報を収集する
    p_lens_list = get_p_lens_list(scraping)
    for lens in p_lens_list:
        print(lens)

    # DBを再構築して書き込む
    lens_service = LensService(database)
    lens_service.delete_all()
    for lens in p_lens_list:
        lens_service.save(lens)
    for lens in o_lens_list:
        lens_service.save(lens)
    with open('lens_data.json', 'w') as f:
        f.write(Lens.schema().dumps(lens_service.find_all(), many=True))


if __name__ == '__main__':
    main()
