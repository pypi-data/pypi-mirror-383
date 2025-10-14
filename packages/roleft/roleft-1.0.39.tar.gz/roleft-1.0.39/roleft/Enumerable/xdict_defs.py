from typing import TypeVar, Generic

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")


class xdict(dict[TKey, TValue], Generic[TKey, TValue]):
    @classmethod
    def x_from(cls, src: dict[TKey, TValue]) -> "xdict[TKey, TValue]":
        """从任意可迭代对象快速创建 xdict"""
        # return cls(src)

        new_dict: xdict[TKey, TValue] = cls()
        for k, v in src.items():
            new_dict[k] = v

        return new_dict

    def x_add(self, key: TKey, value: TValue) -> "xdict[TKey, TValue]":
        self[key] = value
        return self

    def x_try_get(self, key: TKey, default: TValue | None = None) -> TValue | None:
        return self.get(key, default)

    def x_contains_key(self, key: TKey) -> bool:
        return key in self

    def x_remove(self, key: TKey) -> "xdict[TKey, TValue]":
        if key in self:
            del self[key]
        return self

    @property
    def x_keys(self) -> list[TKey]:
        return list(self.keys())

    @property
    def x_values(self) -> list[TValue]:
        return list(self.values())
