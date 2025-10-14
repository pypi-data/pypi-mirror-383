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


class Stickers(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.messages.Stickers`.

    Details:
        - Layer: ``148``
        - ID: ``30A6EC7E``

    Parameters:
        hash (``int`` ``64-bit``):
            N/A

        stickers (List of :obj:`Document <geezlibs.raw.base.Document>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetStickers
    """

    __slots__: List[str] = ["hash", "stickers"]

    ID = 0x30a6ec7e
    QUALNAME = "types.messages.Stickers"

    def __init__(self, *, hash: int, stickers: List["raw.base.Document"]) -> None:
        self.hash = hash  # long
        self.stickers = stickers  # Vector<Document>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "Stickers":
        # No flags
        
        hash = Long.read(b)
        
        stickers = TLObject.read(b)
        
        return Stickers(hash=hash, stickers=stickers)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.hash))
        
        b.write(Vector(self.stickers))
        
        return b.getvalue()
