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


class UpdatePeerBlocked(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.Update`.

    Details:
        - Layer: ``148``
        - ID: ``246A4B22``

    Parameters:
        peer_id (:obj:`Peer <geezlibs.raw.base.Peer>`):
            N/A

        blocked (``bool``):
            N/A

    """

    __slots__: List[str] = ["peer_id", "blocked"]

    ID = 0x246a4b22
    QUALNAME = "types.UpdatePeerBlocked"

    def __init__(self, *, peer_id: "raw.base.Peer", blocked: bool) -> None:
        self.peer_id = peer_id  # Peer
        self.blocked = blocked  # Bool

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdatePeerBlocked":
        # No flags
        
        peer_id = TLObject.read(b)
        
        blocked = Bool.read(b)
        
        return UpdatePeerBlocked(peer_id=peer_id, blocked=blocked)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer_id.write())
        
        b.write(Bool(self.blocked))
        
        return b.getvalue()
