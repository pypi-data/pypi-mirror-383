from datetime import datetime


class xdatetime(datetime):
    """继承自 datetime 的扩展类，增加了一些便捷方法"""

    @classmethod
    def x_from(cls, dt: datetime) -> "xdatetime":
        """从任意可迭代对象快速创建 xdatetime"""
        return cls(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            dt.tzinfo,
        )

    @property
    def x_standard(self) -> str:
        """返回标准格式的字符串表示，格式为 'YYYY-MM-DD HH:MM:SS'"""
        return self.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def x_fmt_YMD(self) -> str:
        """返回年月日格式的字符串表示，格式为 'YYYY-MM-DD'"""
        return self.strftime("%Y-%m-%d")

    @property
    def x_fmt_MD(self) -> str:
        """返回月日格式的字符串表示，格式为 'MM-DD'"""
        return self.strftime("%m-%d")

    @property
    def x_fmt_HMS(self) -> str:
        """返回时分秒格式的字符串表示，格式为 'HH:MM:SS'"""
        return self.strftime("%H:%M:%S")

    @property
    def x_fmt_MS(self) -> str:
        """返回分秒格式的字符串表示，格式为 'MM:SS'"""
        return self.strftime("%M:%S")

    @property
    def x_timestamp10(self) -> int:
        """返回10位时间戳，单位为秒"""
        return int(self.timestamp())

    @property
    def x_timestamp13(self) -> int:
        """返回13位时间戳，单位为毫秒"""
        return int(self.timestamp() * 1000)

    @property
    def x_standardCN(self) -> str:
        """返回中文标准格式的字符串表示，格式为 'YYYY年MM月DD日 HH时MM分SS秒'"""
        return self.strftime("%Y年%m月%d日 %H时%M分%S秒")

    @property
    def x_standardCN_YMD(self) -> str:
        """返回中文年月日格式的字符串表示，格式为 'YYYY年MM月DD日'"""
        return self.strftime("%Y年%m月%d日")

    @property
    def x_standardCN_HMS(self) -> str:
        """返回中文时分秒格式的字符串表示，格式为 'HH时MM分SS秒'"""
        return self.strftime("%H时%M分%S秒")
