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


class SendReaction(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``D30D78D4``

    Parameters:
        peer (:obj:`InputPeer <geezlibs.raw.base.InputPeer>`):
            N/A

        msg_id (``int`` ``32-bit``):
            N/A

        big (``bool``, *optional*):
            N/A

        add_to_recent (``bool``, *optional*):
            N/A

        reaction (List of :obj:`Reaction <geezlibs.raw.base.Reaction>`, *optional*):
            N/A

    Returns:
        :obj:`Updates <geezlibs.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "msg_id", "big", "add_to_recent", "reaction"]

    ID = 0xd30d78d4
    QUALNAME = "functions.messages.SendReaction"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int, big: Optional[bool] = None, add_to_recent: Optional[bool] = None, reaction: Optional[List["raw.base.Reaction"]] = None) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.big = big  # flags.1?true
        self.add_to_recent = add_to_recent  # flags.2?true
        self.reaction = reaction  # flags.0?Vector<Reaction>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SendReaction":
        
        flags = Int.read(b)
        
        big = True if flags & (1 << 1) else False
        add_to_recent = True if flags & (1 << 2) else False
        peer = TLObject.read(b)
        
        msg_id = Int.read(b)
        
        reaction = TLObject.read(b) if flags & (1 << 0) else []
        
        return SendReaction(peer=peer, msg_id=msg_id, big=big, add_to_recent=add_to_recent, reaction=reaction)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.big else 0
        flags |= (1 << 2) if self.add_to_recent else 0
        flags |= (1 << 0) if self.reaction else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(Int(self.msg_id))
        
        if self.reaction is not None:
            b.write(Vector(self.reaction))
        
        return b.getvalue()
