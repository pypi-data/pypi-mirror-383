import pymysql
from roleft.Entities.RoleftMpn import EatDictable

from roleft.Enumerable.RoleftList import xList

# from roleft import xList
# from Module1.RoleftMpn import EatDictable

# T = TypeVar("T")


class DbConfig4Mysql(EatDictable):
    def __init__(
        self, host: str = "", port: int = 0, db: str = "", user: str = "", pwd: str = ""
    ) -> None:
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.pwd = pwd


class QueryObject4Mysql:
    def __init__(self, cfg: DbConfig4Mysql) -> None:
        self._cfg = cfg

    def _get_conn(self) -> pymysql.connections.Connection:
        cfg = self._cfg
        return pymysql.connect(
            host=cfg.host,
            port=cfg.port,
            db=cfg.db,
            user=cfg.user,
            password=cfg.pwd,
        )

    def execute_query(self, sql: str, params: dict = {}) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()

        affected = cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return affected

    def query_mpns(self, sql: str, params: dict = {}) -> xList[dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        cols = cur.description
        records = cur.fetchall()
        mpns = xList[dict]()

        for item in records:
            mpn = {}
            for i in range(len(cols) - 1):
                mpn[cols[i][0]] = item[i]
            mpns.Add(mpn)

        conn.commit()
        conn.close()
        return mpns

    """【闻祖东 2024-02-05 164459】将原始的信息返回回来, 一般用于调试。"""

    def query_records(self, sql: str, params: dict = {}) -> list:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        records = cur.fetchall()

        conn.commit()
        conn.close()
        """【闻祖东 2025-10-02 223154】后续还要检查这里的返回情况，之前是return records"""
        return list(records)

    """【闻祖东 2024-02-05 164050】适用于返回单列的情况"""

    def query_base_types(self, sql: str, params: dict = {}) -> xList[int | str | float]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        records = cur.fetchall()
        results = xList[int | str | float]()

        for item in records:
            results.Add(item[0])

        conn.commit()
        conn.close()
        return results
