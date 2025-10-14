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


class SecureValueErrorData(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.SecureValueError`.

    Details:
        - Layer: ``148``
        - ID: ``E8A40BD9``

    Parameters:
        type (:obj:`SecureValueType <geezlibs.raw.base.SecureValueType>`):
            N/A

        data_hash (``bytes``):
            N/A

        field (``str``):
            N/A

        text (``str``):
            N/A

    """

    __slots__: List[str] = ["type", "data_hash", "field", "text"]

    ID = 0xe8a40bd9
    QUALNAME = "types.SecureValueErrorData"

    def __init__(self, *, type: "raw.base.SecureValueType", data_hash: bytes, field: str, text: str) -> None:
        self.type = type  # SecureValueType
        self.data_hash = data_hash  # bytes
        self.field = field  # string
        self.text = text  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SecureValueErrorData":
        # No flags
        
        type = TLObject.read(b)
        
        data_hash = Bytes.read(b)
        
        field = String.read(b)
        
        text = String.read(b)
        
        return SecureValueErrorData(type=type, data_hash=data_hash, field=field, text=text)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.type.write())
        
        b.write(Bytes(self.data_hash))
        
        b.write(String(self.field))
        
        b.write(String(self.text))
        
        return b.getvalue()
