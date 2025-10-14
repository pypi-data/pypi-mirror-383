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


class MessageUserVote(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.MessageUserVote`.

    Details:
        - Layer: ``148``
        - ID: ``34D247B4``

    Parameters:
        user_id (``int`` ``64-bit``):
            N/A

        option (``bytes``):
            N/A

        date (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["user_id", "option", "date"]

    ID = 0x34d247b4
    QUALNAME = "types.MessageUserVote"

    def __init__(self, *, user_id: int, option: bytes, date: int) -> None:
        self.user_id = user_id  # long
        self.option = option  # bytes
        self.date = date  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageUserVote":
        # No flags
        
        user_id = Long.read(b)
        
        option = Bytes.read(b)
        
        date = Int.read(b)
        
        return MessageUserVote(user_id=user_id, option=option, date=date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.user_id))
        
        b.write(Bytes(self.option))
        
        b.write(Int(self.date))
        
        return b.getvalue()
