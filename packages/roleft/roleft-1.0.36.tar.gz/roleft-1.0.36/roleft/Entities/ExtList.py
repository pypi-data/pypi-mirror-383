import ctypes
from typing import Any


def first(self: list) -> Any | None:
    return self[0] if self else None


def last(self: list) -> Any | None:
    return self[-1] if self else None


ctypes.pythonapi.PyObject_SetAttrString(
    ctypes.py_object(list), b"first", ctypes.py_object(first)
)

ctypes.pythonapi.PyObject_SetAttrString(
    ctypes.py_object(list), b"last", ctypes.py_object(last)
)

nums = [10, 20, 30]
# print(nums.first())  # 10
# print(nums.last())  # 30
