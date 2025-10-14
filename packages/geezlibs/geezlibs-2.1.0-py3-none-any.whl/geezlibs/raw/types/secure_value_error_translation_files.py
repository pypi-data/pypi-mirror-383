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


class SecureValueErrorTranslationFiles(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.SecureValueError`.

    Details:
        - Layer: ``148``
        - ID: ``34636DD8``

    Parameters:
        type (:obj:`SecureValueType <geezlibs.raw.base.SecureValueType>`):
            N/A

        file_hash (List of ``bytes``):
            N/A

        text (``str``):
            N/A

    """

    __slots__: List[str] = ["type", "file_hash", "text"]

    ID = 0x34636dd8
    QUALNAME = "types.SecureValueErrorTranslationFiles"

    def __init__(self, *, type: "raw.base.SecureValueType", file_hash: List[bytes], text: str) -> None:
        self.type = type  # SecureValueType
        self.file_hash = file_hash  # Vector<bytes>
        self.text = text  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SecureValueErrorTranslationFiles":
        # No flags
        
        type = TLObject.read(b)
        
        file_hash = TLObject.read(b, Bytes)
        
        text = String.read(b)
        
        return SecureValueErrorTranslationFiles(type=type, file_hash=file_hash, text=text)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.type.write())
        
        b.write(Vector(self.file_hash, Bytes))
        
        b.write(String(self.text))
        
        return b.getvalue()
