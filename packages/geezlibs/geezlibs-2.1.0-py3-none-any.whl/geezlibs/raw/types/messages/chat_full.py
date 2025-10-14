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


class ChatFull(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.messages.ChatFull`.

    Details:
        - Layer: ``148``
        - ID: ``E5D7D19C``

    Parameters:
        full_chat (:obj:`ChatFull <geezlibs.raw.base.ChatFull>`):
            N/A

        chats (List of :obj:`Chat <geezlibs.raw.base.Chat>`):
            N/A

        users (List of :obj:`User <geezlibs.raw.base.User>`):
            N/A

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetFullChat
            channels.GetFullChannel
    """

    __slots__: List[str] = ["full_chat", "chats", "users"]

    ID = 0xe5d7d19c
    QUALNAME = "types.messages.ChatFull"

    def __init__(self, *, full_chat: "raw.base.ChatFull", chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.full_chat = full_chat  # ChatFull
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChatFull":
        # No flags
        
        full_chat = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return ChatFull(full_chat=full_chat, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.full_chat.write())
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
