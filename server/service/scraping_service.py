from decimal import Decimal
from typing import List, Dict, Tuple

from constant import Lens
from service.ulitity import regex, load_csv_lens


def get_la_lens_list(scraping: ScrapingService) -> List[Lens]:
    """LAOWA製レンズの情報を取得する

    Parameters
    ----------
    scraping: ScrapingService
        データスクレイピング用クラス

    Returns
    -------
        スクレイピング後のレンズデータ一覧
    """

    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str]] = []
    page = scraping.get_page('https://www.laowa.jp/cat1/', cache=False)
    for div_element in page.find_all('div.product3'):
        h3_element = div_element.find('h3')
        if h3_element is None:
            continue
        a_element = div_element.find('a')
        if a_element is None:
            continue
        lens_name = h3_element.text
        lens_url = a_element.attrs['href']
        lens_list.append((lens_name, lens_url))

    # レンズの情報を取得する
    output: List[Lens] = []
    for lens_name, lens_url in lens_list:
        page = scraping.get_page(lens_url)
        temp: Dict[str, str] = {'レンズ名': lens_name, 'URL': lens_url}
        section_element = page.find('div.productTable')
        if section_element is not None:
            for tr_element in section_element.find_all('tr'):
                td_elements = tr_element.find_all('td')
                if len(td_elements) < 2:
                    continue
                temp[td_elements[0].text] = td_elements[1].text
            lens_data = dict_to_lens_for_la(temp)
            if lens_data.mount == '':
                continue
            output.append(lens_data)
    return output


def dict_to_lens_for_la(record: Dict[str, str]) -> Lens:
    """辞書型をレンズデータに変換する

    Parameters
    ----------
    record: Dict[str, str]
        辞書型

    Returns
    -------
        レンズデータ
    """

    # レンズではない製品の場合
    if '焦点距離' not in record:
        return Lens()

    # 焦点距離
    result1 = regex(record['焦点距離'], r'(\d+\.?\d*)-(\d+\.?\d*)mm')
    result2 = regex(record['焦点距離'], r'(\d+\.?\d*)mm')
    if len(result1) > 0:
        wide_focal_length = float(result1[0])
        telephoto_focal_length = float(result1[1])
    else:
        wide_focal_length = float(result2[0])
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

    # 最短撮影距離(mm単位に変換していることに注意)
    temp = record['最短合焦距離'] if '最短合焦距離' in record else record['最短撮影距離'] \
        if '最短撮影距離' in record else record['最小撮影距離'] \
        if '最小撮影距離' in record else record['最小フォーカシングディスタンス']
    temp = temp.replace('㎝', 'cm').replace('cｍ', 'cm')
    result1 = regex(temp, r'(\d+\.?\d*)mm～(\d+\.?\d*)mm')
    result2 = regex(temp, r'(\d+\.?\d*)cm')
    result3 = regex(temp, r'(\d+\.?\d*)mm')
    result4 = regex(temp, r'(\d+\.?\d*)m')
    if len(result1) > 0:
        wide_min_focus_distance = int(Decimal(result1[0]))
        telephoto_min_focus_distance = int(Decimal(result1[1]))
    elif len(result2) > 0:
        wide_min_focus_distance = int(Decimal(result2[0]).scaleb(1))
        telephoto_min_focus_distance = wide_min_focus_distance
    elif len(result3) > 0:
        wide_min_focus_distance = int(Decimal(result3[0]).scaleb(1))
        telephoto_min_focus_distance = wide_min_focus_distance
    else:
        wide_min_focus_distance = int(Decimal(result4[0]).scaleb(3))
        telephoto_min_focus_distance = wide_min_focus_distance

    # 換算最大撮影倍率
    temp = record['最大倍率'] if '最大倍率' in record else record['最大撮影倍率'] \
        if '最大撮影倍率' in record else record['撮影倍率'] \
        if '撮影倍率' in record else record['最大倍率比']
    result1 = regex(temp, r'(\d+\.?\d*):(\d+\.?\d*)')
    result2 = regex(temp, r'(\d+\.?\d*)')
    if len(result1) > 0:
        max_photographing_magnification = float(result1[0]) / float(result1[1])
    else:
        max_photographing_magnification = float(result2[0])

    # フィルターサイズ
    temp = record['フィルター径'] if 'フィルター径' in record else record['フィルタースレッド'] \
        if 'フィルタースレッド' in record else ''
    result = regex(temp, r'(\d+)mm')
    if temp != '' and len(result) > 0:
        filter_diameter = int(result[0])
    else:
        filter_diameter = -1

    # 最大径と全長
    temp = record['外形寸法'] if '外形寸法' in record else record['サイズ'] \
        if 'サイズ' in record else ''
    if temp != '':
        result = regex(temp, r'(\d+\.?\d*)[^\d]*(\d+\.?\d*)')
        overall_diameter = float(result[0])
        overall_length = float(result[1])
    else:
        overall_diameter = 0
        overall_length = 0

    # 質量
    if record['レンズ名'] in [
        'LAOWA 15mm F4 WIDE ANGLE MACRO'
    ]:
        # なぜか重量とマウントの掲載が逆なので修正
        temp = str(record['重量'])
        record['重量'] = str(record['マウント'])
        record['マウント'] = temp
    if '重量' in record:
        record['質量'] = record['重量']
    result = regex(record['質量'], r'([\d,]+)(g|ｇ)')
    weight = int(result[0].replace(',', ''))

    # レンズマウント
    mount = ''
    temp = record['マウント'] if 'マウント' in record else record['対応マウント']
    if 'マイクロフォーサーズ' in temp:
        mount = 'マイクロフォーサーズ'
    if 'Leica L' in temp:
        mount = 'ライカL'
    if mount == 'マイクロフォーサーズ':
        wide_focal_length *= 2
        telephoto_focal_length *= 2
        max_photographing_magnification *= 2

    return Lens(
        maker='LAOWA',
        name=record['レンズ名'].replace('\u3000', ' '),
        wide_focal_length=int(wide_focal_length),
        telephoto_focal_length=int(telephoto_focal_length),
        wide_f_number=wide_f_number,
        telephoto_f_number=telephoto_f_number,
        wide_min_focus_distance=wide_min_focus_distance,
        telephoto_min_focus_distance=telephoto_min_focus_distance,
        max_photographing_magnification=max_photographing_magnification,
        filter_diameter=filter_diameter,
        is_inner_zoom=wide_focal_length == telephoto_focal_length,
        overall_diameter=overall_diameter,
        overall_length=overall_length,
        weight=weight,
        mount=mount,
        url=record['URL'],
    )


