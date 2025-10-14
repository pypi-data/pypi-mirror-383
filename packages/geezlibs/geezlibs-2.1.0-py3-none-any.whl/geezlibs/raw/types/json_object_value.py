#  GeezLibs - Telegram MTProto API Client Library for Python.
#  Copyright (C) 2022-2023 izzy<https://github.com/hitokizzy>
#
#  This file is part of GeezLibs.
#
#  GeezLibs is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  GeezLibs is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with GeezLibs.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from geezlibs.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from geezlibs.raw.core import TLObject
from geezlibs import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class JsonObjectValue(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.JSONObjectValue`.

    Details:
        - Layer: ``148``
        - ID: ``C0DE1BD9``

    Parameters:
        key (``str``):
            N/A

        value (:obj:`JSONValue <geezlibs.raw.base.JSONValue>`):
            N/A

    """

    __slots__: List[str] = ["key", "value"]

    ID = 0xc0de1bd9
    QUALNAME = "types.JsonObjectValue"

    def __init__(self, *, key: str, value: "raw.base.JSONValue") -> None:
        self.key = key  # string
        self.value = value  # JSONValue

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "JsonObjectValue":
        # No flags
        
        key = String.read(b)
        
        value = TLObject.read(b)
        
        return JsonObjectValue(key=key, value=value)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.key))
        
        b.write(self.value.write())
        
        return b.getvalue()
