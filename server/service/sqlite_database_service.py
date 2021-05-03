from sqlite3 import connect
from typing import List, Dict

from service.i_database_service import IDataBaseService


class SqliteDataBaseService(IDataBaseService):
    def __init__(self, database_file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.db_file_path = database_file_path

    def select(self, query: str, parameter=()) -> List[Dict[str, any]]:
        with connect(self.db_file_path) as conn:
            cur = conn.cursor()
            cur.execute(query, parameter)
            columns = [description[0] for description in cur.description]
            output: List[Dict[str, any]] = []
            for row in cur.fetchall():
                temp: Dict[str, any] = {}
                for c, d in zip(columns, row):
                    temp[c] = d
                output.append(temp)
            return output

    def query(self, query: str, parameter=()) -> None:
        self.many_query([query], [parameter])

    def many_query(self, query: List[str], parameter=None) -> None:
        if parameter is None:
            parameter = []
            for _ in range(0, len(query)):
                parameter.append(())
        if len(query) != len(parameter):
            return
        with connect(self.db_file_path) as conn:
            cur = conn.cursor()
            for q, p in zip(query, parameter):
                cur.execute(q, p)
            conn.commit()
