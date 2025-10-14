from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
    runtime_checkable,
)
from numbers import Number  # 用于约束 TOut 为数字类型


@runtime_checkable
# 【闻祖东 2025-10-12 163221】SupportsLessThan也好，SupportsRichComparison也好，都是需要现自己手动来定义的并非什么库预先定义的
class SupportsLessThan(Protocol):
    def __lt__(self, other: object) -> bool: ...


# 【闻祖东 2025-10-11 193832】推迟到运行时再检查，这样mypy就不会报错(本身python作为弱类型，运行时候本就不会报错)。
@runtime_checkable
class SupportsRichComparison(Protocol):
    def __lt__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...
    def __le__(self, other: Any) -> bool: ...
    def __ge__(self, other: Any) -> bool: ...


T = TypeVar("T")
TOut = TypeVar("TOut")

# 【闻祖东 2025-10-11 193729】Protocal是推荐的做法，而Union虽然也可以实现，但是是比较老的做法。
TCompare = TypeVar("TCompare", bound=SupportsRichComparison)
TNumUnn = TypeVar("TNumUnn", bound=Union[int, float])
TNumber = TypeVar("TNumber", bound=Number)
TNum = TypeVar("TNum", int, float, complex)


class xlist(list[T]):
    @classmethod
    def x_from[T](cls, lst: Iterable[T]) -> "xlist[T]":
        """从任意可迭代对象快速创建 xlist"""
        return cls(lst)

    def x_true_4_all(self, predicate: Callable[[T], bool]) -> bool:
        # 已测试
        return all(predicate(x) for x in self)

    def x_add(self, item: T) -> "xlist[T]":
        # 已测试
        self.append(item)
        return self

    def x_remove_at(self, index: int) -> "xlist[T]":
        # 已测试
        del self[
            index
        ]  # 【闻祖东 2023-07-26 102651】其实 self.__items.pop(index) 也可以
        return self

    def x_remove(self, item: T) -> "xlist[T]":
        # 已测试
        self.remove(item)
        return self

    def x_exists(self, predicate: Callable[[T], bool]) -> bool:
        # 已测试
        return any(predicate(x) for x in self)

    def x_count(self, predicate: Callable[[T], bool] | None = None) -> int:
        # 已测试
        if predicate == None:
            return len(self)
        else:
            return len(self.x_find_all(predicate))

    def x_find_all(self, predicate: Callable[[T], bool]) -> "xlist[T]":
        """【闻祖东 2025-10-11 155802】调用时形如：nums_ex.x_find_all(lambda a: a > 2)"""
        # 已测试
        return xlist([x for x in self if predicate(x)])

    def x_first(self, predicate: Callable[[T], bool]) -> "T | None":
        # 已测试
        items = self.x_find_all(predicate)
        return items[0] if items else None

    def x_last(self, predicate: Callable[[T], bool]) -> "T | None":
        # 已测试
        items = self.x_find_all(predicate)
        return items[-1] if items else None

    def x_first_index(self, predicate: Callable[[T], bool]) -> int | None:
        # 已测试
        for i in range(0, len(self) - 1, 1):
            if predicate(self[i]):
                return i

        return None

    def x_last_index(self, predicate: Callable[[T], bool]) -> int | None:
        # 已测试
        for i in range(len(self) - 1, -1, -1):
            if predicate(self[i]):
                return i

        return None

    def x_to_list(self) -> "xlist[T]":
        # 已测试
        return xlist(self)

    def x_map(self, predicate: Callable[[T], TOut]) -> "xlist[TOut]":
        # 已测试
        return xlist([predicate(item) for item in self])

    def x_insert(self, index: int, item: T) -> "xlist[T]":
        # 已测试
        self.insert(index, item)
        return self

    def x_each(self, predicate: Callable[[T], None]) -> None:
        # 已测试
        for x in self:
            predicate(x)

    def x_find_all_indexes(self, predicate: Callable[[T], bool]) -> "xlist[int]":
        # 已测试
        indexes = xlist[int]()
        index = 0
        for x in self:
            if predicate(x):
                indexes.x_add(index)
            index += 1

        return indexes

    def x_max_old(self, predicate: Callable[[T], TNumUnn]) -> Optional[TNumUnn]:
        # 已测试
        return max((predicate(item) for item in self), default=None)

    def x_max(self, predicate: Callable[[T], TCompare]) -> Optional[TCompare]:
        # 已测试
        return max((predicate(item) for item in self), default=None)

    def x_min(self, predicate: Callable[[T], TCompare]) -> Optional[TCompare]:
        # 已测试
        return min((predicate(item) for item in self), default=None)

    def x_sort(self, predicate: Callable[[T], TCompare]) -> "xlist[T]":
        # 已测试
        return xlist(sorted(self, key=predicate))

    def x_sort_desc(self, predicate: Callable[[T], TCompare]) -> "xlist[T]":
        # 已测试
        return xlist(sorted(self, key=predicate, reverse=True))

    def x_sum(self, predicate: Callable[[T], TNum]) -> TNum:
        # 已测试
        return sum(predicate(x) for x in self)

    def x_avg(self, predicate: Callable[[T], TNum]) -> float:
        # 已测试
        if len(self) == 0:
            return 0
        else:
            return cast(float, sum(predicate(x) for x in self)) / len(self)

    def x_distinct_by(self, key_selector: Callable[[T], TOut]) -> "xlist[T]":
        # 已测试
        keys: set[TOut] = set()
        lst = xlist[T]()
        for x in self:
            key = key_selector(x)
            if key not in keys:
                keys.add(key)
                lst.append(x)

        return lst

    def x_skip(self, count: int) -> "xlist[T]":
        # 已测试
        # return self[count:] 【闻祖东 2025-10-13 114650】返回的就还是list而不是xlist
        return xlist(self[count:])

    def x_take(self, count: int) -> "xlist[T]":
        # 已测试
        return xlist(self[:count])

    def x_join(self, sep: str) -> str:
        # 已测试
        return sep.join(str(x) for x in self)

    def x_partition(self, size: int) -> "xlist[xlist[T]]":
        # 已测试
        """将列表分割成多个指定大小的子列表"""
        if size <= 0:
            raise ValueError("Size must be greater than 0")

        return xlist(xlist(self[i : i + size]) for i in range(0, len(self), size))

    def x_devide(self, count: int) -> "xlist[xlist[T]]":
        # 已测试
        """将列表分割成指定数量的子列表"""
        if count <= 0:
            raise ValueError("Count must be greater than 0")

        size = (len(self) + count - 1) // count  # 向上取整计算每个子列表的大小
        return self.x_partition(size)

    # return sum(nums)
    # return sum(predicate(x) for x in self)
    # return min((predicate(item) for item in self), default=None)


nums = xlist.x_from([1, 4, 2, 3, 3, 4, 5, 6, 2])

hehe = nums.x_devide(2)
hihi = nums.x_partition(2)

sorted_nums = nums.x_sort(lambda x: x)
sorted_nums_desc = nums.x_sort_desc(lambda x: x)
sums = nums.x_sum(lambda x: x)


class Student:
    def __init__(self, id: int, age: float):
        self.id = id
        self.age = age
        pass


stus = nums.x_map(lambda x: Student(x, x * 3))
stus_sorted = stus.x_sort(lambda x: x.age)
stus_sorted_desc = stus.x_sort_desc(lambda x: x.age)

age_sum = stus.x_sum(lambda x: x.age)
age_avg = stus.x_avg(lambda x: x.age)
dstinct_stus = stus.x_distinct_by(lambda x: x.age)

hh = stus.x_max(lambda x: x.age)
gg = stus.x_max_old(lambda x: x.age)

# hh = nums.x_find_all(lambda a: a > 2)

haha = list(filter(lambda a: a > 2, nums))
pass
