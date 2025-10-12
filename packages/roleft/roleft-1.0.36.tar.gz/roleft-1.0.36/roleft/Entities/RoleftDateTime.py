from datetime import datetime


class xDateTime:
    def __init__(self, tm: datetime = datetime.now()) -> None:
        self.Time = tm
        self.Standard = self.Time.strftime("%Y-%m-%d %H:%M:%S")
        self.StandardYMD = self.Time.strftime("%Y-%m-%d")
        self.StandardHMS = self.Time.strftime("%H:%M:%S")
        self.Timestamp10 = int(self.Time.timestamp())
        self.Timestamp13 = int(self.Time.timestamp() * 1000)
        self.StandardCN = self.Time.strftime("%Y年%m月%d日 %H时%M分%S秒")
        self.StandardCN_YMD = self.Time.strftime("%Y年%m月%d日")
        self.StandardCN_HMS = self.Time.strftime("%H时%M分%S秒")
        pass
