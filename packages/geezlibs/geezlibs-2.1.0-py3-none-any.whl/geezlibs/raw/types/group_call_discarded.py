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


class GroupCallDiscarded(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.GroupCall`.

    Details:
        - Layer: ``148``
        - ID: ``7780BCB4``

    Parameters:
        id (``int`` ``64-bit``):
            N/A

        access_hash (``int`` ``64-bit``):
            N/A

        duration (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["id", "access_hash", "duration"]

    ID = 0x7780bcb4
    QUALNAME = "types.GroupCallDiscarded"

    def __init__(self, *, id: int, access_hash: int, duration: int) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.duration = duration  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GroupCallDiscarded":
        # No flags
        
        id = Long.read(b)
        
        access_hash = Long.read(b)
        
        duration = Int.read(b)
        
        return GroupCallDiscarded(id=id, access_hash=access_hash, duration=duration)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.id))
        
        b.write(Long(self.access_hash))
        
        b.write(Int(self.duration))
        
        return b.getvalue()
