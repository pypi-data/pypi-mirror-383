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


class EditUserInfo(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``66B91B70``

    Parameters:
        user_id (:obj:`InputUser <geezlibs.raw.base.InputUser>`):
            N/A

        message (``str``):
            N/A

        entities (List of :obj:`MessageEntity <geezlibs.raw.base.MessageEntity>`):
            N/A

    Returns:
        :obj:`help.UserInfo <geezlibs.raw.base.help.UserInfo>`
    """

    __slots__: List[str] = ["user_id", "message", "entities"]

    ID = 0x66b91b70
    QUALNAME = "functions.help.EditUserInfo"

    def __init__(self, *, user_id: "raw.base.InputUser", message: str, entities: List["raw.base.MessageEntity"]) -> None:
        self.user_id = user_id  # InputUser
        self.message = message  # string
        self.entities = entities  # Vector<MessageEntity>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "EditUserInfo":
        # No flags
        
        user_id = TLObject.read(b)
        
        message = String.read(b)
        
        entities = TLObject.read(b)
        
        return EditUserInfo(user_id=user_id, message=message, entities=entities)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.user_id.write())
        
        b.write(String(self.message))
        
        b.write(Vector(self.entities))
        
        return b.getvalue()
