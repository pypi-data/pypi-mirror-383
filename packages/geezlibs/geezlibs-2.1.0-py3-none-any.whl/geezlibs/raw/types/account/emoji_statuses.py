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


class EmojiStatuses(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.account.EmojiStatuses`.

    Details:
        - Layer: ``148``
        - ID: ``90C467D1``

    Parameters:
        hash (``int`` ``64-bit``):
            N/A

        statuses (List of :obj:`EmojiStatus <geezlibs.raw.base.EmojiStatus>`):
            N/A

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            account.GetDefaultEmojiStatuses
            account.GetRecentEmojiStatuses
    """

    __slots__: List[str] = ["hash", "statuses"]

    ID = 0x90c467d1
    QUALNAME = "types.account.EmojiStatuses"

    def __init__(self, *, hash: int, statuses: List["raw.base.EmojiStatus"]) -> None:
        self.hash = hash  # long
        self.statuses = statuses  # Vector<EmojiStatus>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "EmojiStatuses":
        # No flags
        
        hash = Long.read(b)
        
        statuses = TLObject.read(b)
        
        return EmojiStatuses(hash=hash, statuses=statuses)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.hash))
        
        b.write(Vector(self.statuses))
        
        return b.getvalue()
