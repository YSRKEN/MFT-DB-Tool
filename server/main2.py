from typing import List

import pandas
from pandas import DataFrame

from service.i_database_service import IDataBaseService
from service.i_scraping_service import IScrapingService
from service.lxml_scraping_service import LxmlScrapingService
from service.maker.olympus import get_olympus_lens_list
from service.maker.panasonic import get_panasonic_lens_list, get_panasonic_old_lens_list
from service.maker.sigma import get_sigma_lens_list
from service.sqlite_database_service import SqliteDataBaseService

pandas.options.display.max_columns = None
pandas.options.display.width = 150


def main(maker: List[str]):
    database: IDataBaseService = SqliteDataBaseService('database.db')
    scraping: IScrapingService = LxmlScrapingService(database)

    df = DataFrame()

    if 'Panasonic' in maker:
        # Panasonic
        df1 = get_panasonic_lens_list(scraping)
        if len(df) == 0:
            df = df1
        df2 = get_panasonic_old_lens_list(scraping)
        df = pandas.concat([df, df2])

    if 'OLYMPUS' in maker:
        # OLYMPUS
        df3 = get_olympus_lens_list(scraping)
        if len(df) == 0:
            df = df3
        else:
            df = pandas.concat([df, df3])

    if 'SIGMA' in maker:
        # SIGMA
        df4 = get_sigma_lens_list(scraping)
        if len(df) == 0:
            df = df4
        else:
            df = pandas.concat([df, df4])

    # LEICA
    # COSINA
    # LAOWA
    # その他(TAMRON・Tokina・KOWA・安原製作所・SAMYANG・DZOFilm・中一光学・七工匠・銘匠光学・Vazen・KAMLAN・ヨンヌオ)

    df.to_csv('df.csv', index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    maker = [
        # 'Panasonic',
        # 'OLYMPUS',
        'SIGMA',
    ]
    main(maker)
