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


class GetEmojiKeywords(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``35A0E062``

    Parameters:
        lang_code (``str``):
            N/A

    Returns:
        :obj:`EmojiKeywordsDifference <geezlibs.raw.base.EmojiKeywordsDifference>`
    """

    __slots__: List[str] = ["lang_code"]

    ID = 0x35a0e062
    QUALNAME = "functions.messages.GetEmojiKeywords"

    def __init__(self, *, lang_code: str) -> None:
        self.lang_code = lang_code  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetEmojiKeywords":
        # No flags
        
        lang_code = String.read(b)
        
        return GetEmojiKeywords(lang_code=lang_code)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.lang_code))
        
        return b.getvalue()
