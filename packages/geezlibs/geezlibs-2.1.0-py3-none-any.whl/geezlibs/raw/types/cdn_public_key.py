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


class CdnPublicKey(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.CdnPublicKey`.

    Details:
        - Layer: ``148``
        - ID: ``C982EABA``

    Parameters:
        dc_id (``int`` ``32-bit``):
            N/A

        public_key (``str``):
            N/A

    """

    __slots__: List[str] = ["dc_id", "public_key"]

    ID = 0xc982eaba
    QUALNAME = "types.CdnPublicKey"

    def __init__(self, *, dc_id: int, public_key: str) -> None:
        self.dc_id = dc_id  # int
        self.public_key = public_key  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "CdnPublicKey":
        # No flags
        
        dc_id = Int.read(b)
        
        public_key = String.read(b)
        
        return CdnPublicKey(dc_id=dc_id, public_key=public_key)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.dc_id))
        
        b.write(String(self.public_key))
        
        return b.getvalue()
