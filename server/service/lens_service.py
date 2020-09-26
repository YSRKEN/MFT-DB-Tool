from typing import List, Tuple

from constant import Lens
from service.i_database_service import IDataBaseService


class LensService:
    def __init__(self, database: IDataBaseService):
        self.database = database
        self.database.query(
            'CREATE TABLE IF NOT EXISTS lens ('       # レンズ定義
            'id INTEGER PRIMARY KEY,'                 # ID
            'maker TEXT,'                             # メーカー名
            'name TEXT,'                              # レンズ名
            'product_number TEXT,'                    # 型番
            'wide_focal_length INTEGER,'              # 広角端の換算焦点距離(mm)
            'telephoto_focal_length INTEGER,'         # 望遠端の換算焦点距離(mm)
            'wide_f_number REAL,'                     # 広角端の開放F値
            'telephoto_f_number REAL,'                # 望遠端の開放F値
            'wide_min_focus_distance INTEGER,'        # 広角端の最短撮影距離(mm)
            'telephoto_min_focus_distance INTEGER,'   # 望遠端の最短撮影距離(mm)
            'max_photographing_magnification REAL,'   # 換算最大撮影倍率
            'filter_diameter REAL,'                   # フィルター径(mm)
            'is_drip_proof INTEGER,'                  # 防塵防滴ならTrue
            'has_image_stabilization INTEGER,'        # 手ブレ補正付きならTrue
            'is_inner_zoom INTEGER,'                  # インナーズームならTrue
            'overall_diameter REAL,'                  # レンズ全体の直径(mm)
            'overall_length REAL,'                    # レンズ全体の全長(mm)
            'weight REAL,'                            # 重量(g)
            'price INTEGER,'                          # 定価(円)
            'mount TEXT,'                             # レンズマウント
            'url TEXT)')                              # URL

    def get_data_count(self) -> int:
        result = self.database.select('SELECT COUNT(*) FROM lens')
        return result[0]['COUNT(*)']

    def find_all(self) -> List[Lens]:
        result = self.database.select('SELECT id, maker, name, product_number,'
                                      'wide_focal_length, telephoto_focal_length,'
                                      'wide_f_number, telephoto_f_number,'
                                      'wide_min_focus_distance,telephoto_min_focus_distance,'
                                      'max_photographing_magnification, filter_diameter, '
                                      'is_drip_proof, has_image_stabilization, is_inner_zoom, overall_diameter, '
                                      'overall_length, weight, price, mount, url FROM lens ORDER BY id')
        return [Lens.from_dict(x) for x in result]

    def save(self, lens: Lens) -> None:
        lens_list = self.find_all()
        if len([x for x in lens_list if x.id == lens.id]) == 0:
            lens_items: List[Tuple[str, any]] = lens.to_dict().items()
            temp1: List[str] = [x[0] for x in lens_items]
            temp2: List[any] = [x[1] for x in lens_items]
            if lens.id == 0:
                index = temp1.index('id')
                temp2[index] = self.get_data_count() + 1
            temp3 = ','.join(temp1)
            temp4 = ','.join(['?' for _ in temp1])
            self.database.query(f'INSERT INTO lens ({temp3}) VALUES ({temp4})', temp2)
        else:
            lens_items: List[Tuple[str, any]] = [x for x in lens.to_dict().items() if x[0] != 'id']
            temp1: List[str] = [f'{x[0]}=?' for x in lens_items]
            temp2: List[any] = [x[1] for x in lens_items]
            temp3 = ','.join(temp1)
            self.database.query(f'UPDATE lens SET {temp3} WHERE id={lens.id}', temp2)

    def save_all(self, lens_list: List[Lens]) -> None:
        query_list = []
        parameter_list = []
        lens_id = 1
        for lens in lens_list:
            lens_items: List[Tuple[str, any]] = lens.to_dict().items()
            temp1: List[str] = [x[0] for x in lens_items]
            temp2: List[any] = [x[1] for x in lens_items]
            index = temp1.index('id')
            temp2[index] = lens_id
            temp3 = ','.join(temp1)
            temp4 = ','.join(['?' for _ in temp1])
            query_list.append(f'INSERT INTO lens ({temp3}) VALUES ({temp4})')
            lens_id += 1
            parameter_list.append(temp2)
        self.database.many_query(query_list, parameter_list)

    def delete_all(self) -> None:
        self.database.query('DELETE FROM lens')
