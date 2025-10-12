from enum import Enum
import math
import pathlib
import random
import time
from typing import TypeVar

from roleft.Entities.RoleftDateTime import xDateTime
from roleft.Entities.RoleftMpn import MpnBase

TMpn = TypeVar("TMpn", bound=MpnBase)

_strSrc = "2345678abcdefghjkmnprstuvwxyzABCDEFGHJKMNPRSTUVWXYZ"
_step = 1024
_kvps = {
    "B": math.pow(_step, 1),
    "KB": math.pow(_step, 2),
    "MB": math.pow(_step, 3),
    "GB": math.pow(_step, 4),
    "TB": math.pow(_step, 5),
}


def _getMembers(obj: object) -> list[str]:
    all_attrs = dir(obj)
    return [
        attr
        for attr in all_attrs
        if not callable(getattr(obj, attr)) and not attr.startswith("_")
    ]


class CU:
    @staticmethod
    def GenRandom(min_value: int = 0, max_value: int = 10) -> int:
        return random.randrange(min_value, max_value)

    @staticmethod
    def Save2File(content: str, path: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

    @staticmethod
    def GetRandomStr(length: int = 16) -> str:
        return "".join(random.sample(_strSrc, length))

    @staticmethod
    def HasValue(items: list) -> bool:
        return len(items) > 0

    @staticmethod
    def ReadAllText(path: str) -> str:
        fo = open(path, "r")
        content = fo.read()
        fo.close()
        return content

    @staticmethod
    def SureDir(dirPath: str) -> None:
        path = pathlib.Path(dirPath)
        if not path.exists():
            path.mkdir(511, True)

    @staticmethod
    def RandomBool() -> bool:
        return bool(CU.GenRandom(0, 2))

    # @classmethod
    # def RandomDateTime(cls) -> xDateTime:
    #     ticks = CU.GenRandom(0, 17280000000)
    #     tm = time.localtime(ticks)
    #     return xDateTime(tm)

    @staticmethod
    def GenSizeDesc(length: int) -> str:
        showNum = float(length)

        currKey = ""
        for key, value in _kvps.items():
            currKey = key
            if showNum < _step:
                break

            showNum = length / value

        return f"{round(showNum, 2)}{currKey}"

    @staticmethod
    def C2E(val1: str | int, defaultEnum: Enum) -> Enum:
        tp = type(defaultEnum)
        values = list(map(lambda member: member, tp))
        for x in values:
            if type(val1) == int and val1 == x.value:
                return tp[x.name]
            elif type(val1) == str and val1.lower() == x.name.lower():
                return tp[x.name]

        return defaultEnum

    # 【闻祖东 2024-01-17 174133】以后这里做一个泛型的限制
    @staticmethod
    def EatDictNew(mpn: TMpn, dic: dict) -> TMpn:
        attrs = _getMembers(mpn)
        for attr in attrs:
            if attr in dic:
                setattr(mpn, attr, dic[attr])

        return mpn
