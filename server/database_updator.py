from pprint import pprint
from typing import List, Dict

import pandas
from pandas import DataFrame

from constant import DATABASE_PATH
from service.i_database_service import IDataBaseService
from service.lens_service import LensService, Lens
from service.sqlite_database_service import SqliteDataBaseService

from requests_html import HTMLSession


def get_p_lens_list() -> List[Lens]:
    # 情報ページを開く
    session = HTMLSession()
    response = session.get('https://panasonic.jp/dc/comparison.html')

    # データを収集する
    df = DataFrame()
    for table_element in response.html.find('table'):
        if 'LUMIX G' not in table_element.full_text:
            continue
        df['レンズ名'] = [x.text for x in table_element.find('th p')]
        for tr_element in table_element.find('tbody > tr'):
            key = tr_element.find('th', first=True).text
            value = [x.text for x in tr_element.find('td')]
            df[key] = value
        break

    pandas.options.display.width = 150
    pandas.options.display.max_columns = None
    print(df)
    return []


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
