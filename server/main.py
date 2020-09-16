from constant import DATABASE_PATH
from service.i_database_service import IDataBaseService
from service.lens_service import Lens, LensService
from service.scraping_service import ScrapingService, get_p_lens_list, get_o_lens_list, get_s_lens_list, \
    get_t_lens_list, get_other_lens_list, get_p_l_lens_list, get_s_l_lens_list, get_l_l_lens_list
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

    # タムロン製レンズについての情報を収集する
    t_lens_list = get_t_lens_list()
    for lens in t_lens_list:
        print(lens)

    # その他レンズについての情報を収集する
    other_lens_list = get_other_lens_list()
    for lens in other_lens_list:
        print(lens)

    # DBを再構築して書き込む
    lens_service = LensService(database)
    lens_service.delete_all()
    for lens in p_lens_list:
        lens_service.save(lens)
    for lens in p_l_lens_list:
        lens_service.save(lens)
    for lens in o_lens_list:
        lens_service.save(lens)
    for lens in s_lens_list:
        lens_service.save(lens)
    for lens in s_l_lens_list:
        lens_service.save(lens)
    for lens in t_lens_list:
        lens_service.save(lens)
    for lens in other_lens_list:
        lens_service.save(lens)
    with open('lens_data.json', 'w') as f:
        f.write(Lens.schema().dumps(lens_service.find_all(), many=True))


def main2():
    database: IDataBaseService = SqliteDataBaseService(DATABASE_PATH)
    scraping = ScrapingService(database)
    lens_list = get_l_l_lens_list(scraping)
    print('')
    for lens in lens_list:
        print(lens)
        print(f'  {lens.wide_min_focus_distance} {lens.telephoto_min_focus_distance}')


if __name__ == '__main__':
    # main()
    main2()
