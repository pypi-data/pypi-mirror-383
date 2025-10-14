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


class MsgsStateInfo(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.MsgsStateInfo`.

    Details:
        - Layer: ``148``
        - ID: ``04DEB57D``

    Parameters:
        req_msg_id (``int`` ``64-bit``):
            N/A

        info (``str``):
            N/A

    """

    __slots__: List[str] = ["req_msg_id", "info"]

    ID = 0x04deb57d
    QUALNAME = "types.MsgsStateInfo"

    def __init__(self, *, req_msg_id: int, info: str) -> None:
        self.req_msg_id = req_msg_id  # long
        self.info = info  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MsgsStateInfo":
        # No flags
        
        req_msg_id = Long.read(b)
        
        info = String.read(b)
        
        return MsgsStateInfo(req_msg_id=req_msg_id, info=info)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.req_msg_id))
        
        b.write(String(self.info))
        
        return b.getvalue()
