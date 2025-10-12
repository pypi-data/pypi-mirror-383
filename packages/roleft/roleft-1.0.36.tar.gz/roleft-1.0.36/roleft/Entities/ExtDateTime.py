from datetime import datetime


class xDateTime(datetime):
    # def __init__(self) -> None:

    #     pass

    @property
    def xStandard(self) -> str:
        return self.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def xFmtYMD(self) -> str:
        return self.strftime("%Y-%m-%d")

    @property
    def xFmtMD(self) -> str:
        return self.strftime("%m-%d")

    @property
    def xFmtHMS(self) -> str:
        return self.strftime("%H:%M:%S")

    @property
    def xFmtMS(self) -> str:
        return self.strftime("%M:%S")

    @property
    def xTimestamp10(self) -> int:
        return int(self.timestamp())

    @property
    def xTimestamp13(self) -> int:
        return int(self.timestamp() * 1000)

    @property
    def xStandardCN(self) -> str:
        return self.strftime("%Y年%m月%d日 %H时%M分%S秒")

    @property
    def xStandardCN_YMD(self) -> str:
        return self.strftime("%Y年%m月%d日")

    @property
    def xStandardCN_HMS(self) -> str:
        return self.strftime("%H时%M分%S秒")


if __name__ == "__main__":
    # tt = datetime.now()

    hehe = xDateTime.now()
    ss = hehe.xFmtHMS
    pass
