from datetime import datetime


class xdatetime:

    @staticmethod
    def Standard(tm: datetime = datetime.now()) -> str:
        return tm.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def StandardYMD(tm: datetime = datetime.now()) -> str:
        return tm.strftime("%Y-%m-%d")

    @staticmethod
    def StandardHMS(tm: datetime = datetime.now()) -> str:
        return tm.strftime("%H:%M:%S")

    @staticmethod
    def Timestamp10(tm: datetime = datetime.now()) -> int:
        return int(tm.timestamp())

    @staticmethod
    def Timestamp13(tm: datetime = datetime.now()) -> int:
        return int(tm.timestamp() * 1000)

    @staticmethod
    def StandardCN(tm: datetime = datetime.now()) -> str:
        return tm.strftime("%Y年%m月%d日 %H时%M分%S秒")

    @staticmethod
    def StandardCN_YMD(tm: datetime = datetime.now()) -> str:
        return tm.strftime("%Y年%m月%d日")

    @staticmethod
    def StandardCN_HMS(tm: datetime = datetime.now()) -> str:
        return tm.strftime("%H时%M分%S秒")
