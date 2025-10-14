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


class GetStickers(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``D5A5D3A1``

    Parameters:
        emoticon (``str``):
            N/A

        hash (``int`` ``64-bit``):
            N/A

    Returns:
        :obj:`messages.Stickers <geezlibs.raw.base.messages.Stickers>`
    """

    __slots__: List[str] = ["emoticon", "hash"]

    ID = 0xd5a5d3a1
    QUALNAME = "functions.messages.GetStickers"

    def __init__(self, *, emoticon: str, hash: int) -> None:
        self.emoticon = emoticon  # string
        self.hash = hash  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetStickers":
        # No flags
        
        emoticon = String.read(b)
        
        hash = Long.read(b)
        
        return GetStickers(emoticon=emoticon, hash=hash)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.emoticon))
        
        b.write(Long(self.hash))
        
        return b.getvalue()
