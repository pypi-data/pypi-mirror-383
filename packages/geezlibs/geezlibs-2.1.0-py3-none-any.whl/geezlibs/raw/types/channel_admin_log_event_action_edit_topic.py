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


class ChannelAdminLogEventActionEditTopic(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``148``
        - ID: ``F06FE208``

    Parameters:
        prev_topic (:obj:`ForumTopic <geezlibs.raw.base.ForumTopic>`):
            N/A

        new_topic (:obj:`ForumTopic <geezlibs.raw.base.ForumTopic>`):
            N/A

    """

    __slots__: List[str] = ["prev_topic", "new_topic"]

    ID = 0xf06fe208
    QUALNAME = "types.ChannelAdminLogEventActionEditTopic"

    def __init__(self, *, prev_topic: "raw.base.ForumTopic", new_topic: "raw.base.ForumTopic") -> None:
        self.prev_topic = prev_topic  # ForumTopic
        self.new_topic = new_topic  # ForumTopic

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelAdminLogEventActionEditTopic":
        # No flags
        
        prev_topic = TLObject.read(b)
        
        new_topic = TLObject.read(b)
        
        return ChannelAdminLogEventActionEditTopic(prev_topic=prev_topic, new_topic=new_topic)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.prev_topic.write())
        
        b.write(self.new_topic.write())
        
        return b.getvalue()
