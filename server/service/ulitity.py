import re
from typing import List


def regex(text: str, pattern: str) -> List[str]:
    """グループ入り正規表現にマッチさせて、ヒットした場合はそれぞれの文字列の配列、そうでない場合は空配列を返す"""
    m = re.search(pattern, text)
    if m is None:
        return []
    return list(m.groups())
