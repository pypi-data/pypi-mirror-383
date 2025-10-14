import binascii
import re
from typing import Optional, Pattern
from base64 import b64encode, b64decode


_EMAIL_PATTERN: Pattern[str] = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)

_encoding = "utf-8"


class xstr(str):
    """继承自 str 的扩展类，增加了一些便捷方法"""

    @property
    def x_is_email(self) -> bool:
        # 已测试
        """验证字符串是否为有效的电子邮件地址"""
        return _EMAIL_PATTERN.match(self) is not None

    @property
    def x_reverse(self) -> "xstr":
        # 已测试
        """反转字符串"""
        return xstr(self[::-1])

    @property
    def x_to_base64(self) -> "xstr":
        # 已测试
        """将字符串编码为 Base64"""

        bytes = b64encode(self.encode(_encoding))
        return xstr(bytes.decode(_encoding))

    @property
    def x_from_base64(self) -> "xstr | None":
        # 已测试
        """将 Base64 字符串解码为普通字符串"""
        try:
            bytes = b64decode(self.encode(_encoding))
            return xstr(bytes.decode(_encoding))
        except (binascii.Error, ValueError, UnicodeDecodeError):
            return None

    @property
    def x_is_ipv4(self) -> bool:
        # 已测试
        """验证字符串是否为有效的 IPv4 地址"""
        import ipaddress

        try:
            ipaddress.IPv4Address(self)
            return True
        except ipaddress.AddressValueError:
            return False

    def x_sub_string(self, start: int, length: Optional[int] = None) -> "xstr":
        # 已测试
        """获取子字符串"""
        return (
            xstr(self[start:]) if length is None else xstr(self[start : start + length])
        )


hehe = xstr("abcdeft")
print(hehe.x_is_email)
print(hehe.x_is_ipv4)
print(hehe.x_to_base64)
print(hehe.x_from_base64)
print(hehe.x_sub_string(2))
print(hehe.x_sub_string(2, 3))
print(hehe.x_reverse)
print(hehe)


pass
