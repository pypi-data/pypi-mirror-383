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


class InstallStickerSet(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``C78FE460``

    Parameters:
        stickerset (:obj:`InputStickerSet <geezlibs.raw.base.InputStickerSet>`):
            N/A

        archived (``bool``):
            N/A

    Returns:
        :obj:`messages.StickerSetInstallResult <geezlibs.raw.base.messages.StickerSetInstallResult>`
    """

    __slots__: List[str] = ["stickerset", "archived"]

    ID = 0xc78fe460
    QUALNAME = "functions.messages.InstallStickerSet"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", archived: bool) -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.archived = archived  # Bool

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InstallStickerSet":
        # No flags
        
        stickerset = TLObject.read(b)
        
        archived = Bool.read(b)
        
        return InstallStickerSet(stickerset=stickerset, archived=archived)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.stickerset.write())
        
        b.write(Bool(self.archived))
        
        return b.getvalue()
