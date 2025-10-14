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


class AllStickers(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.messages.AllStickers`.

    Details:
        - Layer: ``148``
        - ID: ``CDBBCEBB``

    Parameters:
        hash (``int`` ``64-bit``):
            N/A

        sets (List of :obj:`StickerSet <geezlibs.raw.base.StickerSet>`):
            N/A

    Functions:
        This object can be returned by 3 functions.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetAllStickers
            messages.GetMaskStickers
            messages.GetEmojiStickers
    """

    __slots__: List[str] = ["hash", "sets"]

    ID = 0xcdbbcebb
    QUALNAME = "types.messages.AllStickers"

    def __init__(self, *, hash: int, sets: List["raw.base.StickerSet"]) -> None:
        self.hash = hash  # long
        self.sets = sets  # Vector<StickerSet>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AllStickers":
        # No flags
        
        hash = Long.read(b)
        
        sets = TLObject.read(b)
        
        return AllStickers(hash=hash, sets=sets)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.hash))
        
        b.write(Vector(self.sets))
        
        return b.getvalue()
