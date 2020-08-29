from constant import DATABASE_PATH
from service.i_database_service import IDataBaseService
from service.lens_service import Lens, LensService
from service.scraping_service import ScrapingService, get_p_lens_list, get_o_lens_list
from service.sqlite_database_service import SqliteDataBaseService


def main():
    database: IDataBaseService = SqliteDataBaseService(DATABASE_PATH)
    scraping = ScrapingService(database)

    # パナソニック製レンズについての情報を収集する
    p_lens_list = get_p_lens_list(scraping)
    for lens in p_lens_list:
        print(lens)

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
