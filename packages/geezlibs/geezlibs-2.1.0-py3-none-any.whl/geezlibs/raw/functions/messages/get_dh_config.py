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


class GetDhConfig(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``26CF8950``

    Parameters:
        version (``int`` ``32-bit``):
            N/A

        random_length (``int`` ``32-bit``):
            N/A

    Returns:
        :obj:`messages.DhConfig <geezlibs.raw.base.messages.DhConfig>`
    """

    __slots__: List[str] = ["version", "random_length"]

    ID = 0x26cf8950
    QUALNAME = "functions.messages.GetDhConfig"

    def __init__(self, *, version: int, random_length: int) -> None:
        self.version = version  # int
        self.random_length = random_length  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetDhConfig":
        # No flags
        
        version = Int.read(b)
        
        random_length = Int.read(b)
        
        return GetDhConfig(version=version, random_length=random_length)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.version))
        
        b.write(Int(self.random_length))
        
        return b.getvalue()
