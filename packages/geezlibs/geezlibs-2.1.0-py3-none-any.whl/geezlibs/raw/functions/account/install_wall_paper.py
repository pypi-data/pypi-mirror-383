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


class InstallWallPaper(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``FEED5769``

    Parameters:
        wallpaper (:obj:`InputWallPaper <geezlibs.raw.base.InputWallPaper>`):
            N/A

        settings (:obj:`WallPaperSettings <geezlibs.raw.base.WallPaperSettings>`):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["wallpaper", "settings"]

    ID = 0xfeed5769
    QUALNAME = "functions.account.InstallWallPaper"

    def __init__(self, *, wallpaper: "raw.base.InputWallPaper", settings: "raw.base.WallPaperSettings") -> None:
        self.wallpaper = wallpaper  # InputWallPaper
        self.settings = settings  # WallPaperSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InstallWallPaper":
        # No flags
        
        wallpaper = TLObject.read(b)
        
        settings = TLObject.read(b)
        
        return InstallWallPaper(wallpaper=wallpaper, settings=settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.wallpaper.write())
        
        b.write(self.settings.write())
        
        return b.getvalue()
