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


class InputSecureFileUploaded(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.InputSecureFile`.

    Details:
        - Layer: ``148``
        - ID: ``3334B0F0``

    Parameters:
        id (``int`` ``64-bit``):
            N/A

        parts (``int`` ``32-bit``):
            N/A

        md5_checksum (``str``):
            N/A

        file_hash (``bytes``):
            N/A

        secret (``bytes``):
            N/A

    """

    __slots__: List[str] = ["id", "parts", "md5_checksum", "file_hash", "secret"]

    ID = 0x3334b0f0
    QUALNAME = "types.InputSecureFileUploaded"

    def __init__(self, *, id: int, parts: int, md5_checksum: str, file_hash: bytes, secret: bytes) -> None:
        self.id = id  # long
        self.parts = parts  # int
        self.md5_checksum = md5_checksum  # string
        self.file_hash = file_hash  # bytes
        self.secret = secret  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputSecureFileUploaded":
        # No flags
        
        id = Long.read(b)
        
        parts = Int.read(b)
        
        md5_checksum = String.read(b)
        
        file_hash = Bytes.read(b)
        
        secret = Bytes.read(b)
        
        return InputSecureFileUploaded(id=id, parts=parts, md5_checksum=md5_checksum, file_hash=file_hash, secret=secret)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.id))
        
        b.write(Int(self.parts))
        
        b.write(String(self.md5_checksum))
        
        b.write(Bytes(self.file_hash))
        
        b.write(Bytes(self.secret))
        
        return b.getvalue()
