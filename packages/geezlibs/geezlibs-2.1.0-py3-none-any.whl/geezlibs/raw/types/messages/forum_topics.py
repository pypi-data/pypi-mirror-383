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


class ForumTopics(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.messages.ForumTopics`.

    Details:
        - Layer: ``148``
        - ID: ``367617D3``

    Parameters:
        count (``int`` ``32-bit``):
            N/A

        topics (List of :obj:`ForumTopic <geezlibs.raw.base.ForumTopic>`):
            N/A

        messages (List of :obj:`Message <geezlibs.raw.base.Message>`):
            N/A

        chats (List of :obj:`Chat <geezlibs.raw.base.Chat>`):
            N/A

        users (List of :obj:`User <geezlibs.raw.base.User>`):
            N/A

        pts (``int`` ``32-bit``):
            N/A

        order_by_create_date (``bool``, *optional*):
            N/A

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            channels.GetForumTopics
            channels.GetForumTopicsByID
    """

    __slots__: List[str] = ["count", "topics", "messages", "chats", "users", "pts", "order_by_create_date"]

    ID = 0x367617d3
    QUALNAME = "types.messages.ForumTopics"

    def __init__(self, *, count: int, topics: List["raw.base.ForumTopic"], messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"], pts: int, order_by_create_date: Optional[bool] = None) -> None:
        self.count = count  # int
        self.topics = topics  # Vector<ForumTopic>
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.pts = pts  # int
        self.order_by_create_date = order_by_create_date  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ForumTopics":
        
        flags = Int.read(b)
        
        order_by_create_date = True if flags & (1 << 0) else False
        count = Int.read(b)
        
        topics = TLObject.read(b)
        
        messages = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        pts = Int.read(b)
        
        return ForumTopics(count=count, topics=topics, messages=messages, chats=chats, users=users, pts=pts, order_by_create_date=order_by_create_date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.order_by_create_date else 0
        b.write(Int(flags))
        
        b.write(Int(self.count))
        
        b.write(Vector(self.topics))
        
        b.write(Vector(self.messages))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        b.write(Int(self.pts))
        
        return b.getvalue()
