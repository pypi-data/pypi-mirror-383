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


class GetStrings(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``EFEA3803``

    Parameters:
        lang_pack (``str``):
            N/A

        lang_code (``str``):
            N/A

        keys (List of ``str``):
            N/A

    Returns:
        List of :obj:`LangPackString <geezlibs.raw.base.LangPackString>`
    """

    __slots__: List[str] = ["lang_pack", "lang_code", "keys"]

    ID = 0xefea3803
    QUALNAME = "functions.langpack.GetStrings"

    def __init__(self, *, lang_pack: str, lang_code: str, keys: List[str]) -> None:
        self.lang_pack = lang_pack  # string
        self.lang_code = lang_code  # string
        self.keys = keys  # Vector<string>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetStrings":
        # No flags
        
        lang_pack = String.read(b)
        
        lang_code = String.read(b)
        
        keys = TLObject.read(b, String)
        
        return GetStrings(lang_pack=lang_pack, lang_code=lang_code, keys=keys)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.lang_pack))
        
        b.write(String(self.lang_code))
        
        b.write(Vector(self.keys, String))
        
        return b.getvalue()
