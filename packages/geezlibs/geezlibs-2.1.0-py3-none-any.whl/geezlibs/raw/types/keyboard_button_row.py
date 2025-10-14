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


class KeyboardButtonRow(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.KeyboardButtonRow`.

    Details:
        - Layer: ``148``
        - ID: ``77608B83``

    Parameters:
        buttons (List of :obj:`KeyboardButton <geezlibs.raw.base.KeyboardButton>`):
            N/A

    """

    __slots__: List[str] = ["buttons"]

    ID = 0x77608b83
    QUALNAME = "types.KeyboardButtonRow"

    def __init__(self, *, buttons: List["raw.base.KeyboardButton"]) -> None:
        self.buttons = buttons  # Vector<KeyboardButton>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "KeyboardButtonRow":
        # No flags
        
        buttons = TLObject.read(b)
        
        return KeyboardButtonRow(buttons=buttons)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.buttons))
        
        return b.getvalue()
