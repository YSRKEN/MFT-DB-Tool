from abc import ABCMeta, abstractmethod
from typing import Optional, MutableMapping, List


class DomObject(metaclass=ABCMeta):
    """DOMオブジェクト"""

    @abstractmethod
    def find(self, query: str) -> Optional['DomObject']:
        """指定したCSSクエリでDOMオブジェクトを検索する

        Parameters
        ----------
        query CSSクエリ文字列

        Returns
        -------
            最初の検索結果(未ヒット時はNone)
        """
        pass

    @abstractmethod
    def find_all(self, query: str) -> List['DomObject']:
        """指定したCSSクエリでDOMオブジェクトを検索する(複数)

        Parameters
        ----------
        query CSSクエリ文字列

        Returns
        -------
            すべての検索結果
        """
        pass

    @property
    @abstractmethod
    def text(self) -> str:
        """含まれるテキスト分を返す

        Returns
        -------
            テキスト分
        """
        pass

    @property
    @abstractmethod
    def full_text(self) -> str:
        """含まれる全てのテキスト分を返す

        Returns
        -------
            全てのテキスト分
        """
        pass

    @property
    @abstractmethod
    def attrs(self) -> MutableMapping:
        """属性とその値を、Key-Valueな辞書として返す

        Returns
        -------
            属性をKey、属性値をValueとする辞書
        """
        pass
