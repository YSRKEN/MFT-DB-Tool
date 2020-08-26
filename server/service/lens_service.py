from dataclasses import dataclass
from typing import List, Dict, Tuple

from dataclasses_json import dataclass_json

from service.i_database_service import IDataBaseService


@dataclass_json
@dataclass
class Lens:
    id: int
    name: str
    product_number: str
    wide_focal_length: float
    telephoto_focal_length: float
    wide_f_number: float
    telephoto_f_number: float
    wide_min_focus_distance: float
    telephoto_min_focus_distance: float
    max_photographing_magnification: float
    filter_diameter: float
    is_drip_proof: bool
    has_image_stabilization: bool
    is_inner_zoom: bool
    overall_diameter: float
    overall_length: float
    weight: float
    price: int


class LensService:
    def __init__(self, database: IDataBaseService):
        self.database = database
        self.database.query(
            'CREATE TABLE IF NOT EXISTS lens ('       # レンズ定義
            'id INTEGER PRIMARY KEY,'                 # ID
            'name TEXT,'                              # レンズ名
            'product_number TEXT,'                    # 型番
            'wide_focal_length REAL,'                 # 広角端の実焦点距離(mm)
            'telephoto_focal_length REAL,'            # 望遠端の実焦点距離(mm)
            'wide_f_number REAL,'                     # 広角端の開放F値
            'telephoto_f_number REAL,'                # 望遠端の開放F値
            'wide_min_focus_distance REAL,'           # 広角端の最短撮影距離(mm)
            'telephoto_min_focus_distance REAL,'      # 望遠端の最短撮影距離(mm)
            'max_photographing_magnification REAL,'   # 実最大撮影倍率
            'filter_diameter REAL,'                   # フィルター径(mm)
            'is_drip_proof INTEGER,'                  # 防塵防滴ならTrue
            'has_image_stabilization INTEGER,'        # 手ブレ補正付きならTrue
            'is_inner_zoom INTEGER,'                  # インナーズームならTrue
            'overall_diameter REAL,'                  # レンズ全体の直径(mm)
            'overall_length REAL,'                    # レンズ全体の全長(mm)
            'weight REAL,'                            # 重量(g)
            'price INTEGER)')                         # 定価(円)

    def find_all(self) -> List[Lens]:
        result = self.database.select('SELECT id, name, product_number, wide_focal_length, telephoto_focal_length,'
                                      'wide_f_number, telephoto_f_number, wide_min_focus_distance,'
                                      'telephoto_min_focus_distance, max_photographing_magnification, filter_diameter, '
                                      'is_drip_proof, has_image_stabilization, is_inner_zoom, overall_diameter, '
                                      'overall_length, weight, price FROM lens ORDER BY id')
        return [Lens.from_dict(x) for x in result]

    def save(self, lens: Lens) -> None:
        lens_list = self.find_all()
        if len([x for x in lens_list if x.id == lens.id]) == 0:
            lens_items: List[Tuple[str, any]] = lens.to_dict().items()
            temp1: List[str] = [x[0] for x in lens_items]
            temp2: List[any] = [x[1] for x in lens_items]
            temp3 = ','.join(temp1)
            temp4 = ','.join(['?' for _ in temp1])
            self.database.query(f'INSERT INTO lens ({temp3}) VALUES ({temp4})', temp2)
        else:
            lens_items: List[Tuple[str, any]] = [x for x in lens.to_dict().items() if x[0] != 'id']
            temp1: List[str] = [f'{x[0]}=?' for x in lens_items]
            temp2: List[any] = [x[1] for x in lens_items]
            temp3 = ','.join(temp1)
            self.database.query(f'UPDATE lens SET {temp3} WHERE id={lens.id}', temp2)

    def delete_all(self) -> None:
        self.database.query('DELETE FROM lens')
