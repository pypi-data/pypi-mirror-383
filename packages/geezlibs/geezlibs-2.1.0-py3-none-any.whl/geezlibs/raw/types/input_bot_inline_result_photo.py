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


class InputBotInlineResultPhoto(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.InputBotInlineResult`.

    Details:
        - Layer: ``148``
        - ID: ``A8D864A7``

    Parameters:
        id (``str``):
            N/A

        type (``str``):
            N/A

        photo (:obj:`InputPhoto <geezlibs.raw.base.InputPhoto>`):
            N/A

        send_message (:obj:`InputBotInlineMessage <geezlibs.raw.base.InputBotInlineMessage>`):
            N/A

    """

    __slots__: List[str] = ["id", "type", "photo", "send_message"]

    ID = 0xa8d864a7
    QUALNAME = "types.InputBotInlineResultPhoto"

    def __init__(self, *, id: str, type: str, photo: "raw.base.InputPhoto", send_message: "raw.base.InputBotInlineMessage") -> None:
        self.id = id  # string
        self.type = type  # string
        self.photo = photo  # InputPhoto
        self.send_message = send_message  # InputBotInlineMessage

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputBotInlineResultPhoto":
        # No flags
        
        id = String.read(b)
        
        type = String.read(b)
        
        photo = TLObject.read(b)
        
        send_message = TLObject.read(b)
        
        return InputBotInlineResultPhoto(id=id, type=type, photo=photo, send_message=send_message)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.id))
        
        b.write(String(self.type))
        
        b.write(self.photo.write())
        
        b.write(self.send_message.write())
        
        return b.getvalue()
