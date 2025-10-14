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


class LeaveGroupCall(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``500377F9``

    Parameters:
        call (:obj:`InputGroupCall <geezlibs.raw.base.InputGroupCall>`):
            N/A

        source (``int`` ``32-bit``):
            N/A

    Returns:
        :obj:`Updates <geezlibs.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "source"]

    ID = 0x500377f9
    QUALNAME = "functions.phone.LeaveGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall", source: int) -> None:
        self.call = call  # InputGroupCall
        self.source = source  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "LeaveGroupCall":
        # No flags
        
        call = TLObject.read(b)
        
        source = Int.read(b)
        
        return LeaveGroupCall(call=call, source=source)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.call.write())
        
        b.write(Int(self.source))
        
        return b.getvalue()
