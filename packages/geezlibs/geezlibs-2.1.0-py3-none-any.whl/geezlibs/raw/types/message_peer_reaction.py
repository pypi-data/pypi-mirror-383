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


class MessagePeerReaction(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.MessagePeerReaction`.

    Details:
        - Layer: ``148``
        - ID: ``B156FE9C``

    Parameters:
        peer_id (:obj:`Peer <geezlibs.raw.base.Peer>`):
            N/A

        reaction (:obj:`Reaction <geezlibs.raw.base.Reaction>`):
            N/A

        big (``bool``, *optional*):
            N/A

        unread (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["peer_id", "reaction", "big", "unread"]

    ID = 0xb156fe9c
    QUALNAME = "types.MessagePeerReaction"

    def __init__(self, *, peer_id: "raw.base.Peer", reaction: "raw.base.Reaction", big: Optional[bool] = None, unread: Optional[bool] = None) -> None:
        self.peer_id = peer_id  # Peer
        self.reaction = reaction  # Reaction
        self.big = big  # flags.0?true
        self.unread = unread  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessagePeerReaction":
        
        flags = Int.read(b)
        
        big = True if flags & (1 << 0) else False
        unread = True if flags & (1 << 1) else False
        peer_id = TLObject.read(b)
        
        reaction = TLObject.read(b)
        
        return MessagePeerReaction(peer_id=peer_id, reaction=reaction, big=big, unread=unread)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.big else 0
        flags |= (1 << 1) if self.unread else 0
        b.write(Int(flags))
        
        b.write(self.peer_id.write())
        
        b.write(self.reaction.write())
        
        return b.getvalue()
