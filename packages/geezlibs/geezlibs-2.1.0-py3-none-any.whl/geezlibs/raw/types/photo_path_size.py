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


class PhotoPathSize(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.PhotoSize`.

    Details:
        - Layer: ``148``
        - ID: ``D8214D41``

    Parameters:
        type (``str``):
            N/A

        bytes (``bytes``):
            N/A

    """

    __slots__: List[str] = ["type", "bytes"]

    ID = 0xd8214d41
    QUALNAME = "types.PhotoPathSize"

    def __init__(self, *, type: str, bytes: bytes) -> None:
        self.type = type  # string
        self.bytes = bytes  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PhotoPathSize":
        # No flags
        
        type = String.read(b)
        
        bytes = Bytes.read(b)
        
        return PhotoPathSize(type=type, bytes=bytes)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.type))
        
        b.write(Bytes(self.bytes))
        
        return b.getvalue()
