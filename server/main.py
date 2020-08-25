from flask import Flask

from service.i_database_service import IDataBaseService
from service.sqlite_database_service import SqliteDataBaseService

app = Flask(__name__)
service: IDataBaseService = SqliteDataBaseService('database.db')


@app.route('/')
def hello():
    return 'hello, world'


if __name__ == '__main__':
    service.query('CREATE TABLE IF NOT EXISTS lens ('       # レンズ定義
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
    app.run(debug=True)
