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


class DeleteTopicHistory(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``34435F2D``

    Parameters:
        channel (:obj:`InputChannel <geezlibs.raw.base.InputChannel>`):
            N/A

        top_msg_id (``int`` ``32-bit``):
            N/A

    Returns:
        :obj:`messages.AffectedHistory <geezlibs.raw.base.messages.AffectedHistory>`
    """

    __slots__: List[str] = ["channel", "top_msg_id"]

    ID = 0x34435f2d
    QUALNAME = "functions.channels.DeleteTopicHistory"

    def __init__(self, *, channel: "raw.base.InputChannel", top_msg_id: int) -> None:
        self.channel = channel  # InputChannel
        self.top_msg_id = top_msg_id  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "DeleteTopicHistory":
        # No flags
        
        channel = TLObject.read(b)
        
        top_msg_id = Int.read(b)
        
        return DeleteTopicHistory(channel=channel, top_msg_id=top_msg_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.channel.write())
        
        b.write(Int(self.top_msg_id))
        
        return b.getvalue()
