from dataclasses import dataclass
from typing import Any, Dict, Optional, TypeVar, Union
import pymysql
from pymysql.connections import Connection
from pymysql.cursors import Cursor
from Entities.Mpn_defs import EatDictable

from Enumerable.xlist_defs import xlist

# from roleft import xList
# from Module1.RoleftMpn import EatDictable

# T = TypeVar("T")
# TNumUnn = TypeVar("TNumUnn", bound=Union[int, float])
TBaseTypes = TypeVar("TBaseTypes", int, float, str)


@dataclass
class DbConfig4Mysql(EatDictable):
    host: str
    port: int
    db: str
    user: str
    pwd: str

    # def __init__(self, host: str, port: int, db: str, user: str, pwd: str) -> None:
    #     self.host = host
    #     self.port = port
    #     self.db = db
    #     self.user = user
    #     self.pwd = pwd


class QueryObject4Mysql:
    def __init__(self, cfg: DbConfig4Mysql) -> None:
        self._cfg = cfg

    def _get_conn(self) -> Connection:
        cfg = self._cfg
        return pymysql.connect(
            host=cfg.host,
            port=cfg.port,
            db=cfg.db,
            user=cfg.user,
            password=cfg.pwd,
        )

    # 【闻祖东 2025-10-13 104331】坚决不要使用 params: dict = {} 这样的 可变默认参数（Critical）
    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        with self._get_conn() as conn:
            cursor: Cursor
            with conn.cursor() as cursor:
                affected = cursor.execute(sql, params)
            conn.commit()

        return affected

    def query_records(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> xlist[dict]:
        mpns = xlist[dict]()
        with self._get_conn() as conn:
            cursor: Cursor = conn.cursor()
            cursor.execute(sql, params)
            cols = cursor.description
            records = cursor.fetchall()

            for item in records:
                mpn = {}
                for i in range(len(cols) - 1):
                    mpn[cols[i][0]] = item[i]
                mpns.append(mpn)

            conn.commit()

        return mpns

    def query_drafts(self, sql: str, params: Optional[Dict[str, Any]] = None) -> xlist:
        """【闻祖东 2024-02-05 164459】将原始的信息返回回来, 一般用于调试。"""
        with self._get_conn() as conn:
            cursor: Cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()

            conn.commit()

        """【闻祖东 2025-10-02 223154】后续还要检查这里的返回情况，之前是return records"""
        return xlist(rows)

    def query_base_types(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> xlist[TBaseTypes]:
        """【闻祖东 2024-02-05 164050】适用于返回单列的情况"""
        drafts = self.query_drafts(sql, params)
        return drafts.x_map(lambda x: x[0])

        # records: xlist[TBaseTypes] = []
        # for item in drafts:
        #     records.append(item[0])

        # # with self._get_conn() as conn:
        # #     with conn.cursor() as cursor:
        # #         cursor.execute(sql, params)
        # #         drafts = cursor.fetchall()
        # #         results: xlist[TBaseTypes] = []

        # #         for item in drafts:
        # #             results.append(item[0])

        # #     conn.commit()

        # return records
