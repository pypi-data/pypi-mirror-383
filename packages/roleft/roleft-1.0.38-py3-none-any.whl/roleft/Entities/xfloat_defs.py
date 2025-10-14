from decimal import Decimal
from typing import Type, TypeVar, Union


T = TypeVar("T", bound="xfloat")


class xfloat(float):
    """继承自 float 的扩展类，增加了一些便捷方法"""

    # def __new__(cls: type[T], value: Any = 0) -> T:
    #     return super().__new__(cls, float(value))

    def __new__(cls: Type[T], value: Union[float, int, str, Decimal] = 0.0) -> T:
        """创建 xfloat 实例"""
        return super().__new__(cls, value)

    def x_to_percent(self, decimals: int = 2) -> str:
        # 已测试
        """将浮点数转换为百分比字符串表示，默认保留两位小数"""
        if self == 0:
            return "0"

        value = f"{self * 100:.{decimals}f}"
        return f"{value.rstrip("0").rstrip(".")}%"

    def x_to_percentCN(self, decimals: int = 2) -> str:
        # 已测试
        """将浮点数转换为百分比字符串(中文)表示，默认保留两位小数"""
        if self == 0:
            return "0"

        value = f"{self * 100:.{decimals}f}"
        return f"百分之{value.rstrip("0").rstrip(".")}"

    def x_intro_as_wan(self, decimals: int = 2) -> str:
        """将数字转换为以万为单位的字符串表示，默认保留两位小数"""
        if self == 0:
            return "0"

        wan_value = self / 10000
        value = f"{wan_value:.{decimals}f}"
        return f"{value.rstrip('0').rstrip('.')}万"


hehe = xfloat(4)

print(hehe.x_to_percentCN(3))  # 输出: 400.000%
print(hehe.x_intro_as_wan(3))  # 输出: 0.0004万
pass
