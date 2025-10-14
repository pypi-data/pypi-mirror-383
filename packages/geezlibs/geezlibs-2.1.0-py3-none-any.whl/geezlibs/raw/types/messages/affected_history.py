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


class AffectedHistory(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.messages.AffectedHistory`.

    Details:
        - Layer: ``148``
        - ID: ``B45C69D1``

    Parameters:
        pts (``int`` ``32-bit``):
            N/A

        pts_count (``int`` ``32-bit``):
            N/A

        offset (``int`` ``32-bit``):
            N/A

    Functions:
        This object can be returned by 6 functions.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            messages.DeleteHistory
            messages.ReadMentions
            messages.UnpinAllMessages
            messages.ReadReactions
            channels.DeleteParticipantHistory
            channels.DeleteTopicHistory
    """

    __slots__: List[str] = ["pts", "pts_count", "offset"]

    ID = 0xb45c69d1
    QUALNAME = "types.messages.AffectedHistory"

    def __init__(self, *, pts: int, pts_count: int, offset: int) -> None:
        self.pts = pts  # int
        self.pts_count = pts_count  # int
        self.offset = offset  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AffectedHistory":
        # No flags
        
        pts = Int.read(b)
        
        pts_count = Int.read(b)
        
        offset = Int.read(b)
        
        return AffectedHistory(pts=pts, pts_count=pts_count, offset=offset)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.pts))
        
        b.write(Int(self.pts_count))
        
        b.write(Int(self.offset))
        
        return b.getvalue()