def dict_to_lens_for_cosina(record: Dict[str, str]) -> Lens:
    """辞書型をレンズデータに変換する

    Parameters
    ----------
    record: Dict[str, str]
        辞書型

    Returns
    -------
        レンズデータ
    """

    lens_data = Lens(maker='Cosina', url=record['URL'], mount='マイクロフォーサーズ')

    # レンズ名
    if record['レンズ名'] == 'mft60mm':
        lens_data.name = 'Voigtlander NOKTON 60mm F0.95'
    elif record['レンズ名'] == '25mm Type2':
        lens_data.name = 'Voigtlander NOKTON 25mm F0.95 TypeII'
    elif record['レンズ名'] == '29mm':
        lens_data.name = 'Voigtlander SUPER NOKTON 29mm F0.8'
    else:
        lens_data.name = 'Voigtlander NOKTON ' + record['レンズ名']

    # 35mm判換算焦点距離
    result = regex(record['焦点距離'], r'(\d+\.?\d*)mm')
    if len(result) == 1:
        lens_data.wide_focal_length = round(float(result[0]) * 2)
        lens_data.telephoto_focal_length = lens_data.wide_focal_length
    else:
        raise Exception('焦点距離がパースできません')

    # F値
    result = regex(lens_data.name, r'F(\d+\.?\d*)')
    if len(result) == 1:
        lens_data.wide_f_number = float(result[0])
        lens_data.telephoto_f_number = lens_data.wide_f_number
    else:
        raise Exception('F値がパースできません')

    # 最短撮影距離
    result = regex(record['最短撮影距離'], r'(\d+\.?\d*)m')
    if len(result) == 1:
        lens_data.wide_min_focus_distance = float(result[0]) * 1000
        lens_data.telephoto_min_focus_distance = lens_data.wide_min_focus_distance
    else:
        raise Exception('最短撮影距離がパースできません')

    # 最大撮影倍率
    result = regex(record['最大撮影倍率'], r'1(:|：)(\d+\.?\d*)')
    if len(result) >= 2:
        lens_data.max_photographing_magnification = round(1.0 / float(result[1]) * 2 * 100) / 100
    else:
        raise Exception('最大撮影倍率がパースできません')

    # フィルターサイズ
    result = regex(record['フィルターサイズ'], r'(\d+\.?\d*)mm')
    if len(result) == 1:
        lens_data.filter_diameter = float(result[0])
    else:
        raise Exception('フィルターサイズがパースできません')

    # インナーズームか？
    lens_data.is_inner_zoom = lens_data.wide_focal_length == lens_data.telephoto_focal_length

    # 最大径×全長
    result = regex(record['最大径×全長'], r'(\d+\.?\d*)[^\d]*(\d+\.?\d*)mm')
    lens_data.overall_diameter = float(result[0])
    lens_data.overall_length = float(result[1])

    # 質量
    result = regex(record['重量'], r'(\d+)g')
    if len(result) == 1:
        lens_data.weight = float(result[0])
    else:
        raise Exception('質量がパースできません')

    return lens_data


def get_cosina_lens_list(scraping: ScrapingService) -> List[Lens]:
    """Cosina製レンズの情報を取得する

    Parameters
    ----------
    scraping: ScrapingService
        データスクレイピング用クラス

    Returns
    -------
        スクレイピング後のレンズデータ一覧
    """

    # レンズのURL一覧を取得する
    lens_list: List[Tuple[str, str]] = []
    page = scraping.get_page('http://www.cosina.co.jp/seihin/voigtlander/mft-mount/index.html',
                             encoding='cp932', cache=False)
    for a_element in page.find_all('td > a'):
        lens_name = a_element.find('img').attrs['alt']
        lens_url = 'http://www.cosina.co.jp/seihin/voigtlander/mft-mount/' + a_element.attrs['href']
        if 'mm' in lens_name and 'mft' in a_element.attrs['href']:
            lens_list.append((lens_name, lens_url))

    # レンズの情報を取得する
    output: List[Lens] = []
    for lens_name, lens_url in lens_list:
        page = scraping.get_page(lens_url, encoding='cp932')
        temp: Dict[str, str] = {'レンズ名': lens_name, 'URL': lens_url}
        for tr_element in page.find_all('tr'):
            td_elements = tr_element.find_all('td')
            if len(td_elements) < 2:
                continue
            if td_elements[0].text == '' or td_elements[1].text == '':
                continue
            temp[td_elements[0].text] = td_elements[1].text
        lens_data = dict_to_lens_for_cosina(temp)
        if lens_data.mount == '':
            continue
        output.append(lens_data)
    return output


def get_other_lens_list():
    return load_csv_lens('csv/m4_3.csv', 'マイクロフォーサーズ') + load_csv_lens('csv/l_mount.csv', 'ライカL')
