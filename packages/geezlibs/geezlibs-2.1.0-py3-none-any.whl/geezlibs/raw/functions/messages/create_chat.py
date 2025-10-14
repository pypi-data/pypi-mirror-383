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


class CreateChat(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``9CB126E``

    Parameters:
        users (List of :obj:`InputUser <geezlibs.raw.base.InputUser>`):
            N/A

        title (``str``):
            N/A

    Returns:
        :obj:`Updates <geezlibs.raw.base.Updates>`
    """

    __slots__: List[str] = ["users", "title"]

    ID = 0x9cb126e
    QUALNAME = "functions.messages.CreateChat"

    def __init__(self, *, users: List["raw.base.InputUser"], title: str) -> None:
        self.users = users  # Vector<InputUser>
        self.title = title  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "CreateChat":
        # No flags
        
        users = TLObject.read(b)
        
        title = String.read(b)
        
        return CreateChat(users=users, title=title)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.users))
        
        b.write(String(self.title))
        
        return b.getvalue()
