import json
import re
from decimal import Decimal
from pprint import pprint
from typing import List, Dict, Tuple

from pandas import DataFrame
from requests_html import HTMLSession, Element

from constant import DATABASE_PATH
from service.i_database_service import IDataBaseService
from service.lens_service import LensService, Lens
from service.sqlite_database_service import SqliteDataBaseService


def get_p_lens_list() -> List[Lens]:
    # 情報ページを開く
    session = HTMLSession()
    response = session.get('https://panasonic.jp/dc/comparison.html')

    # データを収集する
    df = DataFrame()
    for table_element in response.html.find('table'):
        table_element: Element = table_element
        if 'LUMIX G' not in table_element.full_text:
            continue
        df['レンズ名'] = [x.text for x in table_element.find('th p')]
        for tr_element in table_element.find('tbody > tr'):
            tr_element: Element = tr_element
            key = tr_element.find('th', first=True).text
            value = [x.text for x in tr_element.find('td')]
            df[key] = value
        break

    output: List[Lens] = []
    for record in df.to_dict(orient='records'):
        record: Dict[str, str] = record

        if '～' in record['35mm判換算焦点距離']:
            wfl = int(record['35mm判換算焦点距離'].split('～')[0].replace('mm', ''))
            tfl = int(record['35mm判換算焦点距離'].split('～')[1].replace('mm', ''))
        else:
            wfl = int(record['35mm判換算焦点距離'].replace('mm', ''))
            tfl = int(record['35mm判換算焦点距離'].replace('mm', ''))

        wfn = 0.0
        tfn = 0.0
        m = re.match(r'.*F(\d+\.?\d*)-(\d+\.?\d*).*', record['レンズ名'])
        if m is not None:
            wfn = float(m.groups()[0])
            tfn = float(m.groups()[1])
        else:
            m = re.match(r'.*F(\d+\.?\d*).*', record['レンズ名'])
            if m is not None:
                wfn = float(m.groups()[0])
                tfn = float(m.groups()[0])

        if '/' in record['最短撮影距離']:
            wmfd = int(Decimal(record['最短撮影距離'].split(' / ')[0].replace('m', '')).scaleb(3))
            tmfd = int(Decimal(record['最短撮影距離'].split(' / ')[1].replace('m', '')).scaleb(3))
        else:
            wmfd = int(Decimal(record['最短撮影距離'].replace('m', '')).scaleb(3))
            tmfd = int(Decimal(record['最短撮影距離'].replace('m', '')).scaleb(3))

        m = re.match(r'.*：(\d+\.?\d*).*', record['最大撮影倍率'].replace('\n', ''))
        mpm = float(m.groups()[0].strip())

        if 'mm' in record['フィルターサイズ']:
            fd = int(record['フィルターサイズ'].replace('mm', '').replace('φ', ''))
        else:
            fd = -1

        m = re.match(r'.*φ(\d+\.?\d*)mm[^\d]*(\d+\.?\d*)mm', record['最大径×全長'].replace('\n', ''))
        od = float(m.groups()[0])
        ol = float(m.groups()[1])

        is_inner_zoom = False
        if wfl == tfl:
            is_inner_zoom = True
        elif record['品番'] in ['H-F007014', 'H-E08018', 'H-PS45175']:
            is_inner_zoom = True

        lens_data = Lens(
            id=0,
            maker='Panasonic',
            name=record['レンズ名'],
            product_number=record['品番'],
            wide_focal_length=wfl,
            telephoto_focal_length=tfl,
            wide_f_number=wfn,
            telephoto_f_number=tfn,
            wide_min_focus_distance=wmfd,
            telephoto_min_focus_distance=tmfd,
            max_photographing_magnification=mpm,
            filter_diameter=fd,
            is_drip_proof=(record['防塵・防滴'].find('○') >= 0),
            has_image_stabilization=(record['手ブレ補正'].find('O.I.S.') >= 0),
            is_inner_zoom=is_inner_zoom,
            overall_diameter=od,
            overall_length=ol,
            weight=int(record['質量'].replace('約', '').replace('g', '').replace(',', '')),
            price=int(record['メーカー希望小売価格'].replace('円（税抜）', '').replace(',', '')),
        )
        output.append(lens_data)
    return output


def get_o_lens_list() -> List[Lens]:
    # レンズのURL一覧を取得する
    session = HTMLSession()
    response = session.get('https://www.olympus-imaging.jp/product/dslr/mlens/index.html')
    lens_list: List[Tuple[str, str]] = []
    for a_element in response.html.find('h2.productName > a'):
        a_element: Element = a_element
        lens_name = a_element.text.split('/')[0].replace('\n', '')
        if 'M.ZUIKO' not in lens_name:
            continue
        lens_product_number = a_element.attrs["href"].replace('/product/dslr/mlens/', '').replace('/index.html', '')
        lens_list.append((lens_name, lens_product_number))

    # レンズごとに情報を取得する
    output: List[Lens] = []
    for lens_name, lens_product_number in lens_list:
        # ざっくり情報を取得する
        spec_url = f'https://www.olympus-imaging.jp/product/dslr/mlens/{lens_product_number}/spec.html'
        response = session.get(spec_url)
        table_element: Element = response.html.find('table', first=True)
        temp_dict: Dict[str, str] = {}
        for tr_element in table_element.find('tr'):
            th_element: Element = tr_element.find('th', first=True)
            td_element: Element = tr_element.find('td', first=True)
            temp_dict[th_element.text] = td_element.text

        # 詳細な情報を取得する
        lens_data = Lens(
            id=0,
            maker='OLYMPUS',
            name=lens_name,
            product_number=lens_product_number,
            wide_focal_length=0,
            telephoto_focal_length=0,
            wide_f_number=0,
            telephoto_f_number=0,
            wide_min_focus_distance=0,
            telephoto_min_focus_distance=0,
            max_photographing_magnification=0,
            filter_diameter=0,
            is_drip_proof=('防滴処理' in temp_dict),
            has_image_stabilization=('IS' in lens_name),
            is_inner_zoom=False,
            overall_diameter=0,
            overall_length=0,
            weight=0,
            price=0,
        )
        output.append(lens_data)
    return output


def main():
    # オリンパス製レンズについての情報を収集する
    o_lens_list = get_o_lens_list()
    for lens in o_lens_list:
        print(lens)
    return

    # パナソニック製レンズについての情報を収集する
    p_lens_list = get_p_lens_list()

    # DBを再構築して書き込む
    database: IDataBaseService = SqliteDataBaseService(DATABASE_PATH)
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
