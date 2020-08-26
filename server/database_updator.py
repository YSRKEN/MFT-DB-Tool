import re
import uuid
from decimal import Decimal
from pprint import pprint
from typing import List, Dict

import pandas
from pandas import DataFrame

from constant import DATABASE_PATH
from service.i_database_service import IDataBaseService
from service.lens_service import LensService, Lens
from service.sqlite_database_service import SqliteDataBaseService

from requests_html import HTMLSession, Element


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

        lens_data = Lens(
            id=0,
            name=record['レンズ名'],
            product_number=record['品番'],
            wide_focal_length=wfl,
            telephoto_focal_length=tfl,
            wide_f_number=wfn,
            telephoto_f_number=tfn,
            wide_min_focus_distance=wmfd,
            telephoto_min_focus_distance=tmfd,
            max_photographing_magnification=mpm
        )
        output.append(lens_data)
    return output


def main():
    database: IDataBaseService = SqliteDataBaseService(DATABASE_PATH)
    lens_service = LensService(database)
    lens_service.delete_all()

    # パナソニック製レンズについての情報を収集する
    p_lens_list = get_p_lens_list()
    for lens in p_lens_list:
        lens_service.save(lens)
    pprint(lens_service.find_all())


if __name__ == '__main__':
    main()
