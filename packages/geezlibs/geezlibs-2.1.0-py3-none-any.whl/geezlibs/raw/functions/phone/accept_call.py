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


class AcceptCall(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``3BD2B4A0``

    Parameters:
        peer (:obj:`InputPhoneCall <geezlibs.raw.base.InputPhoneCall>`):
            N/A

        g_b (``bytes``):
            N/A

        protocol (:obj:`PhoneCallProtocol <geezlibs.raw.base.PhoneCallProtocol>`):
            N/A

    Returns:
        :obj:`phone.PhoneCall <geezlibs.raw.base.phone.PhoneCall>`
    """

    __slots__: List[str] = ["peer", "g_b", "protocol"]

    ID = 0x3bd2b4a0
    QUALNAME = "functions.phone.AcceptCall"

    def __init__(self, *, peer: "raw.base.InputPhoneCall", g_b: bytes, protocol: "raw.base.PhoneCallProtocol") -> None:
        self.peer = peer  # InputPhoneCall
        self.g_b = g_b  # bytes
        self.protocol = protocol  # PhoneCallProtocol

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AcceptCall":
        # No flags
        
        peer = TLObject.read(b)
        
        g_b = Bytes.read(b)
        
        protocol = TLObject.read(b)
        
        return AcceptCall(peer=peer, g_b=g_b, protocol=protocol)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(Bytes(self.g_b))
        
        b.write(self.protocol.write())
        
        return b.getvalue()
