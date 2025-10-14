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


class FoundStickerSets(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.messages.FoundStickerSets`.

    Details:
        - Layer: ``148``
        - ID: ``8AF09DD2``

    Parameters:
        hash (``int`` ``64-bit``):
            N/A

        sets (List of :obj:`StickerSetCovered <geezlibs.raw.base.StickerSetCovered>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            messages.SearchStickerSets
    """

    __slots__: List[str] = ["hash", "sets"]

    ID = 0x8af09dd2
    QUALNAME = "types.messages.FoundStickerSets"

    def __init__(self, *, hash: int, sets: List["raw.base.StickerSetCovered"]) -> None:
        self.hash = hash  # long
        self.sets = sets  # Vector<StickerSetCovered>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "FoundStickerSets":
        # No flags
        
        hash = Long.read(b)
        
        sets = TLObject.read(b)
        
        return FoundStickerSets(hash=hash, sets=sets)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.hash))
        
        b.write(Vector(self.sets))
        
        return b.getvalue()
