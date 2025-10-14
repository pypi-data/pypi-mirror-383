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


class InputEncryptedChat(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.InputEncryptedChat`.

    Details:
        - Layer: ``148``
        - ID: ``F141B5E1``

    Parameters:
        chat_id (``int`` ``32-bit``):
            N/A

        access_hash (``int`` ``64-bit``):
            N/A

    """

    __slots__: List[str] = ["chat_id", "access_hash"]

    ID = 0xf141b5e1
    QUALNAME = "types.InputEncryptedChat"

    def __init__(self, *, chat_id: int, access_hash: int) -> None:
        self.chat_id = chat_id  # int
        self.access_hash = access_hash  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputEncryptedChat":
        # No flags
        
        chat_id = Int.read(b)
        
        access_hash = Long.read(b)
        
        return InputEncryptedChat(chat_id=chat_id, access_hash=access_hash)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.chat_id))
        
        b.write(Long(self.access_hash))
        
        return b.getvalue()
