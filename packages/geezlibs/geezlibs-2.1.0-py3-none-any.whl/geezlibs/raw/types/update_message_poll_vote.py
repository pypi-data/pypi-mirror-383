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


class UpdateMessagePollVote(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.Update`.

    Details:
        - Layer: ``148``
        - ID: ``106395C9``

    Parameters:
        poll_id (``int`` ``64-bit``):
            N/A

        user_id (``int`` ``64-bit``):
            N/A

        options (List of ``bytes``):
            N/A

        qts (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["poll_id", "user_id", "options", "qts"]

    ID = 0x106395c9
    QUALNAME = "types.UpdateMessagePollVote"

    def __init__(self, *, poll_id: int, user_id: int, options: List[bytes], qts: int) -> None:
        self.poll_id = poll_id  # long
        self.user_id = user_id  # long
        self.options = options  # Vector<bytes>
        self.qts = qts  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateMessagePollVote":
        # No flags
        
        poll_id = Long.read(b)
        
        user_id = Long.read(b)
        
        options = TLObject.read(b, Bytes)
        
        qts = Int.read(b)
        
        return UpdateMessagePollVote(poll_id=poll_id, user_id=user_id, options=options, qts=qts)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.poll_id))
        
        b.write(Long(self.user_id))
        
        b.write(Vector(self.options, Bytes))
        
        b.write(Int(self.qts))
        
        return b.getvalue()
