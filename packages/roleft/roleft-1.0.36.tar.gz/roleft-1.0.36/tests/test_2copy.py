from abc import ABC
from typing import Generic, List, TypeVar

T = TypeVar('T')

class xList(Generic[T]):
    def __init__(self, list: List[T] = []) -> None:
        self.items: List[T] = list if len(list) > 0 else []


class Student:
    def __init__(self, id: int) -> None:
        self.id = id

stus = xList[Student]()
stus.items.append(Student(2))


class Teacher:
    def __init__(self, addr: str) -> None:
        self.addr = addr

teachers = xList[Teacher]()

print(stus.items.__len__())
print(teachers.items.__len__())

# 以上代码为什么输出打印为 1？ 我并未给teachers 的 items 添加值啊，我希望teachers 的 items 的长度为 0，该如何解决？
# print(stus.items == tchs.items)
# tchs.items.append(Teacher('jack'))
# print(stus.items.__len__())
# print(tchs.items.__len__())