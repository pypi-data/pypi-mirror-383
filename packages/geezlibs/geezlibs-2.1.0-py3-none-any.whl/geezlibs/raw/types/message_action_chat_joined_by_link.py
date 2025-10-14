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


class MessageActionChatJoinedByLink(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.MessageAction`.

    Details:
        - Layer: ``148``
        - ID: ``31224C3``

    Parameters:
        inviter_id (``int`` ``64-bit``):
            N/A

    """

    __slots__: List[str] = ["inviter_id"]

    ID = 0x31224c3
    QUALNAME = "types.MessageActionChatJoinedByLink"

    def __init__(self, *, inviter_id: int) -> None:
        self.inviter_id = inviter_id  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageActionChatJoinedByLink":
        # No flags
        
        inviter_id = Long.read(b)
        
        return MessageActionChatJoinedByLink(inviter_id=inviter_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.inviter_id))
        
        return b.getvalue()
