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


class MessageActionGiftPremium(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.MessageAction`.

    Details:
        - Layer: ``148``
        - ID: ``ABA0F5C6``

    Parameters:
        currency (``str``):
            N/A

        amount (``int`` ``64-bit``):
            N/A

        months (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["currency", "amount", "months"]

    ID = 0xaba0f5c6
    QUALNAME = "types.MessageActionGiftPremium"

    def __init__(self, *, currency: str, amount: int, months: int) -> None:
        self.currency = currency  # string
        self.amount = amount  # long
        self.months = months  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageActionGiftPremium":
        # No flags
        
        currency = String.read(b)
        
        amount = Long.read(b)
        
        months = Int.read(b)
        
        return MessageActionGiftPremium(currency=currency, amount=amount, months=months)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.currency))
        
        b.write(Long(self.amount))
        
        b.write(Int(self.months))
        
        return b.getvalue()
