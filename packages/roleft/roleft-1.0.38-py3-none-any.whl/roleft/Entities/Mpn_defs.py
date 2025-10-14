from abc import ABC, abstractmethod
from typing import List, Protocol


def _getMembers(obj: object) -> list[str]:
    all_attrs = dir(obj)
    return [
        attr
        for attr in all_attrs
        if not callable(getattr(obj, attr)) and not attr.startswith("_")
    ]


class EatDictable(Protocol):
    def EatDict(self, dic: dict) -> "EatDictable":
        return self

    def EatDictNew(self, dic: dict) -> "EatDictable":
        attrs = _getMembers(self)
        for attr in attrs:
            setattr(self, attr, dic[attr])
        return self


class MpnBase(EatDictable):
    Id = 0

    def __init__(self) -> None:
        pass


class MpnAliProduct(MpnBase):
    def __init__(self, Id: int = 0, Name: str = "", UserCount: int = 0) -> None:
        self.Id = Id
        self.Name = Name
        self.UserCount = UserCount
        pass

    def EatDict(self, dic: dict) -> "MpnAliProduct":
        attrs = _getMembers(self)
        for attr in attrs:
            setattr(self, attr, dic[attr])

        return self
