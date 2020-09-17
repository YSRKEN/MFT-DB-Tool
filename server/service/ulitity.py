import re
from typing import List

import pandas

from constant import Lens


def regex(text: str, pattern: str) -> List[str]:
    """グループ入り正規表現にマッチさせて、ヒットした場合はそれぞれの文字列の配列、そうでない場合は空配列を返す"""
    output: List[str] = []
    for m in re.finditer(pattern, text, re.MULTILINE):
        for x in m.groups():
            output.append(x)
    return output


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
    df['mount'] = lens_mount
    return [Lens.from_dict(x) for x in df.to_dict(orient='records')]
