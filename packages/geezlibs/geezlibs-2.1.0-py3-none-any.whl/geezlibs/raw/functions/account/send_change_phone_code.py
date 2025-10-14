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


class SendChangePhoneCode(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``82574AE5``

    Parameters:
        phone_number (``str``):
            N/A

        settings (:obj:`CodeSettings <geezlibs.raw.base.CodeSettings>`):
            N/A

    Returns:
        :obj:`auth.SentCode <geezlibs.raw.base.auth.SentCode>`
    """

    __slots__: List[str] = ["phone_number", "settings"]

    ID = 0x82574ae5
    QUALNAME = "functions.account.SendChangePhoneCode"

    def __init__(self, *, phone_number: str, settings: "raw.base.CodeSettings") -> None:
        self.phone_number = phone_number  # string
        self.settings = settings  # CodeSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SendChangePhoneCode":
        # No flags
        
        phone_number = String.read(b)
        
        settings = TLObject.read(b)
        
        return SendChangePhoneCode(phone_number=phone_number, settings=settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.phone_number))
        
        b.write(self.settings.write())
        
        return b.getvalue()
