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


class SecureValueHash(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.SecureValueHash`.

    Details:
        - Layer: ``148``
        - ID: ``ED1ECDB0``

    Parameters:
        type (:obj:`SecureValueType <geezlibs.raw.base.SecureValueType>`):
            N/A

        hash (``bytes``):
            N/A

    """

    __slots__: List[str] = ["type", "hash"]

    ID = 0xed1ecdb0
    QUALNAME = "types.SecureValueHash"

    def __init__(self, *, type: "raw.base.SecureValueType", hash: bytes) -> None:
        self.type = type  # SecureValueType
        self.hash = hash  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SecureValueHash":
        # No flags
        
        type = TLObject.read(b)
        
        hash = Bytes.read(b)
        
        return SecureValueHash(type=type, hash=hash)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.type.write())
        
        b.write(Bytes(self.hash))
        
        return b.getvalue()
