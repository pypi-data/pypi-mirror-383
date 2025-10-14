from roleft.Enumerable.RoleftList import xList




class MpnStudent():
    def __init__(self, id=0, name='', age=0) -> None:
        self.Id = id
        self.Name = name
        self.Age = age
        pass
    
stus = xList[MpnStudent]()
stus.Add(MpnStudent(1, 'jack', 54))
stus.Add(MpnStudent(2, 'pony', 47))
stus.Add(MpnStudent(3, '雷军', 35))
stus.Add(MpnStudent(4, '冯仑', 67))
stus.Add(MpnStudent(5, '王大爷', 67))


new = stus.xOrderByAsc(lambda x: x.Age)
pass