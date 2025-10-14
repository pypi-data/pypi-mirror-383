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


class UpdateChatParticipantAdmin(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.Update`.

    Details:
        - Layer: ``148``
        - ID: ``D7CA61A2``

    Parameters:
        chat_id (``int`` ``64-bit``):
            N/A

        user_id (``int`` ``64-bit``):
            N/A

        is_admin (``bool``):
            N/A

        version (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["chat_id", "user_id", "is_admin", "version"]

    ID = 0xd7ca61a2
    QUALNAME = "types.UpdateChatParticipantAdmin"

    def __init__(self, *, chat_id: int, user_id: int, is_admin: bool, version: int) -> None:
        self.chat_id = chat_id  # long
        self.user_id = user_id  # long
        self.is_admin = is_admin  # Bool
        self.version = version  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateChatParticipantAdmin":
        # No flags
        
        chat_id = Long.read(b)
        
        user_id = Long.read(b)
        
        is_admin = Bool.read(b)
        
        version = Int.read(b)
        
        return UpdateChatParticipantAdmin(chat_id=chat_id, user_id=user_id, is_admin=is_admin, version=version)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.chat_id))
        
        b.write(Long(self.user_id))
        
        b.write(Bool(self.is_admin))
        
        b.write(Int(self.version))
        
        return b.getvalue()
