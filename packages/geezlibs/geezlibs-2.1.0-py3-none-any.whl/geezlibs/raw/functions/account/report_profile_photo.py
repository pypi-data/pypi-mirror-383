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


class ReportProfilePhoto(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``FA8CC6F5``

    Parameters:
        peer (:obj:`InputPeer <geezlibs.raw.base.InputPeer>`):
            N/A

        photo_id (:obj:`InputPhoto <geezlibs.raw.base.InputPhoto>`):
            N/A

        reason (:obj:`ReportReason <geezlibs.raw.base.ReportReason>`):
            N/A

        message (``str``):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "photo_id", "reason", "message"]

    ID = 0xfa8cc6f5
    QUALNAME = "functions.account.ReportProfilePhoto"

    def __init__(self, *, peer: "raw.base.InputPeer", photo_id: "raw.base.InputPhoto", reason: "raw.base.ReportReason", message: str) -> None:
        self.peer = peer  # InputPeer
        self.photo_id = photo_id  # InputPhoto
        self.reason = reason  # ReportReason
        self.message = message  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ReportProfilePhoto":
        # No flags
        
        peer = TLObject.read(b)
        
        photo_id = TLObject.read(b)
        
        reason = TLObject.read(b)
        
        message = String.read(b)
        
        return ReportProfilePhoto(peer=peer, photo_id=photo_id, reason=reason, message=message)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(self.photo_id.write())
        
        b.write(self.reason.write())
        
        b.write(String(self.message))
        
        return b.getvalue()
