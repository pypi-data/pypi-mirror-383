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


class ReceivedQueue(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``55A5BB66``

    Parameters:
        max_qts (``int`` ``32-bit``):
            N/A

    Returns:
        List of ``int`` ``64-bit``
    """

    __slots__: List[str] = ["max_qts"]

    ID = 0x55a5bb66
    QUALNAME = "functions.messages.ReceivedQueue"

    def __init__(self, *, max_qts: int) -> None:
        self.max_qts = max_qts  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ReceivedQueue":
        # No flags
        
        max_qts = Int.read(b)
        
        return ReceivedQueue(max_qts=max_qts)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.max_qts))
        
        return b.getvalue()
