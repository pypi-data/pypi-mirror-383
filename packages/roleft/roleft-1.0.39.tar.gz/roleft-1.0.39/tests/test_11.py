from typing import Iterable, TypeVar

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


from roleft.Fuck.Student_defs import Student

from Utilities.AU_defs import AU
from Utilities.CU_defs import CU

from roleft import Entities


from roleft.Entities.xstr_defs import xstr
import roleft.Enumerable

print(roleft.Enumerable.__file__)


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
