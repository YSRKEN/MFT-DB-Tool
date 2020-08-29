import re
from decimal import Decimal
from typing import List, Dict, Tuple

from pandas import DataFrame

from constant import DATABASE_PATH
from service.i_database_service import IDataBaseService
from service.lens_service import Lens, LensService
from service.scraping_service import ScrapingService
from service.sqlite_database_service import SqliteDataBaseService


def regex(text: str, pattern: str) -> List[str]:
    """グループ入り正規表現にマッチさせて、ヒットした場合はそれぞれの文字列の配列、そうでない場合は空配列を返す"""
    m = re.search(pattern, text)
    if m is None:
        return []
    return list(m.groups())


def dict_to_lens_for_p(record: Dict[str, str]) -> Lens:
    """辞書型をレンズデータに変換する

    Parameters
    ----------
    record: Dict[str, str]
        辞書型

    Returns
    -------
        レンズデータ
    """

    # 35mm判換算焦点距離
    result1 = regex(record['35mm判換算焦点距離'], r'(\d+)mm～(\d+)mm')
    result2 = regex(record['35mm判換算焦点距離'], r'(\d+)mm')
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
    result1 = regex(record['最短撮影距離'], r'(\d+\.?\d*)m / (\d+\.?\d*)m')
    result2 = regex(record['最短撮影距離'], r'(\d+\.?\d*)m')
    if len(result1) > 0:
        wide_min_focus_distance = int(Decimal(result1[0]).scaleb(3))
        telephoto_min_focus_distance = int(Decimal(result1[1]).scaleb(3))
    else:
        wide_min_focus_distance = int(Decimal(result2[0]).scaleb(3))
        telephoto_min_focus_distance = wide_min_focus_distance

    # 換算最大撮影倍率
    result = regex(record['最大撮影倍率'], r'：(\d+\.?\d*)')
    max_photographing_magnification = float(result[0])

    # フィルターサイズ
    result = regex(record['フィルターサイズ'], r'φ(\d+)mm')
    if len(result) > 0:
        filter_diameter = int(result[0])
    else:
        filter_diameter = -1

    # 最大径と全長
    result = regex(record['最大径×全長'], r'(\d+\.?\d*)mm[^\d]*(\d+\.?\d*)mm')
    overall_diameter = float(result[0])
    overall_length = float(result[1])

    # 防塵防滴
    is_drip_proof = record['防塵・防滴'].find('○') >= 0 or record['防塵・防滴'].find('〇') >= 0

    # 手ブレ補正
    has_image_stabilization = record['手ブレ補正'].find('O.I.S.') >= 0

    # インナーズーム
    is_inner_zoom = False
    if wide_focal_length == wide_focal_length:
        is_inner_zoom = True
    elif record['品番'] in ['H-F007014', 'H-E08018', 'H-PS45175']:
        is_inner_zoom = True

    # 質量
    result = regex(record['質量'], r'([\d,]+)g')
    weight = int(result[0].replace(',', ''))

    # メーカー希望小売価格
    result = regex(record['メーカー希望小売価格'], r'([\d,]+) *円')
    price = int(result[0].replace(',', ''))

    return Lens(
        id=0,
        maker='Panasonic',
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


def get_p_lens_list(scraping: ScrapingService) -> List[Lens]:
    """Panasonic製レンズの情報を取得する

    Parameters
    ----------
    scraping: ScrapingService
        データスクレイピング用クラス

    Returns
    -------
        スクレイピング後のレンズデータ一覧
    """
    # 情報ページを開く
    page = scraping.get_page('https://panasonic.jp/dc/comparison.html')

    # tableタグからデータを収集する
    df = DataFrame()
    for table_element in page.find_all('table'):
        if 'LUMIX G' not in table_element.full_text:
            continue
        df['レンズ名'] = [x.text for x in table_element.find_all('th p')]
        for tr_element in table_element.find_all('tbody > tr'):
            key = tr_element.find('th').text
            value = [x.text for x in tr_element.find_all('td')]
            df[key] = value
        break

    # tableタグの各行を、Lens型のデータに変換する
    return [dict_to_lens_for_p(x) for x in df.to_dict(orient='records')]


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
        for tr_element in page.find_all('tr'):
            th_element = tr_element.find('th')
            td_element = tr_element.find('td')
            if th_element is None or td_element is None:
                continue
            temp_dict[th_element.text] = td_element.text

        # 詳細な情報を取得する
        wfl = 0
        tfl = 0
        m = re.match(r'.*換算 *(\d+) *- *(\d+)mm相当.*', temp_dict['焦点距離'])
        if m is not None:
            wfl = int(m.groups()[0])
            tfl = int(m.groups()[1])
        else:
            m = re.match(r'.*換算 *(\d+)mm相当.*', temp_dict['焦点距離'])
            if m is not None:
                wfl = int(m.groups()[0])
                tfl = int(m.groups()[0])

        wfn = 0.0
        tfn = 0.0
        m = re.match(r'.*F(\d+\.?\d*)-(\d+\.?\d*).*', lens_name)
        if m is not None:
            wfn = float(m.groups()[0])
            tfn = float(m.groups()[1])
        else:
            m = re.match(r'.*F(\d+\.?\d*).*', lens_name)
            if m is not None:
                wfn = float(m.groups()[0])
                tfn = float(m.groups()[0])

        wmfd = 0.0
        tmfd = 0.0
        m = re.match(r'.*(\d+\.\d+) *m.*(\d+\.\d+) *m.*', temp_dict['最短撮影距離'])
        if m is not None:
            wmfd = int(Decimal(m.groups()[0].replace('m', '')).scaleb(3))
            tmfd = int(Decimal(m.groups()[1].replace('m', '')).scaleb(3))
        else:
            m = re.match(r'.*(\d+\.\d+) *m.*', temp_dict['最短撮影距離'])
            if m is not None:
                wmfd = int(Decimal(m.groups()[0].replace('m', '')).scaleb(3))
                tmfd = wmfd
            else:
                exit()

        mpm = 0.0
        while True:
            m = re.match(r'.*換算 *(\d+\.\d+)倍.*', temp_dict['最大撮影倍率'])
            if m is not None:
                mpm = float(m.groups()[0])
                break
            m = re.match(r'.*(\d+\.\d+)倍相当.*', temp_dict['最大撮影倍率'])
            if m is not None:
                for x in m.groups():
                    mpm = max(mpm, float(x))
                break
            if '35mm判換算最大撮影倍率' in temp_dict:
                m = re.match(r'.*(\d+\.\d+)倍相当.*', temp_dict['35mm判換算最大撮影倍率'])
                if m is not None:
                    for x in m.groups():
                        mpm = max(mpm, float(x))
                    break
                break
            if '最大撮影倍率（35mm判換算）' in temp_dict:
                m = re.match(r'.*(\d+\.\d+)倍相当.*', temp_dict['最大撮影倍率（35mm判換算）'])
                if m is not None:
                    for x in m.groups():
                        mpm = max(mpm, float(x))
                    break
                break

        od = 0.0
        ol = 0.0
        for key, val in temp_dict.items():
            if '最大径' in key:
                if '全長' in key or '長さ' in key:
                    m = re.search(r'(\d*\.?\d*) mm ｘ (\d*\.?\d*) *mm', val)
                    if m is not None:
                        od = float(m.groups()[0])
                        ol = float(m.groups()[1])
                        continue
                    m = re.search(r'(\d*\.?\d*)mm x (\d*\.?\d*) *mm', val)
                    if m is not None:
                        od = float(m.groups()[0])
                        ol = float(m.groups()[1])
                        continue
                    m = re.search(r'(\d*\.?\d*)mm × (\d*\.?\d*) *mm', val)
                    if m is not None:
                        od = float(m.groups()[0])
                        ol = float(m.groups()[1])
                        continue
                    m = re.search(r'(\d*\.?\d*)[^\d]*(\d*\.?\d*) *mm', val)
                    if m is not None:
                        od = float(m.groups()[0])
                        ol = float(m.groups()[1])
                        continue
        if od == 0.0 or ol == 0.0:
            exit()

        fd = -1
        if 'フィルターサイズ' in temp_dict:
            fd = int(temp_dict['フィルターサイズ'].replace('Ø', '').replace('Φ', '').replace('⌀', '').replace('mm', ''))

        weight = 0
        temp = temp_dict['質量'].replace('ｇ', 'g').replace(' g', 'g')
        m = re.search(r'(\d+)g', temp)
        if m is not None:
            weight = int(m.groups()[0])
        if weight == 0:
            exit()

        index_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/index.html'
        print('  ' + index_url)
        page = scraping.get_page(index_url)
        temp_dict2: Dict[str, str] = {}
        for th_element, td_element in zip(page.find_all('th'), page.find_all('td')):
            if th_element is None or td_element is None:
                continue
            temp_dict2[th_element.text] = td_element.text
        price = 0
        if '希望小売価格' in temp_dict2:
            m = re.search(r'([0-9,]+)円', temp_dict2['希望小売価格'])
            if m is not None:
                price = int(m.groups()[0].replace(',', ''))
        if price == 0:
            exit()

        lens_data = Lens(
            id=0,
            maker='OLYMPUS',
            name=lens_name,
            product_number=lens_product_number,
            wide_focal_length=wfl,
            telephoto_focal_length=tfl,
            wide_f_number=wfn,
            telephoto_f_number=tfn,
            wide_min_focus_distance=wmfd,
            telephoto_min_focus_distance=tmfd,
            max_photographing_magnification=mpm,
            filter_diameter=fd,
            is_drip_proof=('防滴処理' in temp_dict),
            has_image_stabilization=('IS' in lens_name),
            is_inner_zoom=False,
            overall_diameter=od,
            overall_length=ol,
            weight=weight,
            price=price,
        )
        output.append(lens_data)
    return output


def main():
    database: IDataBaseService = SqliteDataBaseService(DATABASE_PATH)
    scraping = ScrapingService(database)

    # パナソニック製レンズについての情報を収集する
    p_lens_list = get_p_lens_list(scraping)
    for lens in p_lens_list:
        print(lens)

    exit()

    # オリンパス製レンズについての情報を収集する
    o_lens_list = get_o_lens_list(scraping)
    for lens in o_lens_list:
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
