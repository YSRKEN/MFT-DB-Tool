from typing import List

import pandas
from pandas import DataFrame

from constant import Lens
from service.i_database_service import IDataBaseService
from service.i_scraping_service import IScrapingService
from service.lxml_scraping_service import LxmlScrapingService
from service.maker.cosina import get_cosina_lens_list
from service.maker.laowa import get_laowa_lens_list
from service.maker.leica import get_leica_lens_list
from service.maker.olympus import get_olympus_lens_list
from service.maker.panasonic import get_panasonic_lens_list, get_panasonic_old_lens_list
from service.maker.samyang import get_samyang_lens_list
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
        print('【Panasonic】')
        df1 = get_panasonic_lens_list(scraping)
        if len(df) == 0:
            df = df1
        df2 = get_panasonic_old_lens_list(scraping)
        df = pandas.concat([df, df2])

    if 'OLYMPUS' in maker:
        # OLYMPUS
        print('【OLYMPUS】')
        df3 = get_olympus_lens_list(scraping)
        if len(df) == 0:
            df = df3
        else:
            df = pandas.concat([df, df3])

    if 'SIGMA' in maker:
        # SIGMA
        print('【SIGMA】')
        df4 = get_sigma_lens_list(scraping)
        if len(df) == 0:
            df = df4
        else:
            df = pandas.concat([df, df4])

    if 'LEICA' in maker:
        # LEICA
        print('【LEICA】')
        df5 = get_leica_lens_list(scraping)
        if len(df) == 0:
            df = df5
        else:
            df = pandas.concat([df, df5])

    if 'COSINA' in maker:
        # COSINA
        print('【COSINA】')
        df6 = get_cosina_lens_list(scraping)
        if len(df) == 0:
            df = df6
        else:
            df = pandas.concat([df, df6])

    if 'LAOWA' in maker:
        # LAOWA
        print('【LAOWA】')
        df7 = get_laowa_lens_list(scraping)
        if len(df) == 0:
            df = df7
        else:
            df = pandas.concat([df, df7])

    if 'SAMYANG' in maker:
        # SAMYANG
        print('【SAMYANG】')
        df8 = get_samyang_lens_list(scraping)
        if len(df) == 0:
            df = df8
        else:
            df = pandas.concat([df, df8])

    # その他(DZOFilm・KAMLAN・KOWA・TAMRON・Tokina・銘匠光学・Vazen・安原製作所・ヨンヌオ・中一光学・七工匠)
    # 銘匠光学はTTArtisan、ヨンヌオはYONGNUO、中一光学はZhongyi Optics Electronics、七工匠は7artisansとする
    if 'Other' in maker:
        print('【Other】')
        df9 = pandas.read_csv('csv/lenses.csv', dtype={'product_number': str})
        if len(df) == 0:
            df = df9
        else:
            df = pandas.concat([df, df9])

    column_list = ['maker', 'name', 'product_number', 'wide_focal_length', 'telephoto_focal_length', 'wide_f_number',
                   'telephoto_f_number', 'wide_min_focus_distance', 'telephoto_min_focus_distance',
                   'max_photographing_magnification', 'filter_diameter', 'is_drip_proof', 'has_image_stabilization',
                   'is_inner_zoom', 'overall_diameter', 'overall_length', 'weight', 'price', 'mount', 'url']
    for column in df.columns:
        if column not in column_list:
            column_list.append(column)
    temp = []
    for record in df.to_dict(orient='records'):
        temp2 = {}
        for key in column_list:
            if key in record:
                temp2[key] = record[key]
            else:
                temp2[key] = ''
        temp.append(temp2)
    df = DataFrame.from_records(temp)
    if '絞り範囲' in df:
        del df['絞り範囲']

    # df.to_csv('df.csv', index=False, encoding='utf_8_sig')
    lens_list = [Lens.from_dict(x) for x in df.to_dict(orient='records')]
    with open('lens_data.json', 'w', encoding='UTF-8') as f:
        f.write(Lens.schema().dumps(lens_list, many=True, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == '__main__':
    maker_list = [
        'Panasonic', 'OLYMPUS', 'SIGMA', 'LEICA', 'COSINA', 'LAOWA', 'SAMYANG', 'Other',
    ]
    main(maker_list)
