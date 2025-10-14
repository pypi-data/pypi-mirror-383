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


class SetBotUpdatesStatus(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``EC22CFCD``

    Parameters:
        pending_updates_count (``int`` ``32-bit``):
            N/A

        message (``str``):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["pending_updates_count", "message"]

    ID = 0xec22cfcd
    QUALNAME = "functions.help.SetBotUpdatesStatus"

    def __init__(self, *, pending_updates_count: int, message: str) -> None:
        self.pending_updates_count = pending_updates_count  # int
        self.message = message  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SetBotUpdatesStatus":
        # No flags
        
        pending_updates_count = Int.read(b)
        
        message = String.read(b)
        
        return SetBotUpdatesStatus(pending_updates_count=pending_updates_count, message=message)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.pending_updates_count))
        
        b.write(String(self.message))
        
        return b.getvalue()
