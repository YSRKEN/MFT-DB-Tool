from constant import DATABASE_PATH
from service.i_database_service import IDataBaseService
from service.lens_service import Lens, LensService
from service.scraping_service import ScrapingService, get_p_lens_list, get_o_lens_list, get_s_lens_list, \
    get_other_lens_list, get_p_l_lens_list, get_s_l_lens_list, get_l_l_lens_list, get_la_lens_list, get_cosina_lens_list
from service.sqlite_database_service import SqliteDataBaseService


def main():
    database: IDataBaseService = SqliteDataBaseService(DATABASE_PATH)
    scraping = ScrapingService(database)

    # パナソニック製レンズについての情報を収集する
    p_lens_list = get_p_lens_list(scraping)
    for lens in p_lens_list:
        print(lens)

    p_l_lens_list = get_p_l_lens_list(scraping)
    for lens in p_l_lens_list:
        print(lens)

    # オリンパス製レンズについての情報を収集する
    o_lens_list = get_o_lens_list(scraping)
    for lens in o_lens_list:
        print(lens)

    # シグマ製レンズについての情報を収集する
    s_lens_list = get_s_lens_list(scraping)
    for lens in s_lens_list:
        print(lens)
    s_l_lens_list = get_s_l_lens_list(scraping)
    for lens in s_l_lens_list:
        print(lens)

    # ライカ製レンズについての情報を収集する
    l_l_lens_list = get_l_l_lens_list(scraping)
    for lens in l_l_lens_list:
        print(lens)

    # コシナ製レンズについての情報を収集する
    cosina_lens_list = get_cosina_lens_list(scraping)
    for lens in cosina_lens_list:
        print(lens)

    # LAOWA製レンズについての情報を収集する
    la_lens_list = get_la_lens_list(scraping)
    for lens in la_lens_list:
        print(lens)

    # その他レンズについての情報を収集する
    other_lens_list = get_other_lens_list()
    for lens in other_lens_list:
        print(lens)

    # DBを再構築して書き込む
    lens_service = LensService(database)
    lens_service.delete_all()
    lens_service.save_all(
        p_lens_list + p_l_lens_list + o_lens_list + s_lens_list + s_l_lens_list
        + l_l_lens_list + cosina_lens_list + la_lens_list + other_lens_list
    )
    with open('lens_data.json', 'w') as f:
        f.write(Lens.schema().dumps(lens_service.find_all(), many=True))


def main2():
    database: IDataBaseService = SqliteDataBaseService(DATABASE_PATH)
    scraping = ScrapingService(database)
    scraping.clear_cache()
    lens_list = get_la_lens_list(scraping)
    for lens in lens_list:
        print(lens)


if __name__ == '__main__':
    """
    database: IDataBaseService = SqliteDataBaseService(DATABASE_PATH)
    scraping = ScrapingService(database)
    scraping.clear_cache()
    """
    main()
    # main2()
