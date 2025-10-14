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


class InputStorePaymentGiftPremium(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.InputStorePaymentPurpose`.

    Details:
        - Layer: ``148``
        - ID: ``616F7FE8``

    Parameters:
        user_id (:obj:`InputUser <geezlibs.raw.base.InputUser>`):
            N/A

        currency (``str``):
            N/A

        amount (``int`` ``64-bit``):
            N/A

    """

    __slots__: List[str] = ["user_id", "currency", "amount"]

    ID = 0x616f7fe8
    QUALNAME = "types.InputStorePaymentGiftPremium"

    def __init__(self, *, user_id: "raw.base.InputUser", currency: str, amount: int) -> None:
        self.user_id = user_id  # InputUser
        self.currency = currency  # string
        self.amount = amount  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputStorePaymentGiftPremium":
        # No flags
        
        user_id = TLObject.read(b)
        
        currency = String.read(b)
        
        amount = Long.read(b)
        
        return InputStorePaymentGiftPremium(user_id=user_id, currency=currency, amount=amount)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.user_id.write())
        
        b.write(String(self.currency))
        
        b.write(Long(self.amount))
        
        return b.getvalue()
