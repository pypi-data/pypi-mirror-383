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


class UpdateChannelMessageForwards(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.Update`.

    Details:
        - Layer: ``148``
        - ID: ``D29A27F4``

    Parameters:
        channel_id (``int`` ``64-bit``):
            N/A

        id (``int`` ``32-bit``):
            N/A

        forwards (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["channel_id", "id", "forwards"]

    ID = 0xd29a27f4
    QUALNAME = "types.UpdateChannelMessageForwards"

    def __init__(self, *, channel_id: int, id: int, forwards: int) -> None:
        self.channel_id = channel_id  # long
        self.id = id  # int
        self.forwards = forwards  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateChannelMessageForwards":
        # No flags
        
        channel_id = Long.read(b)
        
        id = Int.read(b)
        
        forwards = Int.read(b)
        
        return UpdateChannelMessageForwards(channel_id=channel_id, id=id, forwards=forwards)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.channel_id))
        
        b.write(Int(self.id))
        
        b.write(Int(self.forwards))
        
        return b.getvalue()
