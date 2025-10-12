from typing import Generic, TypeVar
from roleft.Entities.RoleftKeyValue import KeyValue
from roleft.Enumerable.RoleftList import xList


TKey = TypeVar("TKey")
TValue = TypeVar("TValue")


class xDict(Generic[TKey, TValue]):
    def __init__(self) -> None:
        self.__kvs: xList[KeyValue[TKey, TValue]] = xList()

    def SureAdd(self, key: TKey, value: TValue) -> "xDict[TKey, TValue]":
        curr = self.__kvs.First(lambda x: x.key == key)
        if curr != None:
            self.__kvs.Remove(curr)

        self.__kvs.Add(KeyValue(key, value))
        return self

    def ContainsKey(self, key: TKey) -> bool:
        return self.__kvs.Exists(lambda x: x.key == key)

    def Keys(self) -> xList[TKey]:
        return self.__kvs.Select(lambda x: x.key)

    def Values(self) -> xList[TValue]:
        return self.__kvs.Select(lambda x: x.value)

    def KeyValues(self) -> xList[KeyValue[TKey, TValue]]:
        return self.__kvs

    def ToList(self) -> list:
        return self.__kvs.ToList()

    def Clear(self) -> "xDict[TKey, TValue]":
        self.__kvs.Clear()
        return self

    def GetValue(self, key: TKey) -> TValue:
        first: KeyValue[TKey, TValue] | None = self.__kvs.First(lambda x: x.key == key)
        if first != None:
            # newFirst: KeyValue[TKey, TValue] = first
            # 【闻祖东 2024-04-20 173327】这里并没有完全写完。
            # result: TValue = newFirst.value
            return first.value
        else:
            raise ValueError(f"不存在的key:{key}")

    def Remove(self, key: TKey) -> "xDict[TKey, TValue]":
        try:
            curr = self.__kvs.First(lambda x: x.key == key)
            if curr is not None:
                self.__kvs.Remove(curr)
        except ValueError:
            pass

        return self

    def Print(self) -> None:
        dic = {}
        for kv in self.__kvs.ToList():
            dic[kv.key] = kv.value

        print(dic)
