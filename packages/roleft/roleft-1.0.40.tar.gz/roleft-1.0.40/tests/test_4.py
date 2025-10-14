# from abc import ABC
# from typing import Generic, List, TypeVar

# from Utilities import ListU



# class Student:
#     def __init__(self, id: int, name: str) -> None:
#         self.id = id
#         self.name = name

# stus = list[Student]()

# stus.append(Student(2, 'jack'))
# stus.append(Student(1, 'pony'))
# stus.append(Student(4, 'zaker'))
# stus.append(Student(3, 'abc'))


# class Teacher:
#     def __init__(self, iden: int, addr: str) -> None:
#         self.iden = iden
#         self.addr = addr

# tchs = list[Teacher]()

# tchs.append(Teacher(2, 'jack'))
# tchs.append(Teacher(1, 'pony'))
# tchs.append(Teacher(4, 'zaker'))
# tchs.append(Teacher(3, 'abc'))

# print(tchs.__len__())

# newStus = ListU.First(stus, lambda x: x.id > 3)
# # print(ListU.Select(newStus, ))
# # newTchs = ListU.FindAll(tchs, lambda x: x.iden < 3)
# # print(newTchs)