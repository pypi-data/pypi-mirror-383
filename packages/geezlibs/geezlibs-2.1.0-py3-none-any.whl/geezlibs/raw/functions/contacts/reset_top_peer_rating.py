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


class ResetTopPeerRating(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``1AE373AC``

    Parameters:
        category (:obj:`TopPeerCategory <geezlibs.raw.base.TopPeerCategory>`):
            N/A

        peer (:obj:`InputPeer <geezlibs.raw.base.InputPeer>`):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["category", "peer"]

    ID = 0x1ae373ac
    QUALNAME = "functions.contacts.ResetTopPeerRating"

    def __init__(self, *, category: "raw.base.TopPeerCategory", peer: "raw.base.InputPeer") -> None:
        self.category = category  # TopPeerCategory
        self.peer = peer  # InputPeer

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ResetTopPeerRating":
        # No flags
        
        category = TLObject.read(b)
        
        peer = TLObject.read(b)
        
        return ResetTopPeerRating(category=category, peer=peer)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.category.write())
        
        b.write(self.peer.write())
        
        return b.getvalue()
