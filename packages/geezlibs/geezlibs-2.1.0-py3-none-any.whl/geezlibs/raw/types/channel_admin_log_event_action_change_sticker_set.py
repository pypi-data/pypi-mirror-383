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


class ChannelAdminLogEventActionChangeStickerSet(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``148``
        - ID: ``B1C3CAA7``

    Parameters:
        prev_stickerset (:obj:`InputStickerSet <geezlibs.raw.base.InputStickerSet>`):
            N/A

        new_stickerset (:obj:`InputStickerSet <geezlibs.raw.base.InputStickerSet>`):
            N/A

    """

    __slots__: List[str] = ["prev_stickerset", "new_stickerset"]

    ID = 0xb1c3caa7
    QUALNAME = "types.ChannelAdminLogEventActionChangeStickerSet"

    def __init__(self, *, prev_stickerset: "raw.base.InputStickerSet", new_stickerset: "raw.base.InputStickerSet") -> None:
        self.prev_stickerset = prev_stickerset  # InputStickerSet
        self.new_stickerset = new_stickerset  # InputStickerSet

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelAdminLogEventActionChangeStickerSet":
        # No flags
        
        prev_stickerset = TLObject.read(b)
        
        new_stickerset = TLObject.read(b)
        
        return ChannelAdminLogEventActionChangeStickerSet(prev_stickerset=prev_stickerset, new_stickerset=new_stickerset)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.prev_stickerset.write())
        
        b.write(self.new_stickerset.write())
        
        return b.getvalue()
