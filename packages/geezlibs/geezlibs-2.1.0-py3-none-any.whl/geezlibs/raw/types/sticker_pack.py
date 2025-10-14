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


class StickerPack(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.StickerPack`.

    Details:
        - Layer: ``148``
        - ID: ``12B299D4``

    Parameters:
        emoticon (``str``):
            N/A

        documents (List of ``int`` ``64-bit``):
            N/A

    """

    __slots__: List[str] = ["emoticon", "documents"]

    ID = 0x12b299d4
    QUALNAME = "types.StickerPack"

    def __init__(self, *, emoticon: str, documents: List[int]) -> None:
        self.emoticon = emoticon  # string
        self.documents = documents  # Vector<long>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StickerPack":
        # No flags
        
        emoticon = String.read(b)
        
        documents = TLObject.read(b, Long)
        
        return StickerPack(emoticon=emoticon, documents=documents)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.emoticon))
        
        b.write(Vector(self.documents, Long))
        
        return b.getvalue()
