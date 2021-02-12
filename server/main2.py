from typing import List

import pandas

from model.Lens import Lens
from service.i_database_service import IDataBaseService
from service.i_scraping_service import IScrapingService
from service.lxml_scraping_service import LxmlScrapingService
from service.maker.olympus import get_olympus_lens_list
from service.maker.panasonic import get_panasonic_lens_list, get_panasonic_old_lens_list
from service.sqlite_database_service import SqliteDataBaseService

pandas.options.display.max_columns = None
pandas.options.display.width = 150


def main():
    database: IDataBaseService = SqliteDataBaseService('database.db')
    scraping: IScrapingService = LxmlScrapingService(database)
    lens_list: List[Lens] = []

    # Panasonic
    df = get_panasonic_lens_list(scraping)
    df2 = get_panasonic_old_lens_list(scraping)
    df = pandas.concat([df, df2])
    df.to_csv('df-p.csv', index=False, encoding='utf_8_sig')

    # OLYMPUS
    # df = get_olympus_lens_list(scraping)
    # df.to_csv('df-o.csv', index=False, encoding='utf_8_sig')
    # SIGMA
    # LEICA
    # COSINA
    # LAOWA
    # その他(TAMRON・Tokina・KOWA・安原製作所・SAMYANG・DZOFilm・中一光学・七工匠・銘匠光学・Vazen・KAMLAN)

    for lens in lens_list:
        print(lens)


if __name__ == '__main__':
    main()
