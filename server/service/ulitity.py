import re
from typing import List, Tuple, Dict

import pandas
from pandas import Series, DataFrame

from constant import Lens


def regex(text: str, pattern: str) -> List[str]:
    """グループ入り正規表現にマッチさせて、ヒットした場合はそれぞれの文字列の配列、そうでない場合は空配列を返す"""
    output: List[str] = []
    for m in re.finditer(pattern, text, re.MULTILINE):
        for x in m.groups():
            output.append(x)
    return output


def extract_numbers(series: Series, pair_data_patterns: List[str], single_data_patterns: List[str])\
        -> Tuple[List[str], List[str]]:
    """ある列について、その各行に含まれる文字列から、数字を1つないし2つ抽出して、リストにまとめる。
    数字が2つ→リストA・リストBにそれぞれの数字を追加
    数字が1つ→リストA・リストBに同じ数字を追加

    Parameters
    ----------
    series ある列
    pair_data_pattern 数字が2つ存在する場合のパターン
    single_data_pattern 数字が1つ存在する場合のパターン

    Returns
    -------
    分析後のリストA・リストB
    """

    list_a: List[str] = []
    list_b: List[str] = []
    for data_line in series.values:
        if data_line != data_line:
            list_a.append('')
            list_b.append('')
            continue
        flg = False

        # 数字が2つ存在する場合のパターン
        for pair_data_pattern in pair_data_patterns:
            result = regex(data_line, pair_data_pattern)
            if len(result) >= 2:
                list_a.append(result[0])
                list_b.append(result[1])
                flg = True
                break
        if flg:
            continue

        # 数字が1つ存在する場合のパターン
        for single_data_pattern in single_data_patterns:
            result = regex(data_line, single_data_pattern)
            if len(result) >= 1:
                list_a.append(result[0])
                list_b.append(result[0])
                flg = True
                break
        if flg:
            continue

    return list_a, list_b


def load_csv_lens(path: str, lens_mount: str) -> List[Lens]:
    """CSVファイルからデータを読み込む

    Parameters
    ----------
    path: str
        ファイルパス
    lens_mount: str
        レンズマウント

    Returns
    -------
        取得結果
    """
    df = pandas.read_csv(path, dtype={'product_number': str})
    df = df.fillna({'product_number': ''})
    df['mount'] = lens_mount
    return [Lens.from_dict(x) for x in df.to_dict(orient='records')]


def convert_columns(df: DataFrame, rename_columns: Dict[str, str], delete_columns: List[str]) -> DataFrame:
    """DataFrameのカラム名を変換する

    Parameters
    ----------
    df DataFrame
    rename_columns リネームするカラム名
    delete_columns 削除するカラム名

    Returns
    -------
    加工後のDataFrame
    """
    temp: List[Dict[str, any]] = []
    for record in df.to_dict(orient='records'):
        record: Dict[str, any] = record
        record2: Dict[str, any] = {}
        for key, val in record.items():
            if key in delete_columns:
                continue
            if val != val:
                continue
            if key in rename_columns:
                record2[rename_columns[key]] = val
            else:
                record2[key] = val
        temp.append(record2)
    return DataFrame.from_records(temp)
