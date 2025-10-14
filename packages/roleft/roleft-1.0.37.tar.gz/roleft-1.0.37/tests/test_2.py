from abc import ABC
from typing import Generic, TypeVar
import json

from roleft.Enumerable.RoleftList import xList

# from demjson import


class Student:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

    def intro(self):
        print(f'i am a student and my id is {self.id}')

    def __str__(self) -> str:
        return json.dumps(self.__dict__)

stus = xList[Student]()

# stus.Add(Student(2, 'jack'))
# stus.Add(Student(1, 'pony'))
# stus.Add(Student(4, 'zaker'))
# stus.Add(Student(3, 'abc'))


class Teacher:
    def __init__(self, iden: int, addr: str) -> None:
        self.id = iden
        self.addr = addr
    
    def intro(self):
        print(f'i am a teacher and my iden is {self.id}')

    def __str__(self) -> str:
        # return json.dumps(self.__dict__)
        return str(self.__dict__)

tchs = xList[Teacher]()

print(tchs.Count())
tchs.ForEach(lambda x: x.intro())

tchs.Add(Teacher(2, 'jack'))
tchs.Add(Teacher(1, 'pony'))
tchs.Add(Teacher(4, 'zaker'))
tchs.Add(Teacher(3, 'abc'))


tch_1 = Teacher(2, 'jack')
tch_2 = Teacher(2, 'jack')

print(tch_1)

# someTeachers = tchs.FindAll(lambda x: x.id > 3)
# otherTeachers = tchs.OrderBy(lambda x: x.addr)
