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


class ServerDHParamsFail(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.ServerDHParams`.

    Details:
        - Layer: ``148``
        - ID: ``79CB045D``

    Parameters:
        nonce (``int`` ``128-bit``):
            N/A

        server_nonce (``int`` ``128-bit``):
            N/A

        new_nonce_hash (``int`` ``128-bit``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            ReqDHParams
    """

    __slots__: List[str] = ["nonce", "server_nonce", "new_nonce_hash"]

    ID = 0x79cb045d
    QUALNAME = "types.ServerDHParamsFail"

    def __init__(self, *, nonce: int, server_nonce: int, new_nonce_hash: int) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.new_nonce_hash = new_nonce_hash  # int128

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ServerDHParamsFail":
        # No flags
        
        nonce = Int128.read(b)
        
        server_nonce = Int128.read(b)
        
        new_nonce_hash = Int128.read(b)
        
        return ServerDHParamsFail(nonce=nonce, server_nonce=server_nonce, new_nonce_hash=new_nonce_hash)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int128(self.nonce))
        
        b.write(Int128(self.server_nonce))
        
        b.write(Int128(self.new_nonce_hash))
        
        return b.getvalue()
