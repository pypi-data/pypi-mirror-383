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


class AddChatUser(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``F24753E3``

    Parameters:
        chat_id (``int`` ``64-bit``):
            N/A

        user_id (:obj:`InputUser <geezlibs.raw.base.InputUser>`):
            N/A

        fwd_limit (``int`` ``32-bit``):
            N/A

    Returns:
        :obj:`Updates <geezlibs.raw.base.Updates>`
    """

    __slots__: List[str] = ["chat_id", "user_id", "fwd_limit"]

    ID = 0xf24753e3
    QUALNAME = "functions.messages.AddChatUser"

    def __init__(self, *, chat_id: int, user_id: "raw.base.InputUser", fwd_limit: int) -> None:
        self.chat_id = chat_id  # long
        self.user_id = user_id  # InputUser
        self.fwd_limit = fwd_limit  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AddChatUser":
        # No flags
        
        chat_id = Long.read(b)
        
        user_id = TLObject.read(b)
        
        fwd_limit = Int.read(b)
        
        return AddChatUser(chat_id=chat_id, user_id=user_id, fwd_limit=fwd_limit)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.chat_id))
        
        b.write(self.user_id.write())
        
        b.write(Int(self.fwd_limit))
        
        return b.getvalue()
