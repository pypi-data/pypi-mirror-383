import json
from typing import Generic, TypeVar, get_type_hints
import inspect

T = TypeVar('T')

class Address:
    def __init__(self, postCode: str, comment: str) -> None:
        self.postCode = postCode
        self.comment = comment
    
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class Student:
    def __init__(self, id: int, name: str, addr: Address) -> None:
        self.id = id
        self.name = name
        self.addr = addr

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class JU(Generic[T]):
    @classmethod
    def Deserialize(cls, json_str: str):
        # props = inspect.getmembers(obj)
        return None

def TryDes(cls: type, json_str: str):

    return None

stu = Student(2, 'jack', Address('112233', '重庆市九龙坡'))
# print(stu.toJson())
# print(stu.addr.toJson())
jsonstr = stu.toJson()

# newStu = JU[Student].Deserialize(jsonstr)
newStu = TryDes(Student, jsonstr)

props = inspect.getmembers(stu)
for x in props:
    if (x[0].startswith('__')):
        continue
    print(f'{x}, type is {type(x)}')