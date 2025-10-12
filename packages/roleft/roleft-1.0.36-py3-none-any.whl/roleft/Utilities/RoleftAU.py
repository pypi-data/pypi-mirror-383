import hashlib
from enum import Enum, unique, auto
from typing_extensions import TypedDict
from typing import NewType


@unique
class InputCate(Enum):
    String = auto()
    File = auto()


@unique
class AlgorithmCate(Enum):
    Md5 = auto()
    Sha1 = auto()
    Sha256 = auto()


@unique
class CountryCate(Enum):
    """【闻祖东 2025-10-03 235829】只是作为一个例子而存在于此处，后续好借鉴"""

    CN = ("China", "People Republic Of China")
    US = ("USA", "United States of America")

    def __init__(self, short_name: str, full_name: str):
        self.short_name = short_name
        self.full_name = full_name

    def intro(self) -> None:
        print(f"this is {self.name}, and the full name is {self.full_name}")


cn = CountryCate.CN
cn.intro()

_algoDic = {
    AlgorithmCate.Md5: hashlib.md5,
    AlgorithmCate.Sha1: hashlib.sha1,
    AlgorithmCate.Sha256: hashlib.sha256,
}


def _loadContent(cate: InputCate, input: str) -> bytes:
    if cate == InputCate.File:
        with open(input, "rb") as file:
            return file.read()
    elif cate == InputCate.String:
        return input.encode()
    else:
        raise f"未定义的输入类型 - {cate}"


class AU:
    @staticmethod
    def Calc(algoCate: AlgorithmCate, inputCate: InputCate, input: str) -> str:
        func = _algoDic[algoCate]
        return func(_loadContent(inputCate, input)).hexdigest()

    @staticmethod
    def Sha1Str(input: str) -> str:
        return AU.Calc(AlgorithmCate.Sha1, InputCate.String, input)

    @staticmethod
    def Sha1File(path: str) -> str:
        return AU.Calc(AlgorithmCate.Sha1, InputCate.File, path)

    @staticmethod
    def Sha256Str(input: str) -> str:
        return AU.Calc(AlgorithmCate.Sha256, InputCate.String, input)

    @staticmethod
    def Sha256File(path: str) -> str:
        return AU.Calc(AlgorithmCate.Sha256, InputCate.File, path)

    @staticmethod
    def Md5Str(input: str) -> str:
        return AU.Calc(AlgorithmCate.Md5, InputCate.String, input)

    @staticmethod
    def Md5File(path: str) -> str:
        return AU.Calc(AlgorithmCate.Md5, InputCate.File, path)
