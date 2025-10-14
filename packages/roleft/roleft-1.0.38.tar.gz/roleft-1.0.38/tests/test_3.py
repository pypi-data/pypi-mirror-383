from abc import ABC
from typing import Generic, List, TypeVar


class Student:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

stus = list[Student]()

stus.append(Student(2, 'jack'))
# stus.Add(Student(1, 'pony'))
# stus.Add(Student(4, 'zaker'))
# stus.Add(Student(3, 'abc'))


class Teacher:
    def __init__(self, iden: int, addr: str) -> None:
        self.iden = iden
        self.addr = addr

tchs = list[Teacher]()

tchs.append(Teacher(2, 'jack'))
# tchs.Add(Teacher(1, 'pony'))
# tchs.Add(Teacher(4, 'zaker'))
# tchs.Add(Teacher(3, 'abc'))

print(tchs.__len__())

# tchs.First(lambda x: x.iden > 3)

# print('jack' == 'abcd')
# dic.Print()


# T = TypeVar("T")

# class Parent(ABC, Generic[T]):
#     def get_impl_t(self):
#         pass

# class Child(Parent[int]):
#     pass