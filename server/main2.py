from typing import List

from model.Lens import Lens
from service.i_database_service import IDataBaseService
from service.i_scraping_service import IScrapingService
from service.lxml_scraping_service import LxmlScrapingService
from service.maker.panasonic import get_panasonic_lens_list
from service.sqlite_database_service import SqliteDataBaseService


def main():
    database: IDataBaseService = SqliteDataBaseService('database.db')
    scraping: IScrapingService = LxmlScrapingService(database)
    lens_list: List[Lens] = []

    # Panasonic
    lens_list += get_panasonic_lens_list(scraping)
    # OLYMPUS
    # SIGMA
    # LEICA
    # COSINA
    # LAOWA
    # その他(TAMRON・Tokina・KOWA・安原製作所・SAMYANG・DZOFilm・中一光学・七工匠・銘匠光学)

    for lens in lens_list:
        print(lens)


if __name__ == '__main__':
    main()
