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


class GetEmojiKeywordsLanguages(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``4E9963B2``

    Parameters:
        lang_codes (List of ``str``):
            N/A

    Returns:
        List of :obj:`EmojiLanguage <geezlibs.raw.base.EmojiLanguage>`
    """

    __slots__: List[str] = ["lang_codes"]

    ID = 0x4e9963b2
    QUALNAME = "functions.messages.GetEmojiKeywordsLanguages"

    def __init__(self, *, lang_codes: List[str]) -> None:
        self.lang_codes = lang_codes  # Vector<string>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetEmojiKeywordsLanguages":
        # No flags
        
        lang_codes = TLObject.read(b, String)
        
        return GetEmojiKeywordsLanguages(lang_codes=lang_codes)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.lang_codes, String))
        
        return b.getvalue()
