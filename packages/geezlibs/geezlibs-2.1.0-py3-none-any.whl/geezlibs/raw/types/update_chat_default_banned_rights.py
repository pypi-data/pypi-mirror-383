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


class UpdateChatDefaultBannedRights(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.Update`.

    Details:
        - Layer: ``148``
        - ID: ``54C01850``

    Parameters:
        peer (:obj:`Peer <geezlibs.raw.base.Peer>`):
            N/A

        default_banned_rights (:obj:`ChatBannedRights <geezlibs.raw.base.ChatBannedRights>`):
            N/A

        version (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["peer", "default_banned_rights", "version"]

    ID = 0x54c01850
    QUALNAME = "types.UpdateChatDefaultBannedRights"

    def __init__(self, *, peer: "raw.base.Peer", default_banned_rights: "raw.base.ChatBannedRights", version: int) -> None:
        self.peer = peer  # Peer
        self.default_banned_rights = default_banned_rights  # ChatBannedRights
        self.version = version  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateChatDefaultBannedRights":
        # No flags
        
        peer = TLObject.read(b)
        
        default_banned_rights = TLObject.read(b)
        
        version = Int.read(b)
        
        return UpdateChatDefaultBannedRights(peer=peer, default_banned_rights=default_banned_rights, version=version)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(self.default_banned_rights.write())
        
        b.write(Int(self.version))
        
        return b.getvalue()
