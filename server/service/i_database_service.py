from abc import ABCMeta, abstractmethod
from typing import List, Dict


class IDataBaseService(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def select(self, query: str, parameter=()) -> List[Dict[str, any]]:
        pass

    @abstractmethod
    def query(self, query: str, parameter=()) -> None:
        self.many_query([query], [parameter])

    @abstractmethod
    def many_query(self, query: List[str], parameter=None) -> None:
        pass
