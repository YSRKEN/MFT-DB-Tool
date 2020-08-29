import re
from decimal import Decimal
from typing import List, Dict, Tuple

from constant import DATABASE_PATH
from service.i_database_service import IDataBaseService
from service.lens_service import Lens, LensService
from service.scraping_service import ScrapingService, get_p_lens_list
from service.sqlite_database_service import SqliteDataBaseService
from service.ulitity import regex


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

    # 35mm判換算焦点距離
    result1 = regex(record['焦点距離'], r'換算 *(\d+) *- *(\d+)mm相当')
    result2 = regex(record['焦点距離'], r'換算 *(\d+)mm相当')
    if len(result1) > 0:
        wide_focal_length = int(result1[0])
        telephoto_focal_length = int(result1[1])
    else:
        wide_focal_length = int(result2[0])
        telephoto_focal_length = wide_focal_length

    # F値
    result1 = regex(record['レンズ名'], r'F(\d+\.?\d*)-(\d+\.?\d*)')
    result2 = regex(record['レンズ名'], r'F(\d+\.?\d*)')
    if len(result1) > 0:
        wide_f_number = float(result1[0])
        telephoto_f_number = float(result1[1])
    else:
        wide_f_number = float(result2[0])
        telephoto_f_number = wide_f_number

    # 最短撮影距離(m単位のものをmm単位に変換していることに注意)
    result1 = regex(record['最短撮影距離'], r'(\d+\.\d+) *m.*(\d+\.\d+) *m')
    result2 = regex(record['最短撮影距離'], r'(\d+\.\d+) *m')
    if len(result1) > 0:
        wide_min_focus_distance = int(Decimal(result1[0]).scaleb(3))
        telephoto_min_focus_distance = int(Decimal(result1[1]).scaleb(3))
    else:
        wide_min_focus_distance = int(Decimal(result2[0]).scaleb(3))
        telephoto_min_focus_distance = wide_min_focus_distance

    # 換算最大撮影倍率
    max_photographing_magnification = 0.0
    for key, val in record.items():
        if '最大撮影倍率' not in key:
            continue
        result = regex(val, r'(\d+\.\d+)倍相当')
        for x in result:
            max_photographing_magnification = max(max_photographing_magnification, float(x))
        result = regex(val, r'換算 *(\d+\.\d+)倍')
        for x in result:
            max_photographing_magnification = max(max_photographing_magnification, float(x))

    # フィルターサイズ
    filter_diameter = -1
    for key, val in record.items():
        if 'フィルターサイズ' not in key:
            continue
        result = regex(val, r'(\d+)mm')
        if len(result) > 0:
            filter_diameter = int(result[0])

    # 最大径と全長
    overall_diameter = 0.0
    overall_length = 0.0
    for key, val in record.items():
        if '最大径' not in key:
            continue
        if '全長' not in key and '長さ' not in key:
            continue
        result = regex(val, r'(\d+\.?\d*)')
        if len(result) >= 2:
            overall_diameter = float(result[0])
            overall_length = float(result[1])
            break

    # 防塵防滴
    is_drip_proof = False
    for key, val in record.items():
        if '防滴' in key:
            is_drip_proof = True
            break

    # 手ブレ補正
    has_image_stabilization = 'IS' in record['レンズ名']

    # インナーズーム
    is_inner_zoom = False
    if wide_focal_length == wide_focal_length:
        is_inner_zoom = True
    elif record['品番'] in ['7-14_28pro', '40-150_28pro']:
        is_inner_zoom = True

    # 質量
    result = regex(record['質量'], r'([\d,]+)(g|ｇ| g)')
    weight = int(result[0].replace(',', ''))

    # メーカー希望小売価格
    price = int(regex(record2['希望小売価格'], r'([0-9,]+)円')[0].replace(',', ''))

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
        is_drip_proof=is_drip_proof,
        has_image_stabilization=has_image_stabilization,
        is_inner_zoom=is_inner_zoom,
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

    exit()

    # パナソニック製レンズについての情報を収集する
    p_lens_list = get_p_lens_list(scraping)

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
